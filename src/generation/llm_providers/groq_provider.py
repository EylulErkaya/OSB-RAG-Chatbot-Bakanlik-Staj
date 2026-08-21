from groq import Groq

from .base import LLMProvider


class GroqProvider(LLMProvider):

    def __init__(
        self,
        model: str = "llama-3.1-8b-instant",
        api_key: str | None = None,
    ):
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY bulunamadı."
            )

        self._model = model

        self._client = Groq(
            api_key=api_key
        )

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        response = self._client.chat.completions.create(
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
            temperature=0,
        )

        answer = response.choices[0].message.content

        if not answer:
            raise RuntimeError(
                "Groq boş yanıt döndürdü."
            )

        return answer.strip()

    @property
    def model_name(self) -> str:
        return self._model