from typing import Any, List, Dict
from autogen import config_list_from_json, ConversableAgent, AssistantAgent, GroupChat, GroupChatManager

from neuroengine_client import NeuroengineClient
# Import configuration
llm_configuration = config_list_from_json("OAI_CONFIG_LIST.json", filter_dict={"model_client_cls": ["NeuroengineClient"]})
llm_configuration = {"config_list": llm_configuration}

# System Messages
CANDIDATE_SYS_MESSAGE = ("Your name is Cathy and you are meeting Joe for a c programming interview regarding secure coding with c."
                         # "He is a c tech lead. Once he is done chatting, he will tell you GOODBYE, thank him and end the covo, do not continue. Do not tell him goodbye until he tells you that first."
                         #"You are an expert in use after free vulnerability")
                         )
SECOND_CANDIDATE_SYS_MESSAGE = ("Your name is Bob, an experienced programmer and you are meeting Joe for a c programming interview")
                                # "He is a c tech lead. Once he is done chatting, he will tell you GOODBYE, thank him and end the covo,do not continue. Do not tell him goodbye until he tells you that first.")

MASTER_SYS_MESSAGE = "3 AGENTS INVOLVED IN THIS CHAT. cathy_agent and bob_agent are candidates interviewed by joe_agent."
INTERVIEWER_SYS_MESSAGE = ("Your name is Joe and you are a secure coding expert conducting a technical interview in c programming with Cathy and Bob."
                           "You are to give one c programming code example which contains two vulnerabilities."
                           "Assign each of them one vulnerability to solve."
                           "Wait for their responses."
                           "Reply TERMINATE in the end when everything is done.")

# Descriptions
FARZANA_DESCRIPTION = "A candidate named cathy."
JULIA_DESCRIPTION = "A candidate named bob."
INTERVIEWER_DESCRIPTION = "A interviewer named joe"

# Create agents
cathy_agent = AssistantAgent(name="cathy_agent", system_message=CANDIDATE_SYS_MESSAGE, llm_config=llm_configuration, description=FARZANA_DESCRIPTION)
bob_agent = AssistantAgent(name="bob_agent", system_message=SECOND_CANDIDATE_SYS_MESSAGE, llm_config=llm_configuration, description=JULIA_DESCRIPTION)
joe_agent = AssistantAgent(name="joe_agent", system_message=INTERVIEWER_SYS_MESSAGE, llm_config=llm_configuration, description=INTERVIEWER_DESCRIPTION)

# Register model client for each agent
for agent in [bob_agent, cathy_agent, joe_agent]:
    agent.register_model_client(model_client_cls=NeuroengineClient)

# Create group chat and group chat manager
group_chat = GroupChat(agents=[bob_agent, joe_agent, cathy_agent], messages=[], role_for_select_speaker_messages="user", max_round=100)
group_chat_manager = GroupChatManager(name="master_agent", llm_config=llm_configuration, groupchat=group_chat, system_message=MASTER_SYS_MESSAGE, is_termination_msg=lambda x: x is not None and x["content"] is not None and "terminate" in x["content"].lower() or "goodbye" in x["content"].lower())
group_chat_manager.register_model_client(model_client_cls=NeuroengineClient)

# default_agent = AssistantAgent(name="default_agent",  llm_config=llm_configuration)
# default_agent.register_model_client(model_client_cls=NeuroengineClient)
# group_chat_manager.client = default_agent.client

# Initiate chat
v = joe_agent.initiate_chat(group_chat_manager, message="Hi candidate cathy and bob.", summary_method="reflection_with_llm")
print(v.summary)