from neuroengine_client import NeuroengineClient  # Ensure correct case
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, ConversableAgent

tool_executor_agent: ConversableAgent = UserProxyAgent(
    name="tool_executor_agent",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x is not None and x["content"] is not None and "terminate" in x["content"].lower() or "goodbye" in x["content"].lower(),
    code_execution_config=False,
)

# Create the configuration for the AssistantAgent
config_list_custom = config_list_from_json(
    "OAI_CONFIG_LIST.json",
    filter_dict={"model_client_cls": ["NeuroengineClient"]},
)

def greeter(name: str) -> str:
    return f'Hello {name} bitch'
greeter_func_definition = {'description': 'A simple greeting creator given a name', 'name': 'greeter', 'parameters': {'type': 'object', 'properties': {'name': {'type': 'string', 'description': 'name'}}, 'required': ['name']}}

# Create the AssistantAgent with a name
# assistant = AssistantAgent(
#     name="Assistant",
#     llm_config={"config_list": config_list_custom, 'functions': [greeter_func_definition]},
#     system_message="For creation of greetings, only use the functions you have been provided with."
#     "eg. {\"function_call\" :{\"name\": \"greeter\", \"arguments\": \"{\"name\": \"Alice\"}\"}}"
# )

assistant = AssistantAgent(
    name="Assistant",
    llm_config={"config_list": config_list_custom, 'functions': [greeter_func_definition]},
    system_message=(
        "For creation of greetings, only use the functions you have been provided with. eg greeter(name: str)"
        # "Ensure that the \"arguments\" portion is a JSON-like dictionary string. "
        # "Example: {\"function_call\": {\"name\": \"greeter\", \"arguments\": \"{\\\"name\\\": \\\"Alice\\\"}\"}}"
    )
)


assistant.register_for_llm(name="greeter", description="A simple greeting creator", api_style="function")(greeter)
tool_executor_agent.register_for_execution(name="greeter")(greeter)
assistant.register_model_client(model_client_cls=NeuroengineClient)
# Example conversation
if __name__ == "__main__":
    prompt :str = "Bob"
#     r = tool_executor_agent.generate_reply(
#     messages=[{"function_call" :{"name": "greeter", "arguments": '{"name": "Alice"}'}}]
# )
#
# print(r)
    tool_executor_agent.initiate_chat(assistant,message=prompt, clear_history=True)

