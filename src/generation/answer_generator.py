import ollama


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "qwen3:4b-instruct"


# ============================================================
# ANSWER GENERATOR
# ============================================================

class AnswerGenerator:

    def __init__(
        self,
        model_name: str = MODEL_NAME,
    ):
        self.model_name = model_name

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
            False
        ):

            return {
                "status": prompt_result.get(
                    "status",
                    "blocked"
                ),
                "answer": prompt_result.get(
                    "message"
                ),
                "model": self.model_name,
                "llm_called": False,
            }

        system_prompt = prompt_result.get(
            "system_prompt",
            ""
        )

        user_prompt = prompt_result.get(
            "user_prompt",
            ""
        )

        # ----------------------------------------------------
        # PROMPT KONTROLÜ
        # ----------------------------------------------------

        if not system_prompt or not user_prompt:

            return {
                "status": "invalid_prompt",
                "answer": (
                    "LLM için geçerli bir prompt "
                    "oluşturulamadı."
                ),
                "model": self.model_name,
                "llm_called": False,
            }

        # ----------------------------------------------------
        # OLLAMA
        # ----------------------------------------------------

        try:

            response = ollama.chat(
                model=self.model_name,
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

            answer = (
                response["message"]["content"]
                .strip()
            )

            return {
                "status": "success",
                "answer": answer,
                "model": self.model_name,
                "llm_called": True,
            }

        except Exception as exc:

            return {
                "status": "error",
                "answer": (
                    "Yanıt oluşturulurken "
                    "bir hata oluştu."
                ),
                "model": self.model_name,
                "llm_called": False,
                "error": str(exc),
            }