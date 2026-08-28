"""Tests for structured ranking/comparison queries."""

import pytest
from src.retrieval.query_intent import detect_intent
from src.generation.rag_pipeline import RAGPipeline


def test_ranking_intent_detection():
    assert detect_intent("Elazığ'da en fazla istihdam sağlayan OSB hangisidir?")["intent"] == "ranking"
    assert detect_intent("Elazığ'da en fazla boş parsele sahip OSB hangisidir?")["intent"] == "ranking"
    assert detect_intent("Adana'da en fazla fabrikaya sahip OSB hangisidir?")["intent"] == "ranking"
    assert detect_intent("Malatya'daki en eski OSB hangisidir?")["intent"] == "ranking"


def test_ranking_regression_intents():
    # Single OSB intent must remain single OSB
    assert detect_intent("Siirt OSB'deki toplam istihdam kaçtır?")["intent"] == "employment"
    assert detect_intent("Malatya-Güney OSB'de kaç parsel vardır?")["intent"] == "parcel"
    assert detect_intent("Adana OSB'nin kuruluş yılı nedir?")["intent"] == "general"

    # Multi OSB aggregation intent must remain aggregation
    assert detect_intent("Elazığ'daki OSB'lerin toplam istihdamı kaçtır?")["intent"] == "aggregation"
    assert detect_intent("Elazığ'da kaç OSB var?")["intent"] == "aggregation"


def test_ranking_pipeline_execution():
    pipeline = RAGPipeline()

    # 1. En fazla istihdam
    res1 = pipeline.ask("Elazığ'da en fazla istihdam sağlayan OSB hangisidir?")
    assert res1["retrieval"]["status"] == "ranking"
    assert res1["answer"]["status"] == "success"
    assert "Elazığ" in res1["answer"]["answer"]

    # 2. En fazla boş parsel
    res2 = pipeline.ask("Elazığ'da en fazla boş parsele sahip OSB hangisidir?")
    assert res2["retrieval"]["status"] == "ranking"
    assert res2["answer"]["status"] == "success"

    # 3. En fazla fabrika
    res3 = pipeline.ask("Adana'da en fazla fabrikaya sahip OSB hangisidir?")
    assert res3["retrieval"]["status"] == "ranking"
    assert res3["answer"]["status"] == "success"
    assert "Adana" in res3["answer"]["answer"]

    # 4. En eski OSB
    res4 = pipeline.ask("Malatya'daki en eski OSB hangisidir?")
    assert res4["retrieval"]["status"] == "ranking"
    assert res4["answer"]["status"] == "success"
    assert "Malatya" in res4["answer"]["answer"]


if __name__ == "__main__":
    test_ranking_intent_detection()
    test_ranking_regression_intents()
    test_ranking_pipeline_execution()
    print("Tüm ranking testleri başarılı!")
