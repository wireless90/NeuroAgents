from tempfile import TemporaryDirectory
from typing import Any, List, Dict
from autogen import config_list_from_json, UserProxyAgent, ConversableAgent, AssistantAgent, GroupChat, GroupChatManager
from autogen.coding import LocalCommandLineCodeExecutor
from neuroengine_client import NeuroengineClient

# Import configuration
llm_configuration = config_list_from_json("OAI_CONFIG_LIST.json", filter_dict={"model_client_cls": ["NeuroengineClient"]})
llm_configuration = {"config_list": llm_configuration}

CODE_GENERATOR_SYS_MESSAGE = ("You are an intelligent AI that generates sqlmap commands for a given task with bash code blocks. "     
                            #  + "You aim is to get the name of the database through a sql injection."
                             + "The sqlmap command you generate will be executed by code_executor_agent."
                             + "Use the -v 0 option to only generate essential info."
                             + "You can task the code_executor_agent to execute multiple commands, one by one."
                             + "After each reply from him, you are to form the next command until the task is completed or will not be able to succeed."
                             + "Only after all task is completed you will send your final message along with TERMINATE."
                             + "You do not need to inform other agents of your intent to use TERMINATE.")

CODE_GENERATOR_SYS_MESSAGE = """You are an intelligent AI that generates sqlmap commands for a given task with bash code blocks. The sqlmap command you generate will be executed by code_executor_agent. Always use the -v 0 option to generate essential info.You can task the code_executor_agent to execute multiple commands, one by one.After each reply from him, you are to form the next command until the task is completed or will not be able to succeed.The code_executor_agent cannot provide any other feedback or perform any other action beyond executing the code you suggest. The code_executor_agent can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
Reply "TERMINATE" in the end when everything is done.
    """
CHAT_MANAGER_SYS_MESSAGE = ("Agents are to solve a given task.")

TASK_PRODUCER_SYS_MESSAGE = ("You are an intelligent AI that reiterates a task more clearly.")

CODE_GENERATOR_DESC = "Helps generate sqlmap commands to solve a task."
CODE_EXECUTOR_DESC = "Executes sqlmap commands."
TASK_PRODUCER_DESC = "Explains the task."

# Create agents
code_generator_agent = AssistantAgent(name="code_generator_agent", system_message=CODE_GENERATOR_SYS_MESSAGE, llm_config=llm_configuration, description=CODE_GENERATOR_DESC)
task_producer_agent = AssistantAgent(name="task_producer_agent", system_message=TASK_PRODUCER_DESC, llm_config=llm_configuration, description=TASK_PRODUCER_DESC)

tempdir :TemporaryDirectory = TemporaryDirectory()
executor :LocalCommandLineCodeExecutor = LocalCommandLineCodeExecutor(
    work_dir= tempdir.name,
    timeout=600 # 100 seconds
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
group_chat_manager = GroupChatManager(name="group_chat_agent", llm_config=llm_configuration, groupchat=group_chat, system_message=CHAT_MANAGER_SYS_MESSAGE, is_termination_msg=lambda x: x is not None and x["content"] is not None and "terminate" in x["content"].lower())
group_chat_manager.register_model_client(model_client_cls=NeuroengineClient)

task_desc = ("There is a url 'http://localhost/vulnerabilities/sqli/?id=john&Submit=Submit#'."+"Determine if its vulnerable to sqlinjection and try to get the name of the databases, thier tables and thier data."
+"I do have a cookie. 'PHPSESSID=fjqr5n2nuo44ugs3m5d6rvm2i2; security=low'")
# Initiate chat
task_producer_agent.initiate_chat(group_chat_manager, message=task_desc)
