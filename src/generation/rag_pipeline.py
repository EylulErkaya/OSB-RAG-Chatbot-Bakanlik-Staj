from typing import Any

from src.retrieval.retrieval_pipeline import retrieve

from .context_builder import ContextBuilder
from .prompt_builder import PromptBuilder
from .answer_generator import AnswerGenerator


# ============================================================
# RAG PIPELINE
# ============================================================

class RAGPipeline:

    def __init__(self):

        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder()
        self.answer_generator = AnswerGenerator()

        # ====================================================
        # CONVERSATION STATE
        # ====================================================

        self.pending_query: str | None = None
        self.pending_candidates: list[dict[str, Any]] = []
        self.pending_listing: dict[str, Any] | None = None

    # ========================================================
    # ASK
    # ========================================================

    def ask(
        self,
        query: str,
    ) -> dict[str, Any]:

        query = query.strip()

        # ====================================================
        # 1. BEKLEYEN LISTING İÇİN DEVAM İSTEĞİ
        # ====================================================

        if (
            self.pending_listing
            and query.lower() == "devam"
        ):

            return self._handle_listing_continue()

        # ====================================================
        # 2. BEKLEYEN AMBIGUOUS SEÇİM VAR MI?
        # ====================================================

        if self.pending_candidates:

            selection_result = self._handle_selection(
                query
            )

            # ------------------------------------------------
            # GEÇERSİZ SEÇİM
            # ------------------------------------------------

            if selection_result["status"] == "invalid":

                return {
                    "query": query,
                    "retrieval": {
                        "status": "selection_error",
                        "candidates": self.pending_candidates,
                    },
                    "context": {
                        "status": "selection_error",
                        "llm_allowed": False,
                    },
                    "prompt": {
                        "status": "selection_error",
                        "llm_allowed": False,
                    },
                    "answer": {
                        "status": "selection_error",
                        "answer": (
                            "Geçersiz seçim. "
                            "Lütfen listede gösterilen "
                            "numaralardan birini yazın."
                        ),
                        "llm_called": False,
                    },
                }

            # ------------------------------------------------
            # ------------------------------------------------
            # SEÇİM BAŞARILI
            # ------------------------------------------------

            selected_osb = selection_result["candidate"]

            original_query = self.pending_query

            if not original_query:
                return {
                    "query": query,
                    "retrieval": {
                        "status": "selection_error",
                    },
                    "context": {
                        "status": "selection_error",
                        "llm_allowed": False,
                    },
                    "prompt": {
                        "status": "selection_error",
                        "llm_allowed": False,
                    },
                    "answer": {
                        "status": "selection_error",
                        "answer": "Bekleyen soru bulunamadı.",
                        "llm_called": False,
                    },
                }

            retrieval_result = retrieve(
                query=original_query,
                selected_osb_id=selected_osb["id"],
                selected_osb_name=selected_osb["name"],
            )

            result = self._build_pipeline_result(
                query=original_query,
                retrieval_result=retrieval_result,
                selected_osb=selected_osb,
                original_query=original_query,
            )

            # Retrieval ve cevap başarıyla oluşturulduktan sonra state temizle
            self._clear_pending_state()

            return result

            # ------------------------------------------------
            # SEÇİLEN OSB İLE RETRIEVAL
            # ------------------------------------------------

            retrieval_result = retrieve(
                query=original_query,
                selected_osb_id=selected_osb["id"],
                selected_osb_name=selected_osb["name"],
            )

            # ------------------------------------------------
            # NORMAL PIPELINE'A DEVAM
            # ------------------------------------------------

            return self._build_pipeline_result(
                query=query,
                retrieval_result=retrieval_result,
                selected_osb=selected_osb,
                original_query=original_query,
            )

        # ====================================================
        # 2. NORMAL RETRIEVAL
        # ====================================================

        retrieval_result = retrieve(
            query=query
        )

        # ====================================================
        # 3. AMBIGUOUS STATE KAYDET
        # ====================================================

        if retrieval_result.get("status") == "ambiguous":

            self.pending_query = query

            self.pending_candidates = (
                retrieval_result.get(
                    "candidates",
                    []
                )
            )
            
        # ====================================================
        # 4. LISTING STATE KAYDET
        # ====================================================

        if retrieval_result.get("status") == "listing":

            self.pending_listing = {
                "query": query,
                "filters": retrieval_result.get(
                    "filters",
                    {}
                ),
                "offset": retrieval_result.get(
                    "offset",
                    0
                ),
                "limit": retrieval_result.get(
                    "limit",
                    10
                ),
                "total_count": retrieval_result.get(
                    "total_count",
                    0
                ),
            }

        # ====================================================
        # 4. NORMAL PIPELINE
        # ====================================================

        return self._build_pipeline_result(
            query=query,
            retrieval_result=retrieval_result,
        )

    # ========================================================
    # LISTING CONTINUE HANDLER
    # ========================================================

    def _handle_listing_continue(self) -> dict[str, Any]:

        listing_state = self.pending_listing

        if not listing_state:
            raise RuntimeError("Bekleyen listeleme durumu bulunamadı.")

        old_offset = listing_state.get("offset", 0)
        limit = listing_state.get("limit", 10)
        total_count = listing_state.get("total_count", 0)
        new_offset = old_offset + limit

        if new_offset >= total_count:

            self.pending_listing = None

            return {
                "query": "devam",
                "retrieval": {
                    "status": "listing_end",
                },
                "context": {
                    "status": "listing_end",
                    "llm_allowed": False,
                },
                "prompt": {
                    "status": "listing_end",
                    "llm_allowed": False,
                },
                "answer": {
                    "status": "listing_end",
                    "answer": "Başka kayıt bulunmamaktadır.",
                    "llm_called": False,
                },
            }

        retrieval_result = retrieve(
            query=listing_state["query"],
            offset=new_offset,
            limit=limit,
            listing_filters=listing_state.get("filters"),
        )

        self.pending_listing = {
            "query": listing_state["query"],
            "filters": retrieval_result.get("filters", {}),
            "offset": retrieval_result.get("offset", new_offset),
            "limit": retrieval_result.get("limit", limit),
            "total_count": retrieval_result.get(
                "total_count",
                total_count,
            ),
        }

        return self._build_pipeline_result(
            query=listing_state["query"],
            retrieval_result=retrieval_result,
        )

    # ========================================================
    # SELECTION HANDLER
    # ========================================================

    def _handle_selection(
        self,
        query: str,
    ) -> dict[str, Any]:

        query = query.strip()

        # ----------------------------------------------------
        # SADECE SAYISAL SEÇİM
        # ----------------------------------------------------

        if not query.isdigit():

            return {
                "status": "invalid",
            }

        selected_index = int(query) - 1

        # ----------------------------------------------------
        # INDEX KONTROLÜ
        # ----------------------------------------------------

        if (
            selected_index < 0
            or selected_index >= len(
                self.pending_candidates
            )
        ):

            return {
                "status": "invalid",
            }

        candidate = self.pending_candidates[
            selected_index
        ]

        return {
            "status": "selected",
            "candidate": candidate,
        }

    # ========================================================
    # CLEAR STATE
    # ========================================================

    def _clear_pending_state(self):

        self.pending_query = None
        self.pending_candidates = []

    # ========================================================
    # PIPELINE RESULT
    # ========================================================

    def _build_pipeline_result(
        self,
        query: str,
        retrieval_result: dict[str, Any],
        selected_osb: dict[str, Any] | None = None,
        original_query: str | None = None,
    ) -> dict[str, Any]:

        # ----------------------------------------------------
        # CONTEXT
        # ----------------------------------------------------

        context_result = self.context_builder.build(
            retrieval_result
        )

        # ----------------------------------------------------
        # PROMPT
        # ----------------------------------------------------

        prompt_result = self.prompt_builder.build(
            query=original_query or query,
            context_result=context_result,
        )

        # ----------------------------------------------------
        # LLM
        # ----------------------------------------------------

        answer_result = self.answer_generator.generate(
            prompt_result
        )

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        result = {
            "query": query,
            "original_query": original_query,
            "retrieval": retrieval_result,
            "context": context_result,
            "prompt": prompt_result,
            "answer": answer_result,
        }

        if selected_osb:

            result["selected_osb"] = {
                "id": selected_osb["id"],
                "name": selected_osb["name"],
                "city": selected_osb.get("city"),
                "district": selected_osb.get("district"),
            }

        return result

