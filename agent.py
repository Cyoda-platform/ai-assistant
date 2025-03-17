import logging
import uuid
import re
import math
from openai import OpenAI
from bs4 import BeautifulSoup
import httpx
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Regular expression to parse action lines from the assistant output.
action_re = re.compile(r'^Action: (\w+): (.+)$', re.MULTILINE)




def web_search(query: str) -> str:
    """
    Searches the web using DuckDuckGo's Instant Answer API and returns a summary of the results.

    Example:
        web_search("Python programming")
    """
    try:
        response = httpx.get("https://api.duckduckgo.com/", params={
            "q": query,
            "format": "json",
            "no_redirect": 1,
            "skip_disambig": 1
        })
        response.raise_for_status()
        data = response.json()
        # Prefer the abstract text if available
        if data.get("AbstractText"):
            return data["AbstractText"]
        elif data.get("RelatedTopics"):
            related = data["RelatedTopics"]
            # Sometimes the first result is a dict with a "Text" key, or a group of topics.
            if isinstance(related, list) and related:
                first = related[0]
                if isinstance(first, dict):
                    if "Text" in first:
                        return first["Text"]
                    elif "Topics" in first and first["Topics"]:
                        return first["Topics"][0].get("Text", "No text available.")
        return "No results found."
    except Exception as e:
        return f"Error during web search: {e}"


def read_link(url: str) -> str:
    """
    Fetches the content of the web page at the given URL and extracts its textual content.

    Example:
        read_link("https://example.com")
    """
    try:
        response = httpx.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Try to get the text of all paragraph elements
        paragraphs = soup.find_all("p")
        if paragraphs:
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)
            return content
        # Fallback: return all text
        return soup.get_text(strip=True)
    except Exception as e:
        return f"Error reading link: {e}"


def web_scrape(url: str, selector: str) -> str:
    """
    Scrapes the web page at the given URL using the provided CSS selector and returns the extracted text.

    Example:
        web_scrape("https://example.com", "div.article")
    """
    try:
        response = httpx.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        elements = soup.select(selector)
        if elements:
            content = "\n".join(element.get_text(separator=" ", strip=True) for element in elements)
            return content
        return "No elements found for the given selector."
    except Exception as e:
        return f"Error during web scraping: {e}"

def calculate(expression: str):
    """
    Evaluates a mathematical expression.

    NOTE: Using eval() can be dangerous. In production, consider using a safe evaluation library
    such as 'simpleeval' or 'asteval'.
    """
    try:
        # Create a limited evaluation context
        allowed_names = {"__builtins__": None}
        allowed_names.update({"sqrt": math.sqrt, "pow": math.pow, "abs": abs})
        return eval(expression, allowed_names)
    except Exception as e:
        logger.exception("Error calculating expression: %s", e)
        return "Error evaluating expression."


def wikipedia(query_str: str) -> str:
    """
    Returns a snippet summary from Wikipedia for a given query.
    """
    try:
        response = httpx.get("https://en.wikipedia.org/w/api.php", params={
            "action": "query",
            "list": "search",
            "srsearch": query_str,
            "format": "json"
        })
        response.raise_for_status()
        data = response.json()
        snippet = data["query"]["search"][0]["snippet"]
        return snippet
    except Exception as e:
        logger.exception("Error fetching Wikipedia data: %s", e)
        return "Error retrieving Wikipedia information."


def simon_blog_search(query_str: str) -> str:
    """
    Searches Simon's blog for a given query and returns a summary.
    """
    try:
        sql_query = """
            select
              blog_entry.title || ': ' || substr(html_strip_tags(blog_entry.body), 0, 1000) as text,
              blog_entry.created
            from
              blog_entry join blog_entry_fts on blog_entry.rowid = blog_entry_fts.rowid
            where
              blog_entry_fts match escape_fts(:q)
            order by
              blog_entry_fts.rank
            limit
              1
        """.strip()
        response = httpx.get("https://datasette.simonwillison.net/simonwillisonblog.json", params={
            "sql": sql_query,
            "_shape": "array",
            "q": query_str,
        })
        response.raise_for_status()
        results = response.json()
        return results[0]["text"] if results else "No results found."
    except Exception as e:
        logger.exception("Error fetching Simon blog data: %s", e)
        return "Error retrieving blog information."


# Dictionary mapping action names to functions.
known_actions = {
    "wikipedia": wikipedia,
    "calculate": calculate,
    "simon_blog_search": simon_blog_search,
}


def get_tools_description() -> str:
    """
    Automatically generates a description for each available tool based on its docstring and a usage example.
    """
    descriptions = []
    for name, func in known_actions.items():
        doc = func.__doc__.strip() if func.__doc__ else "No description available."
        # Use the first sentence of the docstring.
        first_sentence = doc.split('.')[0] + "."
        example = ""
        if name == "calculate":
            example = "e.g. calculate: 4 * 7 / 3"
        elif name == "wikipedia":
            example = "e.g. wikipedia: Django"
        elif name == "simon_blog_search":
            example = "e.g. simon_blog_search: Django"
        descriptions.append(f"{name}: {first_sentence} {example}")
    return "\n".join(descriptions)


# Automatically configure the prompt with the tool descriptions.
TOOLS_DESCRIPTION = get_tools_description()

