from sentence_transformers import CrossEncoder


# ============================================================
# RERANKER
# ============================================================

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:

    def __init__(self):

        print(
            f"Reranker yükleniyor: {MODEL_NAME}"
        )

        self.model = CrossEncoder(
            MODEL_NAME
        )

        print(
            "✓ Reranker hazır"
        )

    def rerank(
        self,
        query: str,
        candidates: list[dict],
        top_k: int = 3,
    ):

        if not candidates:

            return []

        pairs = [
            [query,
             candidate["document"]
            ]
            for candidate in candidates
        ]

        scores = self.model.predict(
            pairs
        )

        ranked = []

        for candidate, score in zip(
            candidates,
            scores
        ):

            item = candidate.copy()

            item["reranker_score"] = float(
                score
            )

            ranked.append(item)

        ranked.sort(
            key=lambda x: x["reranker_score"],
            reverse=True
        )

        return ranked[:top_k]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    reranker = Reranker()

    query = (
        "Malatya-Güney OSB'de "
        "gıda sektöründe kaç kişi çalışıyor?"
    )

    documents = [

        "Sektör: KAYITLI MEDYANIN BASILMASI VE ÇOĞALTILMASI",

        "Sektör: BAŞKA YERDE SINIFLANDIRILMAMIŞ "
        "MAKİNA VE EKİPMAN İMALATI",

        "Sektör: GİYİM EŞYALARININ İMALATI",

        "Sektör: DİĞER ULAŞIM ARAÇLARININ İMALATI",

        "Sektör: GIDA ÜRÜNLERİ İMALATI",
    ]

    candidates = [
    {
        "document": document,
        "metadata": {},
        "distance": 0,
    }
    for document in documents
    ]

    results = reranker.rerank(
        query=query,
        candidates=candidates,
        top_k=5,
    )

    print("\n" + "=" * 70)
    print("RERANKER TESTİ")
    print("=" * 70)

    print(
        f"\nSoru: {query}"
    )

    for rank, item in enumerate(
    results,
    start=1
    ):

        print(
            f"\n#{rank}"
        )

        print(
            f"Score: "
            f"{item['reranker_score']:.4f}"
        )

        print(
            f"Text: "
            f"{item['document']}"
        )