# ============================================================
# AMBIGUOUS SELECTION TEST
# ============================================================

def test_ambiguous_selection():

    print("\n" + "=" * 70)
    print("AMBIGUOUS SELECTION TEST")
    print("=" * 70)

    # Test için ayrı pipeline
    pipeline = RAGPipeline()

    # ========================================================
    # 1. AMBIGUOUS SORU
    # ========================================================

    first_result = pipeline.ask(
        "Malatya OSB'de kaç fabrika üretim yapıyor?"
    )

    retrieval = first_result["retrieval"]

    print("\n1. SORU:")
    print(
        "Malatya OSB'de kaç fabrika üretim yapıyor?"
    )

    print(
        "\nStatus:",
        retrieval.get("status")
    )

    print(
        "Aday sayısı:",
        len(
            retrieval.get(
                "candidates",
                []
            )
        )
    )

    print("\nCEVAP:")

    print(
        first_result["answer"].get(
            "answer",
            ""
        )
    )

    # ========================================================
    # KONTROLLER
    # ========================================================

    if retrieval.get("status") != "ambiguous":

        print(
            "\n❌ TEST BAŞARISIZ:"
            " Soru ambiguous dönmedi."
        )

        return

    if not pipeline.pending_query:

        print(
            "\n❌ TEST BAŞARISIZ:"
            " pending_query oluşmadı."
        )

        return

    if not pipeline.pending_candidates:

        print(
            "\n❌ TEST BAŞARISIZ:"
            " pending_candidates oluşmadı."
        )

        return

    print(
        "\n✓ Ambiguous state oluşturuldu."
    )

    # ========================================================
    # 2. KULLANICI 1 SEÇİYOR
    # ========================================================

    print("\n" + "-" * 70)
    print("KULLANICI SEÇİMİ: 1")
    print("-" * 70)

    second_result = pipeline.ask("1")

    second_retrieval = (
        second_result["retrieval"]
    )

    print(
        "\nStatus:",
        second_retrieval.get(
            "status"
        )
    )

    print(
        "OSB ID:",
        second_retrieval.get(
            "osb_id"
        )
    )

    print(
        "OSB:",
        second_retrieval.get(
            "osb_name"
        )
    )

    print("\nCEVAP:")

    print(
        second_result["answer"].get(
            "answer",
            ""
        )
    )

    # ========================================================
    # 3. SEÇİM KONTROLLERİ
    # ========================================================

    if (
        second_retrieval.get("status")
        != "success"
    ):

        print(
            "\n❌ TEST BAŞARISIZ:"
            " Seçim sonrası retrieval success olmadı."
        )

        return

    selected_osb = (
        second_result.get(
            "selected_osb"
        )
    )

    if not selected_osb:

        print(
            "\n❌ TEST BAŞARISIZ:"
            " selected_osb bulunamadı."
        )

        return

    if (
        second_retrieval.get("osb_id")
        != selected_osb.get("id")
    ):

        print(
            "\n❌ TEST BAŞARISIZ:"
            " OSB ID eşleşmiyor."
        )

        print(
            "Retrieval ID:",
            second_retrieval.get(
                "osb_id"
            )
        )

        print(
            "Selected ID:",
            selected_osb.get(
                "id"
            )
        )

        return

    if (
        second_retrieval.get("osb_name")
        != selected_osb.get("name")
    ):

        print(
            "\n❌ TEST BAŞARISIZ:"
            " OSB adı eşleşmiyor."
        )

        print(
            "Retrieval OSB:",
            second_retrieval.get(
                "osb_name"
            )
        )

        print(
            "Selected OSB:",
            selected_osb.get(
                "name"
            )
        )

        return

    # ========================================================
    # 4. STATE TEMİZLENDİ Mİ?
    # ========================================================

    if pipeline.pending_query is not None:

        print(
            "\n❌ TEST BAŞARISIZ:"
            " pending_query temizlenmedi."
        )

        return

    if pipeline.pending_candidates:

        print(
            "\n❌ TEST BAŞARISIZ:"
            " pending_candidates temizlenmedi."
        )

        return

    print(
        "\n✓ Seçilen OSB doğru."
    )

    print(
        "✓ OSB ID doğru."
    )

    print(
        "✓ OSB adı doğru."
    )

    print(
        "✓ Conversation state temizlendi."
    )

    print(
        "\n🎉 AMBIGUOUS SELECTION TEST BAŞARILI!"
    )



