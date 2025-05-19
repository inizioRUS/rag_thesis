from .prompt import RagPrompt
from llama_index.llms.ollama import Ollama
from llama_index.core import PromptTemplate
from transformers import LlamaTokenizerFast

SYSTEM_PROMPT_TEMPLATE = (
    "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{}<|eot_id|>\n"
)
USER_PROMPT_TEMPLATE = "<|start_header_id|>user<|end_header_id|>\n\n{}<|eot_id|>\n"

ASSISTANT_PROMPT_TEMPLATE = "<|start_header_id|>assistant<|end_header_id|>\n\n{}<|eot_id|>\n"

ASSISTANT_PROMPT_TEMPLATE_END = "<|start_header_id|>assistant<|end_header_id|>\n\n"




class LLMAggregate:
    def __init__(self, llm: Ollama):
        self.llm = llm
        self._tokenizer = LlamaTokenizerFast.from_pretrained("hf-internal-testing/llama-tokenizer")



    def __build_model_prompt(self, context) -> tuple[list[str], int]:
        final_prompt = [RagPrompt.replace("{context}", context)]
        return final_prompt

    def invoke(self, text: str, context):
        prompt = self.__build_model_prompt(context)
        end = USER_PROMPT_TEMPLATE.format(text) + ASSISTANT_PROMPT_TEMPLATE_END
        prompt = "".join(prompt) + end
        answer = self.llm.predict(PromptTemplate(prompt))
        split_position = answer.rfind(ASSISTANT_PROMPT_TEMPLATE_END)

        if split_position >= 0:
            answer = answer[split_position + len(ASSISTANT_PROMPT_TEMPLATE_END):]
        return answer
