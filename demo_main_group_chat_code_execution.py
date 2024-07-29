from tempfile import TemporaryDirectory
from typing import Any, List, Dict
from autogen import config_list_from_json, UserProxyAgent, ConversableAgent, AssistantAgent, GroupChat, GroupChatManager
from autogen.coding import LocalCommandLineCodeExecutor
from neuroengine_client import NeuroengineClient

# Import configuration
llm_configuration = config_list_from_json("OAI_CONFIG_LIST.json", filter_dict={"model_client_cls": ["NeuroengineClient"]})
llm_configuration = {"config_list": llm_configuration}

CODE_GENERATOR_SYS_MESSAGE = ("You are an intelligent AI that generates python programming code as requested. "
                             "The code you generated will be executed by code_generator_agent.")


CHAT_MANAGER_SYS_MESSAGE = ("1. task_producer_agent will give a task."
                            "2. The task involves code_generator_agent to create python script."
                            "3. Code executor will execute the python code.")

TASK_PRODUCER_SYS_MESSAGE = ("You are an intelligent AI that reiterates a task more clearly.")

CODE_GENERATOR_DESC = "Helps generate python code to solve a task."
CODE_EXECUTOR_DESC = "Executes python code"
TASK_PRODUCER_DESC = "Explains the task."

# Create agents
code_generator_agent = AssistantAgent(name="code_generator_agent", system_message=CODE_GENERATOR_SYS_MESSAGE, llm_config=llm_configuration, description=CODE_GENERATOR_DESC)
task_producer_agent = AssistantAgent(name="task_producer_agent", system_message=TASK_PRODUCER_DESC, llm_config=llm_configuration, description=TASK_PRODUCER_DESC)

tempdir :TemporaryDirectory = TemporaryDirectory()
executor :LocalCommandLineCodeExecutor = LocalCommandLineCodeExecutor(
    work_dir= tempdir.name,
    timeout=100 # 100 seconds
)
code_executor_agent :ConversableAgent = UserProxyAgent(
    name="code_executor_agent",
    human_input_mode="NEVER",
    code_execution_config={"executor": executor},
    description=CODE_EXECUTOR_DESC
)

# Register model client for each agent
for agent in [code_generator_agent, task_producer_agent]:
    agent.register_model_client(model_client_cls=NeuroengineClient)


# Create group chat and group chat manager
group_chat = GroupChat(agents=[code_executor_agent, code_generator_agent, task_producer_agent], messages=[], role_for_select_speaker_messages="user", max_round=100)
group_chat_manager = GroupChatManager(name="group_chat_agent", llm_config=llm_configuration, groupchat=group_chat, system_message=CHAT_MANAGER_SYS_MESSAGE, is_termination_msg=lambda x: x is not None and x["content"] is not None and "terminate" in x["content"].lower() or "execution succeeded" in x["content"].lower())
group_chat_manager.register_model_client(model_client_cls=NeuroengineClient)

# Initiate chat
task_producer_agent.initiate_chat(group_chat_manager, message="I need to know the 12th fibonacci number using python to solve.")
