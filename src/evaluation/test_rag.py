from src.generation.rag_pipeline import RAGPipeline


# ============================================================
# TEST CASES
# ============================================================

TEST_CASES = [

    # --------------------------------------------------------
    # NORMAL RETRIEVAL
    # --------------------------------------------------------

    {
        "query": "Malatya-Güney OSB'de kaç boş parsel var?",
        "expected_status": "success",
        "expected_intent": "parcel",
        "expected_osb_id": 305,
        "expected_answer_contains": ["19"],
    },

    {
        "query": "Malatya-Güney OSB'de kaç fabrika üretim yapıyor?",
        "expected_status": "success",
        "expected_intent": "employment",
        "expected_osb_id": 305,
        "expected_answer_contains": ["21"],
    },

    {
        "query": "Malatya-Güney OSB hangi bölgede bulunuyor?",
        "expected_status": "success",
        "expected_intent": "general",
        "expected_osb_id": 305,
        "expected_answer_contains": ["Doğu Anadolu"],
    },

    {
        "query": "Malatya-Güney OSB deprem bölgesinde mi?",
        "expected_status": "success",
        "expected_intent": "general",
        "expected_osb_id": 305,
        "expected_answer_contains": [
            "Hayır",
            "değildir",
        ],
    },

    {
        "query": "Malatya-Güney OSB yatırım programında mı?",
        "expected_status": "success",
        "expected_intent": "general",
        "expected_osb_id": 305,
        "expected_answer_contains": [
            "Evet",
            "yatırım programındadır",
        ],
    },

    # --------------------------------------------------------
    # SECTOR
    # --------------------------------------------------------

    {
        "query": (
            "Malatya-Güney OSB'de "
            "gıda sektöründe kaç kişi çalışıyor?"
        ),
        "expected_status": "success",
        "expected_intent": "sector",
        "expected_osb_id": 305,
        "expected_answer_contains": [
            "bulunmamaktadır",
        ],
    },

    # --------------------------------------------------------
    # AMBIGUOUS
    # --------------------------------------------------------

    {
        "query": "Malatya OSB'de kaç fabrika üretim yapıyor?",
        "expected_status": "ambiguous",
        "expected_intent": "employment",
        "expected_osb_id": None,
        "expected_llm_called": False,
    },

    {
        "query": "Malatya OSB deprem bölgesinde mi?",
        "expected_status": "ambiguous",
        "expected_intent": "general",
        "expected_osb_id": None,
        "expected_llm_called": False,
    },

    # --------------------------------------------------------
    # NOT FOUND
    # --------------------------------------------------------

    {
        "query": "Olmayanşehir OSB'de kaç boş parsel var?",
        "expected_status": "not_found",
        "expected_intent": "parcel",
        "expected_osb_id": None,
        "expected_llm_called": False,
    },
    
        # --------------------------------------------------------
    # EK PARSEL TESTLERİ
    # --------------------------------------------------------

    {
        "query": "Malatya-Güney OSB'de boş parsel alanı kaç hektar?",
        "expected_status": "success",
        "expected_intent": "parcel",
        "expected_osb_id": 305,
        "expected_answer_contains": ["193.86"],
    },

    {
        "query": "Malatya-Güney OSB'nin toplam parsel sayısı kaç?",
        "expected_status": "success",
        "expected_intent": "parcel",
        "expected_osb_id": 305,
        "expected_answer_contains": ["50"],
    },

    {
        "query": "Malatya-Güney OSB'de kaç parsel tahsis edilmiş?",
        "expected_status": "success",
        "expected_intent": "parcel",
        "expected_osb_id": 305,
        "expected_answer_contains": ["15"],
    },

    # --------------------------------------------------------
    # EK İSTİHDAM TESTLERİ
    # --------------------------------------------------------

    {
        "query": "Malatya-Güney OSB'de üretimdeki toplam istihdam kaç?",
        "expected_status": "success",
        "expected_intent": "employment",
        "expected_osb_id": 305,
        "expected_answer_contains": ["2587"],
    },

    {
        "query": "Malatya-Güney OSB'de üretimde kaç parsel var?",
        "expected_status": "success",
        "expected_intent": "employment",
        "expected_osb_id": 305,
        "expected_answer_contains": ["21"],
    },

    # --------------------------------------------------------
    # GENEL BİLGİ
    # --------------------------------------------------------

    {
        "query": "Malatya-Güney OSB hangi ilde?",
        "expected_status": "success",
        "expected_intent": "general",
        "expected_osb_id": 305,
        "expected_answer_contains": ["Malatya"],
    },

    {
        "query": "Malatya-Güney OSB'nin ilçesi nedir?",
        "expected_status": "success",
        "expected_intent": "general",
        "expected_osb_id": 305,
        "expected_answer_contains": ["Güney"],
    },

    {
        "query": "Malatya-Güney OSB'nin türü nedir?",
        "expected_status": "success",
        "expected_intent": "general",
        "expected_osb_id": 305,
        "expected_answer_contains": ["Karma"],
    },

    {
        "query": "Malatya-Güney OSB kaçıncı teşvik bölgesinde?",
        "expected_status": "success",
        "expected_intent": "general",
        "expected_osb_id": 305,
        "expected_answer_contains": ["5", "teşvik bölgesinde", ],
    },

    # --------------------------------------------------------
    # SEKTÖR
    # --------------------------------------------------------

    {
        "query": "Malatya-Güney OSB'de hangi sektör bulunuyor?",
        "expected_status": "success",
        "expected_intent": "sector",
        "expected_osb_id": 305,
        "expected_answer_contains": [
            "GIDA ÜRÜNLERİ İMALATI"
        ],
    },

    {
        "query": "Malatya-Güney OSB'de NC kodu 10 olan sektör nedir?",
        "expected_status": "success",
        "expected_intent": "sector",
        "expected_osb_id": 305,
        "expected_answer_contains": [
            "GIDA ÜRÜNLERİ İMALATI"
        ],
    },

    # --------------------------------------------------------
    # AMBIGUOUS
    # --------------------------------------------------------

    {
        "query": "Malatya OSB'de kaç boş parsel var?",
        "expected_status": "ambiguous",
        "expected_intent": "parcel",
        "expected_osb_id": None,
        "expected_llm_called": False,
    },

    {
        "query": "Malatya OSB hangi bölgede?",
        "expected_status": "ambiguous",
        "expected_intent": "general",
        "expected_osb_id": None,
        "expected_llm_called": False,
    },

    # --------------------------------------------------------
    # NOT FOUND
    # --------------------------------------------------------

    {
        "query": "Hayalşehir OSB'de kaç fabrika var?",
        "expected_status": "not_found",
        "expected_osb_id": None,
        "expected_llm_called": False,
    },

    {
        "query": "Testşehir OSB deprem bölgesinde mi?",
        "expected_status": "not_found",
        "expected_osb_id": None,
        "expected_llm_called": False,
    },
]


