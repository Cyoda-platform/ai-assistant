"""
Builder System Example

Demonstrates the complete builder-based system with:
- WorkflowBuilder for building workflows
- Config builders (AgentConfig, ToolConfig, MessageConfig, PromptConfig)
- Processor interfaces (AgentProcessor, MessageProcessor, FunctionProcessor)
- get_config() methods on all implementations
"""

from workflow_best_ux.agents.chat_assistant.agent import ChatAssistantAgent
from workflow_best_ux.messages.welcome_message.message import WelcomeMessage
from workflow_best_ux.tools.web_search.tool import WebSearchTool
from workflow_best_ux.tools.read_link.tool import ReadLinkTool
from workflow_best_ux.prompts.assistant_prompt.prompt import AssistantPrompt
from workflow_best_ux.builders import workflow, agent_config, tool_config, message_config, prompt_config


def demonstrate_builder_system():
    """Demonstrate the complete builder-based system"""
    
    print("🏗️ BUILDER-BASED WORKFLOW SYSTEM")
    print("=" * 35)
    
    print("✅ COMPLETE BUILDER SYSTEM:")
    print("  1. 🔄 WorkflowBuilder - builds workflows with fluent API")
    print("  2. 🛠️ Config Builders - AgentConfig, ToolConfig, MessageConfig, PromptConfig")
    print("  3. 📝 Processor Interfaces - AgentProcessor, MessageProcessor, FunctionProcessor")
    print("  4. ⚡ get_config() methods - all implementations provide configuration")
    print("  5. 🔧 Static get_name() methods - consistent naming")
    print()


def show_interface_hierarchy():
    """Show the complete interface hierarchy"""
    
    print("📋 COMPLETE INTERFACE HIERARCHY")
    print("=" * 33)
    
    print("""
    AIConfig (base)
    ├── get_name() -> str
    
    Config Interfaces:
    ├── AgentConfig(AIConfig)
    │   ├── get_tools() -> List[ToolConfig]
    │   └── get_prompts() -> List[PromptConfig]
    ├── ToolConfig(AIConfig)
    │   └── get_parameters() -> Dict[str, Any]
    ├── MessageConfig(AIConfig)
    │   └── get_content() -> str
    └── PromptConfig(AIConfig)
        └── get_content() -> str
    
    Processor Interfaces:
    ├── Processor (base)
    │   └── process(context) -> Dict[str, Any]
    ├── AgentProcessor(Processor)
    │   └── get_config() -> AgentConfig
    ├── MessageProcessor(Processor)
    │   └── get_config() -> MessageConfig
    └── FunctionProcessor(Processor)
        └── get_config() -> ToolConfig
    """)
    
    print("✅ Clean separation of concerns!")
    print()


def demonstrate_config_builders():
    """Demonstrate the config builders"""
    
    print("🔧 CONFIG BUILDERS")
    print("=" * 18)
    
    print("AgentConfig Builder:")
    agent_cfg = (agent_config("test_agent")
                 .with_description("Test AI agent")
                 .with_model("gpt-4", temperature=0.7, max_tokens=4000)
                 .build())
    print(f"  • Name: {agent_cfg.get_name()}")
    print(f"  • Description: {agent_cfg.description}")
    print(f"  • Model: {agent_cfg.model_name}")
    print()
    
    print("ToolConfig Builder:")
    tool_cfg = (tool_config("test_tool")
                .with_description("Test tool")
                .add_parameter("input", "string", "Input parameter", required=True)
                .build())
    print(f"  • Name: {tool_cfg.get_name()}")
    print(f"  • Description: {tool_cfg.description}")
    print(f"  • Parameters: {tool_cfg.get_parameters()}")
    print()
    
    print("MessageConfig Builder:")
    msg_cfg = (message_config("test_message")
               .with_content("Hello, world!")
               .with_type("greeting")
               .build())
    print(f"  • Name: {msg_cfg.get_name()}")
    print(f"  • Content: {msg_cfg.get_content()}")
    print(f"  • Type: {msg_cfg.message_type}")
    print()
    
    print("PromptConfig Builder:")
    prompt_cfg = (prompt_config("test_prompt")
                  .with_content("You are a helpful assistant for {platform_name}")
                  .add_variable("platform_name", "Cyoda")
                  .build())
    print(f"  • Name: {prompt_cfg.get_name()}")
    print(f"  • Content: {prompt_cfg.get_content()}")
    print(f"  • Variables: {prompt_cfg.variables}")
    print()


