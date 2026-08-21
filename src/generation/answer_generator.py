from .llm_providers.base import LLMProvider
from .llm_providers.factory import get_provider


# ============================================================
# ANSWER GENERATOR
# ============================================================

class AnswerGenerator:

    def __init__(
        self,
        provider: LLMProvider | None = None,
    ):
        self.provider = (
            provider
            if provider is not None
            else get_provider()
        )

    # ========================================================
    # GENERATE
    # ========================================================

    def generate(
        self,
        prompt_result: dict,
    ) -> dict:

        # ----------------------------------------------------
        # LLM ÇAĞRILMAMALI
        # ----------------------------------------------------

        if not prompt_result.get(
            "llm_allowed",
            False,
        ):

            return {
                "status": prompt_result.get(
                    "status",
                    "blocked",
                ),
                "answer": prompt_result.get(
                    "message",
                    "LLM çağrılmadı.",
                ),
                "model": self.provider.model_name,
                "llm_called": False,
            }

        # ----------------------------------------------------
        # PROMPT
        # ----------------------------------------------------

        system_prompt = prompt_result.get(
            "system_prompt",
            "",
        )

        user_prompt = prompt_result.get(
            "user_prompt",
            "",
        )

        if not system_prompt or not user_prompt:

            return {
                "status": "invalid_prompt",
                "answer": (
                    "LLM için geçerli bir prompt "
                    "oluşturulamadı."
                ),
                "model": self.provider.model_name,
                "llm_called": False,
            }

        # ----------------------------------------------------
        # LLM PROVIDER
        # ----------------------------------------------------

        try:

            answer = self.provider.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

            return {
                "status": "success",
                "answer": answer,
                "model": self.provider.model_name,
                "llm_called": True,
            }

        except Exception as exc:

            return {
                "status": "error",
                "answer": (
                    "Yanıt oluşturulurken "
                    "bir hata oluştu."
                ),
                "model": self.provider.model_name,
                "llm_called": False,
                "error": str(exc),
            }