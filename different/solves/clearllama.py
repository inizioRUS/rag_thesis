from llama_index.core import PromptTemplate
from llama_index.llms.ollama import Ollama
from openai import OpenAI

SYSTEM_PROMPT_TEMPLATE = (
    "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{}<|eot_id|>\n"
)
USER_PROMPT_TEMPLATE = "<|start_header_id|>user<|end_header_id|>\n\n{}<|eot_id|>\n"

ASSISTANT_PROMPT_TEMPLATE_END = "<|start_header_id|>assistant<|end_header_id|>\n\n"

system_prompt = """You are an expert consultant specializing in the Civil Code of the Russian Federation (Гражданский Кодекс Российской Федерации). Your role is to provide clear, concise, and accurate answers regarding legal matters under the Civil Code, including contracts, obligations, property rights, inheritance, corporate law, and other relevant areas. Always reference the applicable articles of the Civil Code when necessary, explain legal concepts in plain Russian, short."""


class ClearLlamma:
    def __init__(self):
        self.client = OpenAI(
            api_key="",
            base_url="https://api.vsegpt.ru/v1",
        )

    def __build_model_prompt(self, system_prompt: str, text: str) -> str:
        final_prompt = [{"role": "system", "content": system_prompt}]
        final_prompt.append({"role": "user", "content": text})
        return final_prompt

    def run(self, text):
        response_big = self.client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=self.__build_model_prompt(system_prompt, text),
            temperature=0.1,
            n=1,
            max_tokens=3000
        )
        response = response_big.choices[0].message.content
        return response
