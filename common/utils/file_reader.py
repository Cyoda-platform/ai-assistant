import io
import os
import json
import csv
import xml.etree.ElementTree as ET

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import yaml
except ImportError:
    # Mock yaml for testing or when PyYAML is not available
    class MockYaml:
        @staticmethod
        def safe_load(content):
            return content
        @staticmethod
        def load(content, Loader=None):
            return content
    yaml = MockYaml()

try:
    import fitz
except ImportError:
    # Mock fitz for testing or when PyMuPDF is not available
    class MockFitz:
        class Document:
            def __init__(self, *args, **kwargs):
                pass
            def __iter__(self):
                return iter([])
            def close(self):
                pass
    fitz = MockFitz()

try:
    from bs4 import BeautifulSoup
except ImportError:
    # Mock BeautifulSoup for testing
    class MockBeautifulSoup:
        def __init__(self, *args, **kwargs):
            self.text = ""
    BeautifulSoup = MockBeautifulSoup


def read_file_content(file):
    """
    Reads the contents of an uploaded file based on its extension and returns the content.
    Supports textual formats: .txt, .json, .csv, .pdf, .docx, .drawio, .xml, .html, .yml, .yaml,
    .toml, .ini, .cfg, .conf, .properties, .env, .log, .md, .rst, .tex, .sql, .sh, .bat,
    .ps1, .dockerfile, .gitignore, .gitattributes, .editorconfig, .htaccess, .robots,
    .makefile, .cmake, .gradle, .maven, .sbt, .requirements, .pipfile, .poetry, .cargo,
    and code files: .java, .kt, .py, .js, .ts, .jsx, .tsx, .c, .cpp, .h, .hpp, .cs, .php,
    .rb, .go, .rs, .swift, .scala, .r, .m, .pl, .lua, .dart, .elm, .clj, .hs, .ml, .fs,
    .vb, .pas, .asm, .s, .f90, .f95, .jl, .nim, .zig, .v, .d, .cr, .ex, .exs, .erl, .hrl.

    :param file: A file-like object (e.g. from Quart's request.files) with a .filename attribute.
    :return: The file's contents in an appropriate format.
    """
    ext = os.path.splitext(file.filename)[1].lower()

    # Ensure the file pointer is at the beginning
    file.seek(0)

    if ext == '.txt':
        # Read bytes and decode to a string
        content = file.read()
        return content.decode('utf-8') if isinstance(content, bytes) else content

    elif ext == '.json':
        # Read and decode before parsing JSON
        file.seek(0)
        content = file.read().decode('utf-8')
        return json.loads(content)

    elif ext == '.csv':
        # Read as text then use io.StringIO for csv.reader
        file.seek(0)
        content = file.read().decode('utf-8')
        file_like = io.StringIO(content)
        reader = csv.reader(file_like)
        return "\n".join([", ".join(row) for row in reader])

    elif ext == '.pdf':
        file.seek(0)
        return read_pdf(file)  # Ensure read_pdf handles file-like objects

    elif ext == '.docx':
        file.seek(0)
        return read_docx(file)

    elif ext == '.drawio':
        file.seek(0)
        return read_drawio(file)

    elif ext == '.xml':
        file.seek(0)
        return read_xml(file)

    elif ext == '.html':
        file.seek(0)
        return read_html(file)

    elif ext in {'.yml', '.yaml'}:
        file.seek(0)
        content = file.read().decode('utf-8')
        return yaml.safe_load(content)

    elif ext in {'.toml'}:
        file.seek(0)
        content = file.read().decode('utf-8')
        return read_toml_content(content)

    elif ext in {'.ini', '.cfg', '.conf'}:
        file.seek(0)
        content = file.read().decode('utf-8')
        return read_ini_content(content)

    elif ext in {'.properties'}:
        file.seek(0)
        content = file.read().decode('utf-8')
        return read_properties_content(content)

    elif ext in {'.env'}:
        file.seek(0)
        content = file.read().decode('utf-8')
        return read_env_content(content)

    elif ext in {'.md', '.markdown'}:
        file.seek(0)
        content = file.read().decode('utf-8')
        return content

    elif ext in {'.rst'}:
        file.seek(0)
        content = file.read().decode('utf-8')
        return content

    elif ext in {'.tex', '.latex'}:
        file.seek(0)
        content = file.read().decode('utf-8')
        return content

    elif ext in {'.log'}:
        file.seek(0)
        content = file.read().decode('utf-8')
        return content

    elif ext in {'.sql'}:
        file.seek(0)
        content = file.read().decode('utf-8')
        return content

    elif ext in {'.ps1'}:
        file.seek(0)
        return read_code_file(file)

    elif ext in {'dockerfile', '.dockerfile'}:
        file.seek(0)
        return read_code_file(file)

    elif ext in {'.gitignore', '.gitattributes', '.editorconfig', '.htaccess', '.robots'}:
        file.seek(0)
        content = file.read().decode('utf-8')
        return content

    elif ext in {'makefile', '.makefile', '.mk'}:
        file.seek(0)
        return read_code_file(file)

    elif ext in {'.cmake'}:
        file.seek(0)
        return read_code_file(file)

    elif ext in {'.gradle'}:
        file.seek(0)
        return read_code_file(file)

    elif ext in {'.java', '.kt', '.py', '.js', '.ts', '.jsx', '.tsx', '.c', '.cpp', '.cc', '.cxx',
                 '.h', '.hpp', '.hh', '.hxx', '.cs', '.php', '.rb', '.go', '.rs', '.swift',
                 '.scala', '.r', '.m', '.pl', '.lua', '.dart', '.elm', '.clj', '.cljs', '.cljc',
                 '.hs', '.lhs', '.ml', '.mli', '.fs', '.fsi', '.fsx', '.vb', '.pas', '.pp',
                 '.asm', '.s', '.f90', '.f95', '.f03', '.f08', '.jl', '.nim', '.zig', '.v',
                 '.d', '.cr', '.ex', '.exs', '.erl', '.hrl'}:
        file.seek(0)
        return read_code_file(file)

    else:
        # Try to read as plain text for any other extension
        try:
            file.seek(0)
            content = file.read()
            return content.decode('utf-8') if isinstance(content, bytes) else content
        except Exception:
            raise ValueError(f"Unsupported file extension: {ext}")