# ============================================================
# TEST QUERIES
# ============================================================

TEST_QUERIES = [

    "Malatya-Güney OSB'de kaç boş parsel var?",

    "Malatya-Güney OSB'de kaç fabrika üretim yapıyor?",

    "Malatya-Güney OSB'de kaç kişi istihdam ediliyor?",

    "Malatya-Güney OSB hangi bölgede bulunuyor?",

    "Malatya-Güney OSB'de gıda sektöründe kaç kişi çalışıyor?",

    "Malatya-Güney OSB deprem bölgesinde mi?",

    "Malatya-Güney OSB yatırım programında mı?",

    "Malatya OSB'de kaç fabrika üretim yapıyor?",

    "Malatya OSB deprem bölgesinde mi?",

    "Olmayanşehir OSB'de kaç boş parsel var?",
    
    "Malatya'daki OSB'leri listele",
    
    "Doğu Anadolu'daki OSB'leri listele",
    
    "Türkiye'deki OSB'leri listele",
    
    "Malatya'daki Karma OSB'leri listele",
    
    "Karma OSB'leri listele",
]


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("GERÇEK RAG PIPELINE TESTİ")
    print("=" * 70)

    for query in TEST_QUERIES:
        
        pipeline = RAGPipeline()

        print("\n" + "=" * 70)
        print(f"SORU: {query}")
        print("=" * 70)

        result = pipeline.ask(
            query
        )

        retrieval = result["retrieval"]
        context = result["context"]
        answer = result["answer"]

        print(
            f"\nRetrieval status: "
            f"{retrieval.get('status')}"
        )

        print(
            f"Intent: "
            f"{retrieval.get('intent')}"
        )

        print(
            f"OSB: "
            f"{retrieval.get('osb_name')}"
        )

        print(
            f"\nContext status: "
            f"{context.get('status')}"
        )

        print(
            f"LLM allowed: "
            f"{context.get('llm_allowed')}"
        )

        print(
            f"\nLLM status: "
            f"{answer.get('status')}"
        )

        print(
            f"LLM called: "
            f"{answer.get('llm_called')}"
        )

        print("\nCEVAP:")

        print(
            answer.get(
                "answer",
                ""
            )
        )
        
    # ========================================================
    # AMBIGUOUS SELECTION TEST
    # ========================================================
    test_ambiguous_selection()
