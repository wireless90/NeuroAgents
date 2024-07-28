from typing import Any, List, Dict
from autogen import config_list_from_json, ConversableAgent, AssistantAgent, GroupChat, GroupChatManager

from neuroengine_client import NeuroengineClient
# Import configuration
llm_configuration = config_list_from_json("OAI_CONFIG_LIST.json", filter_dict={"model_client_cls": ["NeuroengineClient"]})
llm_configuration = {"config_list": llm_configuration}

# System Messages
ADDER_SYS_MESSAGE = "You will be given an integer, You are only allowed to add 1 to the integer to produce a result.Only perform one operation and submit your result. It is ok if you did not reach the target, there are other agents to help you. Tell what u did to produce the result. eg 3 + 1 = 4"
SUBTRACTOR_SYS_MESSAGE = "You will be given an integer, You are only allowed to subtract 1 to the integer to produce a result.Only perform one operation and submit your result. It is ok if you did not reach the target, there are other agents to help you. Tell what u did to produce the result. eg 3 - 1 = 2"
MULTIPLIER_SYS_MESSAGE = "You will be given an integer, You are only allowed to multiply 2 to the integer to produce a result.Only perform one operation and submit your result. It is ok if you did not reach the target, there are other agents to help you. Tell what u did to produce the result. eg 3 * 2 = 6"
DIVIDER_SYS_MESSAGE = "You will be given an integer, You are only allowed to divide it by 2 and round down to nearest integer to produce a result.Only perform one operation and submit your result. It is ok if you did not reach the target, there are other agents to help you. Tell what u did to produce the result.eg 7 / 2 = 3 (Round down)"
MASTER_SYS_MESSAGE = "You will be given a starting number and a target number. Use the other agents to turn the starting number into the target number. "\
                     "Pick the agent that would result in the fastest way to achieve your outcome."\
                     "Do not pick a addition after a substraction or vice versa."\
                     "Also Do not pick a multiplication after a division or vice versa."\
                     "End the groupchat when outcome is achieved. Eg if the outcome is 10, if result is 10, terminate."
NUMBER_SYS_MESSAGE = "Simply return back the number."

# Descriptions
ADDER_DESCRIPTION = "Adds 1 to the latest number in chat."
SUBTRACTOR_DESCRIPTION = "Subtracts 1 from the latest number in chat"
MULTIPLIER_DESCRIPTION = "Multiplies 2 to the latest number in chat"
DIVIDER_DESCRIPTION = "Divides 2 to the latest number in chat and rounds down to nearest integer if there is a decimal."
NUMBER_DESCRIPTION = "Simply returns back the latest given number."

# Create agents
adder_agent = AssistantAgent(name="adder_agent", system_message=ADDER_SYS_MESSAGE, llm_config=llm_configuration, description=ADDER_DESCRIPTION)
subtractor_agent = AssistantAgent(name="subtractor_agent", system_message=SUBTRACTOR_SYS_MESSAGE, llm_config=llm_configuration, description=SUBTRACTOR_DESCRIPTION)
multiplier_agent = AssistantAgent(name="multiplier_agent", system_message=MULTIPLIER_SYS_MESSAGE, llm_config=llm_configuration, description=MULTIPLIER_DESCRIPTION)
divider_agent = AssistantAgent(name="divider_agent", system_message=DIVIDER_SYS_MESSAGE, llm_config=llm_configuration, description=DIVIDER_DESCRIPTION)
number_agent = AssistantAgent(name="number_agent", system_message=NUMBER_SYS_MESSAGE, llm_config=llm_configuration, description=NUMBER_DESCRIPTION)

# Register model client for each agent
for agent in [multiplier_agent, subtractor_agent, adder_agent, divider_agent, number_agent]:
    agent.register_model_client(model_client_cls=NeuroengineClient)

# Create group chat and group chat manager
group_chat = GroupChat(agents=[subtractor_agent, divider_agent, multiplier_agent, number_agent, adder_agent], messages=[], role_for_select_speaker_messages="user", max_round=100)
group_chat_manager = GroupChatManager(name="master_agent", llm_config=llm_configuration, groupchat=group_chat, system_message=MASTER_SYS_MESSAGE, is_termination_msg=lambda x: x is not None and x["content"] is not None and "terminate" in x["content"].lower() or "goodbye" in x["content"].lower())
group_chat_manager.register_model_client(model_client_cls=NeuroengineClient)

# default_agent = AssistantAgent(name="default_agent",  llm_config=llm_configuration)
# default_agent.register_model_client(model_client_cls=NeuroengineClient)
# group_chat_manager.client = default_agent.client

# Initiate chat
v = number_agent.initiate_chat(group_chat_manager, message="My number is 4, my target is 13.", summary_method="reflection_with_llm")
print(v.summary)