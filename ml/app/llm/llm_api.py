from .prompt import RagPrompt, RagPromptDocument, Update_working_context
from openai import OpenAI


class LLMAAPI:
    def __init__(self, token: str):
        self.client = OpenAI(
            api_key=token,
            base_url="https://api.vsegpt.ru/v1",
        )

    def __build_model_prompt(self, context, new_working_context, old_msg, queries) -> tuple[list[str], int]:
        final_prompt = [{"role": "system",
                         "content": RagPromptDocument.replace("{context}", context).replace("{working_context}",
                                                                                            new_working_context).replace(
                             "{history}", old_msg).replace("{queries}", queries)}]
        return final_prompt

    def __build_model_prompt_doc(self, context, new_working_context, old_msg, queries, doc) -> tuple[list[str], int]:
        final_prompt = [
            {"role": "system",
             "content": RagPromptDocument.replace("{context}", context).replace("{format}", doc).replace(
                 "{working_context}", new_working_context).replace("{history}", old_msg).replace("{queries}", queries)}]
        return final_prompt

    def __build_model_prompt_update_working_context(self, old_msg, working_context, queries) -> tuple[list[str], int]:
        final_prompt = [
            {"role": "system",
             "content": Update_working_context.replace("{working_context}", working_context).replace("{new_dialogue}",
                                                                                                queries).replace(
                 "{old_msg}", old_msg)}]
        return final_prompt

    def invoke(self, text: str, context: str, new_working_context,  old_msg, queries):
        prompt_1 = self.__build_model_prompt(context, new_working_context, old_msg, queries)
        prompt_1.append({"role": "user", "content": text})
        answer = self.flex(prompt_1)
        return answer

    def invoke_doc(self, text: str, context: str, new_working_context, old_msg,queries, document_prompt):
        prompt_1 = self.__build_model_prompt_doc(context, new_working_context, old_msg, queries, document_prompt)
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

    def invoke_update_working_context(self, old_msg, working_context, queries):
        prompt_1 = self.__build_model_prompt_update_working_context(old_msg, working_context, queries)
        prompt_1.append({"role": "user", "content": "Please return the updated working context only. Keep it brief, relevant, and focused on user goals, characters, and relationships."})
        answer = self.flex(prompt_1)
        return answer
