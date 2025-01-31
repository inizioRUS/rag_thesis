from .prompt import AGENT_NEW_QUESTION
from openai import OpenAI





class LLMAggregateNewQuestion:
    def __init__(self):
        self.client = OpenAI(
            api_key="",
            base_url="https://api.vsegpt.ru/v1",
        )
    def __build_model_prompt(self) -> tuple[list[str], int]:
        final_prompt = [{"role": "system", "content": AGENT_NEW_QUESTION}]
        return final_prompt

    def invoke(self, text: str):
        prompt_1 = self.__build_model_prompt()
        prompt_1.append({"role": "user", "content": text})
        answer = self.flex(prompt_1)
        return answer

    def flex(self, messages):

        response_big = self.client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=messages,
            temperature=0.1,
            n=1,
            max_tokens=3000
        )

        response = response_big.choices[0].message.content.split("\n")
        return response
