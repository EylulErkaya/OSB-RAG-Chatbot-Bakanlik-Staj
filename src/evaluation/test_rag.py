from src.generation.rag_pipeline import RAGPipeline


# ============================================================
# TEST CASES
# ============================================================

TEST_CASES = [

    # ========================================================
    # NORMAL RETRIEVAL
    # ========================================================

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

    # ========================================================
    # SECTOR
    # ========================================================

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

    # ========================================================
    # EK PARSEL TESTLERİ
    # ========================================================

    {
        "query": "Malatya-Güney OSB'de boş parsel alanı kaç hektar?",
        "expected_status": "success",
        "expected_intent": "parcel",
        "expected_osb_id": 305,
        "expected_answer_contains": ["193,86"],
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

    # ========================================================
    # EK İSTİHDAM TESTLERİ
    # ========================================================

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

    # ========================================================
    # GENEL BİLGİ
    # ========================================================

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
        "expected_answer_contains": [
            "5",
            "teşvik bölgesinde",
        ],
    },

    # ========================================================
    # SEKTÖR
    # ========================================================

    {
        "query": "Malatya-Güney OSB'de hangi sektör bulunuyor?",
        "expected_status": "success",
        "expected_intent": "sector",
        "expected_osb_id": 305,
        "expected_answer_contains": [
            "GIDA ÜRÜNLERİ İMALATI",
        ],
    },

    {
        "query": "Malatya-Güney OSB'de NC kodu 10 olan sektör nedir?",
        "expected_status": "success",
        "expected_intent": "sector",
        "expected_osb_id": 305,
        "expected_answer_contains": [
            "GIDA ÜRÜNLERİ İMALATI",
        ],
    },

    # ========================================================
    # AMBIGUOUS
    # ========================================================

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

    {
        "query": "Malatya OSB'de kaç boş parsel var?",
        "expected_status": "ambiguous",
        "expected_intent": "parcel",
        "expected_osb_id": None,
        "expected_llm_called": False,
    },

    {
        "query": "Malatya OSB hangi bölgede?",
        "expected_status": "success",
        "expected_intent": "general",
        "expected_osb_id": None,
        "expected_answer_contains": ["Doğu Anadolu",],
    },

    # ========================================================
    # NOT FOUND
    # ========================================================

    {
        "query": "Olmayanşehir OSB'de kaç boş parsel var?",
        "expected_status": "not_found",
        "expected_intent": "parcel",
        "expected_osb_id": None,
        "expected_llm_called": False,
    },

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
# NORMAL TEST RUNNER
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

    expected_intent = test_case.get(
        "expected_intent"
    )

    actual_intent = retrieval.get(
        "intent"
    )

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

    expected_osb_id = test_case.get(
        "expected_osb_id"
    )

    actual_osb_id = retrieval.get(
        "osb_id"
    )

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

        expected_llm_called = test_case[
            "expected_llm_called"
        ]

        if actual_llm_called != expected_llm_called:

            errors.append(
                "llm_called "
                f"beklenen={expected_llm_called}, "
                f"gerçek={actual_llm_called}"
            )

    # --------------------------------------------------------
    # ANSWER CONTENT
    # --------------------------------------------------------

    expected_strings = test_case.get(
        "expected_answer_contains",
        [],
    )
    
    print(
        f"  Gerçek cevap: {answer_result.get('answer', '')}"
    )

    answer = answer_result.get(
        "answer",
        "",
    )

    for expected_string in expected_strings:

        if (
            expected_string.lower()
            not in answer.lower()
        ):

            errors.append(
                f"cevap içinde '{expected_string}' "
                "bulunamadı"
            )

    return (
        len(errors) == 0,
        errors,
    )


# ============================================================
# AMBIGUOUS SELECTION TEST
# ============================================================

def test_ambiguous_selection() -> tuple[bool, list[str]]:

    errors = []

    pipeline = RAGPipeline()

    # --------------------------------------------------------
    # 1. Ambiguous soru
    # --------------------------------------------------------

    result = pipeline.ask(
        "Malatya OSB'de kaç fabrika üretim yapıyor?"
    )

    retrieval = result["retrieval"]

    if retrieval.get("status") != "ambiguous":
        errors.append(
            "İlk soru ambiguous dönmedi."
        )

        return False, errors

    if not pipeline.pending_query:
        errors.append(
            "pending_query oluşturulmadı."
        )

    if not pipeline.pending_candidates:
        errors.append(
            "pending_candidates oluşturulmadı."
        )

    # --------------------------------------------------------
    # 2. Kullanıcı 1'i seçiyor
    # --------------------------------------------------------

    selection_result = pipeline.ask("1")

    selection_retrieval = (
        selection_result["retrieval"]
    )

    if selection_retrieval.get("status") != "success":
        errors.append(
            "Numaralı seçim sonrası "
            "retrieval success olmadı."
        )

    selected_osb = selection_result.get(
        "selected_osb"
    )

    if not selected_osb:
        errors.append(
            "selected_osb bulunamadı."
        )

    else:

        if (
            selection_retrieval.get("osb_id")
            != selected_osb.get("id")
        ):
            errors.append(
                "Seçilen OSB ID ile retrieval "
                "OSB ID eşleşmiyor."
            )

        if (
            selection_retrieval.get("osb_name")
            != selected_osb.get("name")
        ):
            errors.append(
                "Seçilen OSB adı ile retrieval "
                "OSB adı eşleşmiyor."
            )

    # --------------------------------------------------------
    # 3. State temizliği
    # --------------------------------------------------------

    if pipeline.pending_query is not None:
        errors.append(
            "Seçim sonrasında pending_query "
            "temizlenmedi."
        )

    if pipeline.pending_candidates:
        errors.append(
            "Seçim sonrasında pending_candidates "
            "temizlenmedi."
        )

    return (
        len(errors) == 0,
        errors,
    )


# ============================================================
# INVALID SELECTION TEST
# ============================================================

def test_invalid_selection() -> tuple[bool, list[str]]:

    errors = []

    pipeline = RAGPipeline()

    # Önce ambiguous state oluştur
    result = pipeline.ask(
        "Malatya OSB'de kaç fabrika üretim yapıyor?"
    )

    if result["retrieval"].get(
        "status"
    ) != "ambiguous":

        errors.append(
            "Invalid selection testi için "
            "ambiguous state oluşturulamadı."
        )

        return False, errors

    # Geçersiz seçim
    invalid_result = pipeline.ask("99")

    retrieval = invalid_result["retrieval"]

    if retrieval.get(
        "status"
    ) != "selection_error":

        errors.append(
            "Geçersiz seçim "
            "selection_error döndürmedi."
        )

    if invalid_result["answer"].get(
        "llm_called"
    ):
        errors.append(
            "Geçersiz seçimde LLM çağrıldı."
        )

    # State korunmalı
    if not pipeline.pending_query:
        errors.append(
            "Geçersiz seçimden sonra "
            "pending_query kayboldu."
        )

    if not pipeline.pending_candidates:
        errors.append(
            "Geçersiz seçimden sonra "
            "pending_candidates kayboldu."
        )

    return (
        len(errors) == 0,
        errors,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("RAG EVALUATION")
    print("=" * 70)

    total = len(TEST_CASES)
    passed = 0
    failed = 0

    # --------------------------------------------------------
    # NORMAL TESTLER
    # --------------------------------------------------------

    for index, test_case in enumerate(
        TEST_CASES,
        start=1,
    ):

        # Her test bağımsız pipeline
        pipeline = RAGPipeline()

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

    # --------------------------------------------------------
    # AMBIGUOUS SELECTION
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("AMBIGUOUS SELECTION TEST")

    success, errors = test_ambiguous_selection()

    if success:

        passed += 1
        print("SONUÇ: ✅ PASS")

    else:

        failed += 1
        print("SONUÇ: ❌ FAIL")

        for error in errors:
            print(f"  - {error}")

    # --------------------------------------------------------
    # INVALID SELECTION
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("INVALID SELECTION TEST")

    success, errors = test_invalid_selection()

    if success:

        passed += 1
        print("SONUÇ: ✅ PASS")

    else:

        failed += 1
        print("SONUÇ: ❌ FAIL")

        for error in errors:
            print(f"  - {error}")

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    total_tests = passed + failed

    print("\n" + "=" * 70)
    print("TEST SONUÇLARI")
    print("=" * 70)

    print(f"Toplam test : {total_tests}")
    print(f"Başarılı    : {passed}")
    print(f"Başarısız   : {failed}")

    if failed == 0:

        print("\n🎉 TÜM RAG TESTLERİ BAŞARILI!")

    else:

        print(
            "\n⚠️ Bazı RAG testleri başarısız."
        )

        raise SystemExit(1)


if __name__ == "__main__":
    main()