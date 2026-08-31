"""
Field resolution and selection tests for OSB RAG Chatbot.
"""

from src.retrieval.field_resolver import detect_requested_field
from src.retrieval.query_intent import detect_intent
from src.generation.rag_pipeline import RAGPipeline


def test_field_detection_1_evrak_kayit_tarihi_full():
    field = detect_requested_field("Tekirdağ OSB evrak kayıt tarihi")
    assert field == "Evrak Kayıt Tarihi"


def test_field_detection_2_kayit_tarihi_short():
    field = detect_requested_field("Tekirdağ OSB kayıt tarihi")
    assert field == "Evrak Kayıt Tarihi"


def test_field_detection_3_turu():
    field = detect_requested_field("Tekirdağ OSB türü")
    assert field == "OSB Türü"


def test_field_detection_4_sektoru():
    field = detect_requested_field("Tekirdağ OSB sektörü")
    assert field == "OSB Türü"


def test_field_detection_5_hangi_bolgede():
    field = detect_requested_field("Tekirdağ OSB hangi bölgede")
    assert field == "Bölge"


def test_field_detection_6_kurulus_tarihi():
    field = detect_requested_field("Tekirdağ OSB kuruluş tarihi")
    assert field == "OSB Kuruluş Tarihi"


def test_field_detection_7_sicil_numarasi():
    field = detect_requested_field("Tekirdağ OSB sicil numarası")
    assert field == "Sicil No"


def test_field_detection_8_kac_hektar():
    field = detect_requested_field("Tekirdağ OSB kaç hektar")
    assert field == "Bölge Büyüklüğü (Ha)"


def test_ambiguous_tekirdag_selection_3_evrak_kayit_tarihi():
    pipeline = RAGPipeline()
    res1 = pipeline.ask("Tekirdağ OSB evrak kayıt tarihi")
    assert res1["retrieval"]["status"] == "ambiguous"

    res2 = pipeline.ask("3")
    assert res2["retrieval"]["status"] == "success"
    answer = res2["answer"]["answer"]
    assert "2026-06-18" in answer or "18 Haziran 2026" in answer or "2026" in answer


def test_ambiguous_tekirdag_selection_3_osb_turu():
    pipeline = RAGPipeline()
    res1 = pipeline.ask("Tekirdağ OSB türü")
    assert res1["retrieval"]["status"] == "ambiguous"

    res2 = pipeline.ask("3")
    assert res2["retrieval"]["status"] == "success"
    answer = res2["answer"]["answer"]
    assert "Tarıma Dayalı" in answer or "tarıma dayalı" in answer.lower()


def test_ambiguous_tekirdag_selection_3_bolge():
    pipeline = RAGPipeline()
    res1 = pipeline.ask("Tekirdağ OSB hangi bölgede")
    assert res1["retrieval"]["status"] in ["success", "ambiguous"]
    if res1["retrieval"]["status"] == "ambiguous":
        res2 = pipeline.ask("3")
        answer = res2["answer"]["answer"]
    else:
        answer = res1["answer"]["answer"]
    assert "Marmara" in answer


def test_specific_gida_sector_intent_preserved():
    intent_res = detect_intent("Tekirdağ OSB'de gıda sektöründe kaç kişi çalışıyor?")
    assert intent_res["intent"] in ["sector", "employment"]

    pipeline = RAGPipeline()
    res = pipeline.ask("gıda sektöründe kaç kişi çalışıyor?")
    # Sektör intent'i bozulmamalı
    assert res["retrieval"]["intent"] == "sector" or res["retrieval"]["intent"] == "employment"


def test_field_detection_parsel_birim_fiyati():
    field = detect_requested_field("Tekirdağ OSB parsel birim fiyatı")
    assert field == "Parsel Birim Fiyat\n(m­²)"


def test_ambiguous_tekirdag_selection_3_parsel_birim_fiyati():
    pipeline = RAGPipeline()
    res1 = pipeline.ask("Tekirdağ OSB parsel birim fiyatı nedir?")
    assert res1["retrieval"]["status"] == "ambiguous"

    res2 = pipeline.ask("3")
    assert res2["retrieval"]["status"] == "success"
    answer = res2["answer"]["answer"]
    assert "1400" in answer

