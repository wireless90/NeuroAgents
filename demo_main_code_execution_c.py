# register_neuroengine.py
from neuroengine_client import NeuroengineClient  # Ensure correct case
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, ConversableAgent
from autogen.coding import LocalCommandLineCodeExecutor
from tempfile import TemporaryDirectory

tempdir :TemporaryDirectory = TemporaryDirectory()
executor :LocalCommandLineCodeExecutor = LocalCommandLineCodeExecutor(
    work_dir= tempdir.name,
    timeout=100 # 100 seconds
)

code_executor_agent :ConversableAgent = UserProxyAgent(
    name="code_executor_agent",
    human_input_mode="NEVER",
    code_execution_config={"executor": executor},
)

# Create the configuration for the AssistantAgent
config_list_custom = config_list_from_json(
    "OAI_CONFIG_LIST.json",
    filter_dict={"model_client_cls": ["NeuroengineClient"]},
)

# Create the AssistantAgent with a name
code_generator_agent = AssistantAgent(
    name="code_generator_agent",
    llm_config={"config_list": config_list_custom},
    system_message="You are an intelligent AI that generates bash programming code as requested."
    "The code you generated will be executed by another agent.",
    # "Once you received its result, print it and terminate by saying TERMINATE."
    is_termination_msg=lambda x: x is not None and x["content"] is not None and "execution succeeded" in x["content"].lower() or "goodbye" in x["content"].lower()
)


# Register the custom model client
code_generator_agent.register_model_client(model_client_cls=NeuroengineClient)


# Example conversation
if __name__ == "__main__":
    prompt :str = "Write a bash script which writes a c code to calculate the 15th Fibonacci number, into a file main.c, compile it with gcc, and execute it."
    code_executor_agent.initiate_chat(code_generator_agent,message=prompt)
