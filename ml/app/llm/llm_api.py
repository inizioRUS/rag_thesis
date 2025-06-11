from .prompt import RagPrompt, RagPromptDocument
from openai import OpenAI


class LLMAAPI:
    def __init__(self, token: str):
        self.client = OpenAI(
            api_key=token,
            base_url="https://api.vsegpt.ru/v1",
        )

    def __build_model_prompt(self, context) -> tuple[list[str], int]:
        final_prompt = [{"role": "system", "content": RagPromptDocument.replace("{context}", context)}]
        return final_prompt

    def __build_model_prompt_doc(self, context, doc) -> tuple[list[str], int]:
        final_prompt = [
            {"role": "system", "content": RagPromptDocument.replace("{context}", context).replace("{format}", doc)}]
        return final_prompt

    def invoke(self, text: str, context: str):
        prompt_1 = self.__build_model_prompt(context)
        prompt_1.append({"role": "user", "content": text})
        answer = self.flex(prompt_1)
        return answer

    def invoke_doc(self, text: str, context: str, document_prompt):
        prompt_1 = self.__build_model_prompt_doc(context, document_prompt)
        prompt_1.append({"role": "user", "content": text})
        answer = self.flex(prompt_1)
        return answer

    def flex(self, messages):
        response_big = self.client.chat.completions.create(
            model="openai/gpt-4.1-mini",
            messages=messages,
            temperature=0.1,
            n=1,
            max_tokens=3000
        )

        response = response_big.choices[0].message.content
        return response
