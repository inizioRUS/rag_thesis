from .prompt import RagPrompt
from openai import OpenAI


class LLMAggregateApi:
    def __init__(self, llm):
        self.client = OpenAI(
            api_key="",
            base_url="https://api.vsegpt.ru/v1",
        )
        self.llm = llm

    def __build_model_prompt(self, context) -> tuple[list[str], int]:
        final_prompt = [{"role": "system", "content": RagPrompt.replace("{context}", context)}]
        return final_prompt

    def invoke(self, text: str, context: str):
        prompt_1 = self.__build_model_prompt(context)
        prompt_1.append({"role": "user", "content": text})
        answer = self.flex(prompt_1)
        return answer

    def flex(self, messages):
        response_big = self.client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=messages,
            temperature=0.1,
            n=1,
            max_tokens=3000
        )

        response = response_big.choices[0].message.content
        return response
