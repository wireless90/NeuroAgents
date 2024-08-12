# NeuroengineClient.py
from typing import Dict, Any, List

from openai.types.chat.chat_completion_message import FunctionCall

from neuroengine import Neuroengine
from openai.types.chat import ChatCompletion
from openai.types.completion_usage import CompletionUsage
from openai.types.chat.chat_completion import ChatCompletionMessage, Choice
from types import SimpleNamespace
import time
import json
class NeuroengineClient:
    def __init__(self, config: Dict[str, Any], **kwargs):
        self.neuroengine = Neuroengine(
            service_name=config.get("service_name"),
            server_address=config.get("server_address"),
            server_port=config.get("server_port", 443),
            key=config.get("key", ""),
            verify_ssl=config.get("verify_ssl", True)
        )
        self.model_name = config["model"]
        self.id = 1

    def create(self, params: Dict[str, Any]) -> ChatCompletion:
        #print("Create method called with params:", params)  # Debug statement
        messages = params["messages"]
        
        # Convert the list of messages into a single prompt
        # TODO See if needs a prompt summary
        prompt = "\n".join([f'{msg["role"]}:{msg["content"]}' for msg in messages])
        if params.get('functions', False):
            prompt += f"\nAvailable functions:{params['functions']}"
        response = self.neuroengine.request(prompt, max_new_len=4000)
        
        prompt_tokens = len(prompt.split())
        completion_tokens = len(response.split())
        total_tokens = prompt_tokens + completion_tokens

        if "function_call" in response:
            # Convert the string to a Python dictionary
            print("woooohoo function_call mann!!!")
            data = json.loads(response) # dict type

            # Extract the function_call dictionary
            function_call_data = data['function_call']
            function_call_data['arguments'] = json.dumps(function_call_data['arguments'])
            
            print("Function call data extracted...")
            print(function_call_data)
            # Create an instance of FunctionCall
            function_call = FunctionCall(**function_call_data)

            message = ChatCompletionMessage(
                role="assistant",
                content=None,
                function_call=function_call,
                tool_calls=None
            )
        else:

            message = ChatCompletionMessage(
                role="assistant",
                content=response,
                function_call=None,
                tool_calls=None
            )
        choices = [Choice(finish_reason="stop", index=0, message=message)]

        usage = SimpleNamespace(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
        )

        chat_completion = ChatCompletion(
            id=str(self.id),  # Generate or fetch a unique ID as per your requirements
            created=int(time.time()),
            object='chat.completion',
            model=self.model_name,
            choices=choices,
            #usage=usage,
            cost=0.0  # Adjust the cost calculation as needed
        )
        self.id += 1
        return chat_completion

    # Function to convert FunctionCall instance to JSON string
    def _function_call_to_json_string(self, function_call: FunctionCall) -> str:
        final_dict: dict = self._function_call_to_dict(function_call)

        # Convert the final dictionary to a JSON string
        return json.dumps(final_dict)

    # Function to convert FunctionCall instance to JSON string
    def _function_call_to_dict(self, function_call: FunctionCall) -> str:
        # Convert FunctionCall instance to a dictionary
        function_call_dict = function_call.model_dump()
        function_name: str = function_call_dict['name']

        # Ensure the arguments field is a JSON string
        function_call_dict['arguments'] = json.dumps(json.loads(function_call_dict['arguments']))
        # Create the final dictionary structure
        final_dict = {"function_call": function_call_dict}
        # final_dict = {"function_call": function_call_dict, "role": "function", 'name':function_name}

        
        return final_dict
    
    def message_retrieval(self, response: ChatCompletion) -> List[str]:
        msgs = []
        for choice in response.choices:
            if choice.message.function_call is not None:
                func_json_string: str= self._function_call_to_json_string(choice.message.function_call)
                func_dict: dict = self._function_call_to_dict(choice.message.function_call)
                msgs.append(func_dict)
            else :
                msgs.append(choice.message.content)

        return msgs

        # return [self._function_call_to_json_string(choice.message.function_call) if choice.message.function_call is not None else choice.message.content  for choice in response.choices]
    
    def cost(self, response: ChatCompletion) -> float:
        return 0.0

    @staticmethod
    def get_usage(response: ChatCompletion) -> Dict[str, Any]:
        return dict()