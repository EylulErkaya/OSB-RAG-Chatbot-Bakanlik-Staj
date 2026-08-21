import ollama

from .base import LLMProvider


class OllamaProvider(LLMProvider):

    def __init__(
        self,
        model: str = "qwen3:4b-instruct",
    ):
        self._model = model

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        response = ollama.chat(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            options={
                "temperature": 0,
            },
        )

        return response["message"]["content"].strip()

    @property
    def model_name(self) -> str:
        return self._model