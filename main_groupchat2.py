from typing import Any, List, Dict
from autogen import config_list_from_json, ConversableAgent, AssistantAgent, GroupChat, GroupChatManager

from neuroengine_client import NeuroengineClient
# Import configuration
llm_configuration = config_list_from_json("OAI_CONFIG_LIST.json", filter_dict={"model_client_cls": ["NeuroengineClient"]})
llm_configuration = {"config_list": llm_configuration}

# System Messages
CANDIDATE_SYS_MESSAGE = "YOUR NAME IS FARZANA. YOU ARE ONE OF THE 2 CANDIDATES INTERVIEWING FOR A CHILDCARE POSITION. YOU HAVE A HISTORY OF CHANGING CHILDCARE CENTERS DUE TO PERSONAL REASONS."
SECOND_CANDIDATE_SYS_MESSAGE = "YOUR NAME IS JULIA. YOU ARE ONE OF THE 2 CANDIDATES INTERVIEWING FOR A CHILDCARE POSITION. YOU ARE A FRESH GRADUATE."
MASTER_SYS_MESSAGE = "3 AGENTS INVOLVED IN THIS CHAT. farzana_agent and julia_agent are candidates interviewed by razali_agent."
INTERVIEWER_SYS_MESSAGE = "INTERVIEW CANDIDATES FARZANA AND JULIA and select a suitable one candidate for the job. After that say goodbye to terminate."

# Descriptions
FARZANA_DESCRIPTION = "A candidate named farzana, farzana_agent, with a history of switching jobs."
JULIA_DESCRIPTION = "A candidate named julia, julia_agent, who is a fresh grad."
INTERVIEWER_DESCRIPTION = "A interviewer for a job at a preschool childcare position.."

# Create agents
farzana_agent = AssistantAgent(name="farzana_agent", system_message=CANDIDATE_SYS_MESSAGE, llm_config=llm_configuration, description=FARZANA_DESCRIPTION)
julia_agent = AssistantAgent(name="julia_agent", system_message=SECOND_CANDIDATE_SYS_MESSAGE, llm_config=llm_configuration, description=JULIA_DESCRIPTION)
interviewer_agent = AssistantAgent(name="interviewer_agent", system_message=INTERVIEWER_SYS_MESSAGE, llm_config=llm_configuration, description=INTERVIEWER_DESCRIPTION)

# Register model client for each agent
for agent in [julia_agent, farzana_agent, interviewer_agent]:
    agent.register_model_client(model_client_cls=NeuroengineClient)

# Create group chat and group chat manager
group_chat = GroupChat(agents=[julia_agent, interviewer_agent, farzana_agent], messages=[], role_for_select_speaker_messages="user", max_round=100)
group_chat_manager = GroupChatManager(name="master_agent", llm_config=llm_configuration, groupchat=group_chat, system_message=MASTER_SYS_MESSAGE, is_termination_msg=lambda x: x is not None and x["content"] is not None and "terminate" in x["content"].lower() or "goodbye" in x["content"].lower())
group_chat_manager.register_model_client(model_client_cls=NeuroengineClient)

# default_agent = AssistantAgent(name="default_agent",  llm_config=llm_configuration)
# default_agent.register_model_client(model_client_cls=NeuroengineClient)
# group_chat_manager.client = default_agent.client

# Initiate chat
v = interviewer_agent.initiate_chat(group_chat_manager, message="Hi candidate farzana and julia.", summary_method="reflection_with_llm")
print(v.summary)