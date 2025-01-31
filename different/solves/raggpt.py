import requests
from llama_index.core import PromptTemplate
from llama_index.llms.ollama import Ollama
from openai import OpenAI

SYSTEM_PROMPT_TEMPLATE = (
    "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{}<|eot_id|>\n"
)
USER_PROMPT_TEMPLATE = "<|start_header_id|>user<|end_header_id|>\n\n{}<|eot_id|>\n"

ASSISTANT_PROMPT_TEMPLATE_END = "<|start_header_id|>assistant<|end_header_id|>\n\n"

system_prompt = """You are an expert consultant specializing in the Civil Code of the Russian Federation (Гражданский Кодекс Российской Федерации). Your role is to provide clear, concise, and accurate answers regarding legal matters under the Civil Code, including contracts, obligations, property rights, inheritance, corporate law, and other relevant areas. Always reference the applicable articles of the Civil Code when necessary, explain legal concepts in plain Russian, short."""


class ClearGPT:
    def __init__(self):
        pass

    def run(self, text):
        return  requests.post("http://localhost:8007/query", json={"service": "civi", "text": text}).json()