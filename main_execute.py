# register_neuroengine.py
from neuroengine_client import NeuroengineClient  # Ensure correct case
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, ConversableAgent
from autogen.coding import LocalCommandLineCodeExecutor
from tempfile import TemporaryDirectory

tempdir :TemporaryDirectory = TemporaryDirectory()
executor :LocalCommandLineCodeExecutor = LocalCommandLineCodeExecutor(
    work_dir=tempdir.name,
    timeout=100 # 100 seconds
)

code_executor_agent :ConversableAgent = UserProxyAgent(
    name="code_executor_agent",
    human_input_mode="NEVER",
    code_execution_config={"executor": executor},
    is_termination_msg=lambda x: x is not None and x["content"] is not None and "terminate" in x["content"].lower() or "goodbye" in x["content"].lower()
)

# code_executor_agent :ConversableAgent = ConversableAgent(
#     name="code_executor_agent",
#     llm_config=False,
#     human_input_mode="NEVER",
#     code_execution_config= {"executor": executor},
#     is_termination_msg=lambda x: x is not None and x["content"] is not None and "terminate" in x["content"].lower() or "goodbye" in x["content"].lower()
# )

# Create the configuration for the AssistantAgent
config_list_custom = config_list_from_json(
    "OAI_CONFIG_LIST.json",
    filter_dict={"model_client_cls": ["NeuroengineClient"]},
)

# Create the AssistantAgent with a name
code_generator_agent = AssistantAgent(
    name="code_generator_agent",
    llm_config={"config_list": config_list_custom},
)


# Register the custom model client
code_generator_agent.register_model_client(model_client_cls=NeuroengineClient)


# Example conversation
if __name__ == "__main__":
    prompt :str = "Write Python code to calculate the 15th Fibonacci number."
    code_executor_agent.initiate_chat(code_generator_agent,message=prompt)

    # Debug: Ensure create method is called
    #print("Initiated chat between assistant and master.")