def demonstrate_processor_configs():
    """Demonstrate get_config() methods on processors"""
    
    print("⚙️ PROCESSOR get_config() METHODS")
    print("=" * 34)
    
    print("ChatAssistantAgent.get_config():")
    agent = ChatAssistantAgent()
    agent_config = agent.get_config()
    print(f"  • Name: {agent_config.get_name()}")
    print(f"  • Description: {agent_config.description}")
    print(f"  • Model: {agent_config.model_name}")
    print(f"  • Tools: {len(agent_config.get_tools())}")
    print(f"  • Prompts: {len(agent_config.get_prompts())}")
    print()
    
    print("WebSearchTool.get_config():")
    tool = WebSearchTool()
    tool_config = tool.get_config()
    print(f"  • Name: {tool_config.get_name()}")
    print(f"  • Description: {tool_config.description}")
    print(f"  • Parameters: {list(tool_config.get_parameters().keys())}")
    print()
    
    print("WelcomeMessage.get_config():")
    message = WelcomeMessage()
    message_config = message.get_config()
    print(f"  • Name: {message_config.get_name()}")
    print(f"  • Content: {message_config.get_content()[:50]}...")
    print(f"  • Type: {message_config.message_type}")
    print()
    
    print("AssistantPrompt.get_config():")
    prompt = AssistantPrompt()
    prompt_config = prompt.get_config()
    print(f"  • Name: {prompt_config.get_name()}")
    print(f"  • Content: {prompt_config.get_content()[:50]}...")
    print(f"  • Variables: {list(prompt_config.variables.keys())}")
    print()


def demonstrate_workflow_builder():
    """Demonstrate the WorkflowBuilder"""
    
    print("🏗️ WORKFLOW BUILDER")
    print("=" * 19)
    
    print("Building workflow with fluent API:")
    workflow_config = (workflow("demo_workflow")
                       .with_description("Demo workflow with builder")
                       .with_initial_state("start")
                       .with_criterion("$.type", "EQUALS", "demo")
                       
                       .add_state("start", "Starting state")
                           .add_transition("begin")
                               .to("processing")
                               .manual(False)
                               .with_processor(f"MessageProcessor.{WelcomeMessage.get_name()}")
                       
                       .add_state("processing", "Processing state")
                           .add_transition("complete")
                               .to("end")
                               .manual(False)
                               .with_processor(f"AgentProcessor.{ChatAssistantAgent.get_name()}")
                       
                       .add_state("end", "End state")
                       
                       .build())
    
    print("✅ Workflow built successfully!")
    print(f"  • Name: {workflow_config['name']}")
    print(f"  • Description: {workflow_config['description']}")
    print(f"  • Initial State: {workflow_config['initial_state']}")
    print(f"  • States: {list(workflow_config['states'].keys())}")
    print(f"  • Criterion: {workflow_config['criterion']['json_path']}")
    print()


def show_navigation_benefits():
    """Show the navigation benefits"""
    
    print("🧭 NAVIGATION BENEFITS")
    print("=" * 22)
    
    print("Complete Ctrl+Click navigation chain:")
    print("  1. Workflow → Component Class")
    print("     • ChatAssistantAgent.get_name() → ChatAssistantAgent class")
    print("     • WelcomeMessage.get_name() → WelcomeMessage class")
    print("     • WebSearchTool.get_name() → WebSearchTool class")
    print()
    
    print("  2. Component Class → get_config() method")
    print("     • agent.get_config() → AgentConfig")
    print("     • tool.get_config() → ToolConfig")
    print("     • message.get_config() → MessageConfig")
    print()
    
    print("  3. Config → Builder → Implementation")
    print("     • AgentConfig → AgentConfigBuilder → agent_config()")
    print("     • ToolConfig → ToolConfigBuilder → tool_config()")
    print("     • MessageConfig → MessageConfigBuilder → message_config()")
    print()
    
    print("✅ Full end-to-end navigation with builders!")
    print()


def show_usage_patterns():
    """Show common usage patterns"""
    
    print("💡 USAGE PATTERNS")
    print("=" * 17)
    
    print("1. Creating configurations:")
    print("""
    # Agent configuration
    config = (agent_config("my_agent")
              .with_description("Custom agent")
              .with_model("gpt-4")
              .build())
    
    # Tool configuration
    config = (tool_config("my_tool")
              .with_description("Custom tool")
              .add_parameter("input", "string", "Input", required=True)
              .build())
    """)
    
    print("2. Building workflows:")
    print("""
    workflow = (workflow("my_workflow")
                .with_description("Custom workflow")
                .add_state("start")
                    .add_transition("process")
                        .to("end")
                        .with_processor(f"AgentProcessor.{MyAgent.get_name()}")
                .build())
    """)
    
    print("3. Using get_config() methods:")
    print("""
    # Get configuration from implementation
    agent = MyAgent()
    config = agent.get_config()
    
    # Access configuration properties
    tools = config.get_tools()
    prompts = config.get_prompts()
    """)
    
    print("✅ Clean, consistent patterns!")
    print()


def run_builder_demo():
    """Run the complete builder system demonstration"""
    
    # Main demonstration
    demonstrate_builder_system()
    
    # Show specific aspects
    show_interface_hierarchy()
    demonstrate_config_builders()
    demonstrate_processor_configs()
    demonstrate_workflow_builder()
    show_navigation_benefits()
    show_usage_patterns()
    
    print("🎉 BUILDER SYSTEM COMPLETE!")
    print("=" * 30)
    print("✅ WorkflowBuilder for building workflows")
    print("✅ Config builders for all component types")
    print("✅ Processor interfaces with get_config() methods")
    print("✅ Complete interface hierarchy")
    print("✅ Full Ctrl+Click navigation support")
    print("✅ Clean, consistent builder patterns")
    print()
    print("🎯 Perfect builder-based workflow system! 🚀")


if __name__ == "__main__":
    run_builder_demo()
