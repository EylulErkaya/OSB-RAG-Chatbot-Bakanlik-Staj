from google import genai

from .base import LLMProvider


class GeminiProvider(LLMProvider):

    def __init__(
        self,
        model: str = "gemini-2.5-flash-lite",
        api_key: str | None = None,
    ):
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY bulunamadı."
            )

        self._model = model

        self._client = genai.Client(
            api_key=api_key
        )

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        response = self._client.models.generate_content(
            model=self._model,
            contents=user_prompt,
            config={
                "system_instruction": system_prompt,
                "temperature": 0,
            },
        )

        if not response.text:
            raise RuntimeError(
                "Gemini boş yanıt döndürdü."
            )

        return response.text.strip()

    @property
    def model_name(self) -> str:
        return self._model