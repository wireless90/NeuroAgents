
import json
from neuroengine_client import NeuroengineClient  # Ensure correct case
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, ConversableAgent

# Create the configuration for the AssistantAgent
config_list_custom = config_list_from_json(
    "OAI_CONFIG_LIST.json",
    filter_dict={"model_client_cls": ["NeuroengineClient"]},
)

# Debug: Print config to ensure it is loaded correctly

# Create the AssistantAgent with a name
assistant = ConversableAgent(
    name="Student",
    system_message="Your name is Cathy and you are meeting Joe for a c programming interview regarding secure coding with c. He is a c# tech lead. Once he is done chatting, he will tell you GOODBYE, thank him and end the covo,do not continue. Do not tell him goodbye until he tells you that first.",
    llm_config={"config_list": config_list_custom},
    human_input_mode="NEVER",
    is_termination_msg=lambda x: "goodbye" in x["content"].lower()
)

# Create the AssistantAgent with a name
master = ConversableAgent(
    name="Interviewer",
    system_message="Your name is Joe and you are a secure coding expert in c. You are to give c examples which contain vulnerabilities of which the interviewee must solve. You are to grade their work, max 3 tasks to them.Once all 2 tasks given and graded, end the chat by saying GOODBYE, do not further continue chat.",
    llm_config={"config_list": config_list_custom},

)

# Register the custom model client
assistant.register_model_client(model_client_cls=NeuroengineClient)
master.register_model_client(model_client_cls=NeuroengineClient)


# Example conversation
if __name__ == "__main__":
    assistant.initiate_chat(master, max_turns=20, message="Hi there")

    # Debug: Ensure create method is called
    #print("Initiated chat between assistant and master.")