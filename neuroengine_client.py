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
        messages = params["messages"]
        
        # Convert the list of messages into a single prompt
        prompt = "\n".join([f'{msg["role"]}:{msg["content"]}' for msg in messages])
        
        # Check the length of the prompt and handle if it exceeds 120k tokens
        prompt_tokens = len(prompt.split())
        if prompt_tokens > 120000:
            # Implement context compression or truncation
            prompt = self.compress_or_truncate_prompt(prompt, 120000)

        if params.get('functions', False):
            prompt += f"\nAvailable functions:{params['functions']}"
        
        # Request response from neuroengine
        response = self.neuroengine.request(prompt, max_new_len=120000)
        
        completion_tokens = len(response.split())
        total_tokens = prompt_tokens + completion_tokens

        # Handle function calls in the response
        if "function_call" in response:
            data = json.loads(response)
            function_call_data = data['function_call']
            function_call_data['arguments'] = json.dumps(function_call_data['arguments'])
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
            id=str(self.id),
            created=int(time.time()),
            object='chat.completion',
            model=self.model_name,
            choices=choices,
            cost=0.0
        )
        self.id += 1
        return chat_completion

    def compress_or_truncate_prompt(self, prompt: str, max_tokens: int) -> str:
        # Example implementation: simple truncation
        tokens = prompt.split()
        if len(tokens) > max_tokens:
            return " ".join(tokens[-max_tokens:])
        return prompt

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