# ============================================================
# TEST RUNNER
# ============================================================

def run_test(
    pipeline: RAGPipeline,
    test_case: dict,
) -> tuple[bool, list[str]]:

    errors = []

    query = test_case["query"]

    result = pipeline.ask(query)

    retrieval = result["retrieval"]
    answer_result = result["answer"]

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    actual_status = retrieval.get("status")
    expected_status = test_case["expected_status"]

    if actual_status != expected_status:
        errors.append(
            f"status beklenen={expected_status}, "
            f"gerçek={actual_status}"
        )

    # --------------------------------------------------------
    # INTENT
    # --------------------------------------------------------

    actual_intent = retrieval.get("intent")
    expected_intent = test_case.get("expected_intent")

    if (
        expected_intent is not None
        and actual_intent != expected_intent
    ):
        errors.append(
            f"intent beklenen={expected_intent}, "
            f"gerçek={actual_intent}"
        )

    # --------------------------------------------------------
    # OSB ID
    # --------------------------------------------------------

    actual_osb_id = retrieval.get("osb_id")
    expected_osb_id = test_case.get("expected_osb_id")

    if actual_osb_id != expected_osb_id:
        errors.append(
            f"osb_id beklenen={expected_osb_id}, "
            f"gerçek={actual_osb_id}"
        )

    # --------------------------------------------------------
    # LLM CALLED
    # --------------------------------------------------------

    if "expected_llm_called" in test_case:

        actual_llm_called = answer_result.get(
            "llm_called"
        )

        if (
            actual_llm_called
            != test_case["expected_llm_called"]
        ):
            errors.append(
                "llm_called "
                f"beklenen={test_case['expected_llm_called']}, "
                f"gerçek={actual_llm_called}"
            )

    # --------------------------------------------------------
    # ANSWER CONTENT
    # --------------------------------------------------------

    expected_strings = test_case.get(
        "expected_answer_contains",
        [],
    )

    answer = answer_result.get(
        "answer",
        "",
    )

    for expected_string in expected_strings:

        if expected_string.lower() not in answer.lower():

            errors.append(
                f"cevap içinde '{expected_string}' "
                "bulunamadı"
            )

    return len(errors) == 0, errors


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("RAG EVALUATION")
    print("=" * 70)

    pipeline = RAGPipeline()

    total = len(TEST_CASES)
    passed = 0
    failed = 0

    results = []

    for index, test_case in enumerate(
        TEST_CASES,
        start=1,
    ):

        query = test_case["query"]

        print("\n" + "-" * 70)
        print(f"TEST {index}/{total}")
        print(f"Soru: {query}")

        success, errors = run_test(
            pipeline,
            test_case,
        )

        if success:

            passed += 1

            print("SONUÇ: ✅ PASS")

        else:

            failed += 1

            print("SONUÇ: ❌ FAIL")

            for error in errors:
                print(f"  - {error}")

        results.append(
            {
                "query": query,
                "passed": success,
                "errors": errors,
            }
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    accuracy = (
        passed / total * 100
        if total
        else 0
    )

    print("\n" + "=" * 70)
    print("EVALUATION SONUCU")
    print("=" * 70)

    print(f"Toplam test : {total}")
    print(f"Başarılı    : {passed}")
    print(f"Başarısız   : {failed}")
    print(f"Başarı oranı: %{accuracy:.2f}")

    print("=" * 70)

    if failed == 0:

        print(
            "🎉 TÜM RAG TESTLERİ BAŞARILI!"
        )

    else:

        print(
            "⚠️ Bazı testler başarısız."
        )


if __name__ == "__main__":
    main()