PROMPT = f"""
You are a highly knowledgeable assistant that uses a Thought-Action-PAUSE-Observation loop to solve queries. At the end of the loop, you must output your final answer prefixed with "Answer:".

Instructions:
- Use "Thought:" to describe your reasoning.
- If you already know the answer or can deduce it without additional information, simply output "Answer:" followed by the answer.
- Otherwise, use "Action:" to call one of the available tools (listed below) and then output "PAUSE".
- "Observation:" will be provided based on the result of your action.
- You can perform the loop a limited number of times for a single question.

Your available actions are:
{TOOLS_DESCRIPTION}

Always look things up on Wikipedia if you have the opportunity to do so.

Example session:

Question: What is the capital of France?
Thought: I know that France is a country and its capital is widely known.
Answer: The capital of France is Paris

Example session with action:

Question: What is the result of 4 * 7 / 3?
Thought: I should perform a calculation to determine the result.
Action: calculate: 4 * 7 / 3
PAUSE

You will then be provided with:
Observation: 9.333333333333334

And you output:
Answer: The result of 4 * 7 / 3 is approximately 9.33
""".strip()


class ChatBot:
    """
    A ChatBot that maintains its conversation history in an instance variable.
    """

    def __init__(self, system_prompt: str = ""):
        self.client = OpenAI()  # Initialize your OpenAI client (ensure API keys are configured)
        self.history = []
        self.chat_id = uuid.uuid4()  # One conversation per instance
        # Use provided system prompt or a default one that includes tool descriptions.
        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})
        else:
            self.history.append({
                "role": "system",
                "content": PROMPT
            })

    def chat(self, message: str) -> str:
        """
        Adds the user message to history, calls the API, appends the assistant response, and returns it.
        """
        self.history.append({"role": "user", "content": message})
        result = self._execute()
        self.history.append({"role": "assistant", "content": result})
        return result

    def _execute(self) -> str:
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.history,
                temperature=0.7,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            assistant_response = completion.choices[0].message.content
            logger.info("Assistant response: %s", assistant_response)
            return assistant_response
        except Exception as e:
            logger.exception("Error during completion: %s", e)
            return "Error: Could not get a response from the model."


def query(question: str, max_turns: int = 3) -> None:
    """
    Runs a multi-turn conversation with the ChatBot.
    Limits the number of model invocations for a single question.

    If the assistant directly outputs a final answer (i.e. contains "Answer:"), then no action is executed.
    """
    bot = ChatBot(system_prompt=PROMPT)
    next_prompt = question
    for turn in range(1, max_turns + 1):
        print(f"\n--- Invocation {turn} ---")
        result = bot.chat(next_prompt)
        print("Assistant:", result)

        # If the assistant already returns an answer, we consider that final.
        if "Answer:" in result:
            print("Final Answer:", result)
            return

        # Otherwise, look for an actionable command.
        match = action_re.search(result)
        if match:
            action, action_input = match.groups()
            if action not in known_actions:
                raise Exception(f"Unknown action: {action} with input: {action_input}")
            print(f" -- Running action '{action}' with input: {action_input}")
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = f"Observation: {observation}"
        else:
            # No action found – assume the response is a final answer.
            print("Final Answer:", result)
            return
    # If we exceed max_turns without a final answer:
    print("Max invocation limit reached. Unable to produce a final answer.")


def web_search(query: str) -> str:
    """
    Searches the web using DuckDuckGo's Instant Answer API and returns a summary of the results.

    Example:
        web_search("Python programming")
    """
    try:
        response = httpx.get("https://api.duckduckgo.com/", params={
            "q": query,
            "format": "json",
            "no_redirect": 1,
            "skip_disambig": 1
        })
        response.raise_for_status()
        data = response.json()
        # Prefer the abstract text if available
        if data.get("AbstractText"):
            return data["AbstractText"]
        elif data.get("RelatedTopics"):
            related = data["RelatedTopics"]
            # Sometimes the first result is a dict with a "Text" key, or a group of topics.
            if isinstance(related, list) and related:
                first = related[0]
                if isinstance(first, dict):
                    if "Text" in first:
                        return first["Text"]
                    elif "Topics" in first and first["Topics"]:
                        return first["Topics"][0].get("Text", "No text available.")
        return "No results found."
    except Exception as e:
        return f"Error during web search: {e}"


def read_link(url: str) -> str:
    """
    Fetches the content of the web page at the given URL and extracts its textual content.

    Example:
        read_link("https://example.com")
    """
    try:
        response = httpx.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Try to get the text of all paragraph elements
        paragraphs = soup.find_all("p")
        if paragraphs:
            content = "\n".join(p.get_text(strip=True) for p in paragraphs)
            return content
        # Fallback: return all text
        return soup.get_text(strip=True)
    except Exception as e:
        return f"Error reading link: {e}"


def web_scrape(url: str, selector: str) -> str:
    """
    Scrapes the web page at the given URL using the provided CSS selector and returns the extracted text.

    Example:
        web_scrape("https://example.com", "div.article")
    """
    try:
        response = httpx.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        elements = soup.select(selector)
        if elements:
            content = "\n".join(element.get_text(separator=" ", strip=True) for element in elements)
            return content
        return "No elements found for the given selector."
    except Exception as e:
        return f"Error during web scraping: {e}"

def main():
    query("What is the capital of UK")


if __name__ == "__main__":
    main()
