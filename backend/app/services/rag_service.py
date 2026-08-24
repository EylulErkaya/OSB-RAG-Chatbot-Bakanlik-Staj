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
        self.pending_query = query
        self.pending_candidates = candidates

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