def read_file_content_by_file_path(file_path):
    """
    Reads the contents of a file based on its extension and returns the content.
    Supports textual formats: .txt, .json, .csv, .pdf, .docx, .drawio, .xml, .html, .yml, .yaml,
    .toml, .ini, .cfg, .conf, .properties, .env, .log, .md, .rst, .tex, .sql, .sh, .bat,
    .ps1, .dockerfile, .gitignore, .gitattributes, .editorconfig, .htaccess, .robots,
    .makefile, .cmake, .gradle, .maven, .sbt, .requirements, .pipfile, .poetry, .cargo,
    and code files: .java, .kt, .py, .js, .ts, .jsx, .tsx, .c, .cpp, .h, .hpp, .cs, .php,
    .rb, .go, .rs, .swift, .scala, .r, .m, .pl, .lua, .dart, .elm, .clj, .hs, .ml, .fs,
    .vb, .pas, .asm, .s, .f90, .f95, .jl, .nim, .zig, .v, .d, .cr, .ex, .exs, .erl, .hrl.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    elif ext == '.json':
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)  # Assumes file content is a JSON array

    elif ext == '.csv':
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            return "\n".join([", ".join(row) for row in reader])  # Flatten CSV rows into a single string

    elif ext == '.pdf':
        return read_pdf(file_path)

    elif ext == '.docx':
        return read_docx(file_path)

    elif ext == '.drawio':
        return read_drawio(file_path)

    elif ext == '.xml':
        return read_xml(file_path)

    elif ext == '.html':
        return read_html(file_path)

    elif ext in {'.yml', '.yaml'}:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    elif ext in {'.toml'}:
        with open(file_path, 'r', encoding='utf-8') as file:
            return read_toml_content(file.read())

    elif ext in {'.ini', '.cfg', '.conf'}:
        with open(file_path, 'r', encoding='utf-8') as file:
            return read_ini_content(file.read())

    elif ext in {'.properties'}:
        with open(file_path, 'r', encoding='utf-8') as file:
            return read_properties_content(file.read())

    elif ext in {'.env'}:
        with open(file_path, 'r', encoding='utf-8') as file:
            return read_env_content(file.read())

    elif ext in {'.md', '.markdown', '.rst', '.tex', '.latex', '.log', '.sql'}:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    elif ext in {'.gitignore', '.gitattributes', '.editorconfig', '.htaccess', '.robots'}:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    else:
        try:
            return read_code_file(file_path)
        except Exception as e:
            # Try to read as plain text for any other extension
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            except Exception:
                raise ValueError("Unsupported file extension")


def read_pdf(file_input):
    """
    Extracts text from a PDF file using PyMuPDF (fitz).

    Args:
        file_input: Either a file path (str) or a file-like object (BytesIO, etc.)
    """
    if isinstance(file_input, str):
        # File path provided
        document = fitz.open(file_input)
    else:
        # File-like object provided (BytesIO, etc.)
        file_input.seek(0)
        document = fitz.open(stream=file_input.read(), filetype="pdf")

    pdf_text = ""
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        pdf_text += page.get_text("text")  # Extract text as plain text

    document.close()  # Clean up resources
    return pdf_text


def read_drawio(file_input):
    """
    Extracts relevant text from a Draw.io (XML) file.
    This function extracts the XML structure, focusing on shapes' labels.

    Args:
        file_input: Either a file path (str) or a file-like object (BytesIO, etc.)
    """
    if isinstance(file_input, str):
        # File path provided
        with open(file_input, 'r', encoding='utf-8') as file:
            xml_content = file.read()
    else:
        # File-like object provided
        file_input.seek(0)
        xml_content = file_input.read().decode('utf-8')

    # Parse the XML content
    root = ET.fromstring(xml_content)

    # Assuming we are interested in extracting the text from the XML 'mxCell' elements
    drawio_text = ""
    for cell in root.iter('mxCell'):
        # Each 'mxCell' may contain a 'value' attribute that holds the text of the diagram element
        value = cell.get('value')
        if value:
            drawio_text += value + "\n"

    return drawio_text


def read_xml(file_input):
    """
    Reads and extracts text from an XML file.

    Args:
        file_input: Either a file path (str) or a file-like object (BytesIO, etc.)
    """
    if isinstance(file_input, str):
        # File path provided
        with open(file_input, 'r', encoding='utf-8') as file:
            xml_content = file.read()
    else:
        # File-like object provided
        file_input.seek(0)
        xml_content = file_input.read().decode('utf-8')

    # Parse the XML content
    root = ET.fromstring(xml_content)

    # Extract all text from the XML tree (this is just an example, you may want to refine this based on your XML structure)
    xml_text = "\n".join([elem.text for elem in root.iter() if elem.text])  # Collecting text from all elements
    return xml_text


def read_html(file_input):
    """
    Extracts text from an HTML file using BeautifulSoup.

    Args:
        file_input: Either a file path (str) or a file-like object (BytesIO, etc.)
    """
    if isinstance(file_input, str):
        # File path provided
        with open(file_input, 'r', encoding='utf-8') as file:
            html_content = file.read()
    else:
        # File-like object provided
        file_input.seek(0)
        html_content = file_input.read().decode('utf-8')

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract and return all text from the HTML page
    html_text = soup.get_text()
    return html_text


def read_code_file(file_input):
    """
    Reads content of code files like .java, .kt, .py (Plain text).

    Args:
        file_input: Either a file path (str) or a file-like object (BytesIO, etc.)
    """
    if isinstance(file_input, str):
        # File path provided
        with open(file_input, 'r', encoding='utf-8') as file:
            code_content = file.read()
    else:
        # File-like object provided
        file_input.seek(0)
        code_content = file_input.read().decode('utf-8')

    return code_content


def read_docx(file_input):
    """
    Extracts text from a DOCX file using python-docx.

    Args:
        file_input: Either a file path (str) or a file-like object (BytesIO, etc.)
    """
    if Document is None:
        raise ImportError("python-docx library is not available. Install it with: pip install python-docx")

    if isinstance(file_input, str):
        # File path provided
        document = Document(file_input)
    else:
        # File-like object provided
        file_input.seek(0)
        document = Document(file_input)

    # Extract text from all paragraphs
    docx_text = ""
    for paragraph in document.paragraphs:
        docx_text += paragraph.text + "\n"

    # Extract text from tables
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                docx_text += cell.text + "\t"
            docx_text += "\n"

    return docx_text.strip()


def read_toml_content(content):
    """
    Parses TOML content. Falls back to plain text if toml library is not available.
    """
    try:
        import toml
        return toml.loads(content)
    except ImportError:
        # If toml library is not available, return as plain text
        return content
    except Exception:
        # If parsing fails, return as plain text
        return content


def read_ini_content(content):
    """
    Parses INI/CFG configuration files.
    """
    import configparser
    config = configparser.ConfigParser()
    try:
        config.read_string(content)
        # Convert to dictionary format
        result = {}
        for section in config.sections():
            result[section] = dict(config.items(section))
        return result
    except Exception:
        # If parsing fails, return as plain text
        return content


def read_properties_content(content):
    """
    Parses Java-style properties files.
    """
    properties = {}
    try:
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('!'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    properties[key.strip()] = value.strip()
                elif ':' in line:
                    key, value = line.split(':', 1)
                    properties[key.strip()] = value.strip()
        return properties if properties else content
    except Exception:
        return content


def read_env_content(content):
    """
    Parses environment variable files (.env).
    """
    env_vars = {}
    try:
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip().strip('"').strip("'")
                env_vars[key.strip()] = value
        return env_vars if env_vars else content
    except Exception:
        return content
