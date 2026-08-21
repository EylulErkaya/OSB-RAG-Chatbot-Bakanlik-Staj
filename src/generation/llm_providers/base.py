from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """LLM'den cevap üretir."""
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Kullanılan modelin adını döndürür."""
        raise NotImplementedError