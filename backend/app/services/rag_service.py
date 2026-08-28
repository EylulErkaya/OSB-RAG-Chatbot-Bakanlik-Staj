from typing import Any

from src.generation.rag_pipeline import RAGPipeline


class RAGService:
    """
    Backend ile mevcut RAG pipeline arasındaki servis katmanı.
    """

    def __init__(self):
        self.pipeline = RAGPipeline()
        
    def restore_pending_state(
        self,
        query: str,
        candidates: list[dict[str, Any]],
    ):
        self.pipeline.pending_query = query
        self.pipeline.pending_candidates = candidates
        
    def restore_pending_listing(
        self,
        listing_state: dict[str, Any],
    ):
        self.pipeline.pending_listing = listing_state

    def restore_last_osb_state(
        self,
        *,
        osb_id: int | None,
        osb_name: str | None,
        intent: str | None,
        requested_field: str | None,
    ):
        self.pipeline.last_osb_id = osb_id
        self.pipeline.last_osb_name = osb_name
        self.pipeline.last_intent = intent
        self.pipeline.last_requested_field = requested_field

    def last_osb_state(self) -> dict[str, Any]:
        return {
            "last_osb_id": self.pipeline.last_osb_id,
            "last_osb_name": self.pipeline.last_osb_name,
            "last_intent": self.pipeline.last_intent,
            "last_requested_field": self.pipeline.last_requested_field,
        }

    def ask(self, query: str) -> dict[str, Any]:
        """
        Kullanıcı sorusunu mevcut RAG pipeline'a gönderir.
        """
        return self.pipeline.ask(query)
    
    def select(self, selection: int) -> dict[str, Any]:
        """
        Bekleyen ambiguous seçim için RAG pipeline'ı çalıştırır.
        """
        return self.pipeline.ask(str(selection))
