import pandas as pd

from src.analytics.osb_aggregation import aggregate_osbs, resolve_metric
from src.retrieval.osb_resolver import list_osbs
from src.retrieval.query_intent import detect_intent


def test_city_total_employment():
    result = aggregate_osbs(
        city="Elazığ",
        metric="Toplam İstihdam",
        operation="sum",
    )

    assert result["status"] == "success"
    assert result["matched_count"] == 10
    assert result["total"] == 14018
    assert result["formatted_total"] == "14.018"
    assert result["missing_count"] == 0


def test_city_total_empty_parcel():
    result = aggregate_osbs(
        city="Elazığ",
        metric="Boş Parsel Sayısı",
        operation="sum",
    )

    assert result["status"] == "success"
    assert result["total"] == 495


def test_city_factory_count():
    result = aggregate_osbs(
        city="Elazığ",
        metric="Üretimdeki Toplam Fabrika Sayısı",
        operation="sum",
    )

    assert result["status"] == "success"
    assert result["total"] == 148


def test_city_osb_count():
    result = aggregate_osbs(city="Elazığ", operation="count")

    assert result["status"] == "success"
    assert result["total"] == 10
    assert result["valid_count"] == 10


def test_multiple_filters_aggregation():
    result = aggregate_osbs(
        city="Malatya",
        osb_type="Karma",
        earthquake_region="Evet",
        operation="count",
    )
    listed = list_osbs(
        city="Malatya",
        osb_type="Karma",
        earthquake_region="Evet",
        limit=100,
    )

    assert result["total"] == listed["total_count"]


def test_missing_values_guardrail(monkeypatch):
    sample = pd.DataFrame({"Toplam İstihdam": [100, None, 0]})
    monkeypatch.setattr(
        "src.analytics.osb_aggregation.filter_osbs",
        lambda **_filters: sample,
    )

    result = aggregate_osbs(metric="Toplam İstihdam", operation="sum")

    assert result["total"] == 100
    assert result["matched_count"] == 3
    assert result["valid_count"] == 2
    assert result["missing_count"] == 1


def test_unknown_city():
    result = aggregate_osbs(
        city="Olmayanşehir",
        metric="Toplam İstihdam",
        operation="sum",
    )

    assert result["status"] == "not_found"
    assert result["total"] == 0


def test_metric_mapping_uses_verified_column_names():
    assert resolve_metric("toplam istihdam") == "Toplam İstihdam"
    assert resolve_metric("üretimde kaç fabrika") == "Üretimdeki Toplam Fabrika Sayısı"
    assert resolve_metric("boş parsel") == "Boş Parsel Sayısı"
    assert resolve_metric("toplam parsel sayısı") == "Toplam Parsel Sayısı (Bölge ve Öngörü)"
    assert resolve_metric("imar parsel sayısı") == "Parsel Sayısı (İmar)"
    assert resolve_metric("bölge parsel sayısı") == "Parsel Sayısı  (Bölge)"
    assert resolve_metric("öngörü parsel") == "Öngörü Parsel"


def test_existing_single_osb_query_not_broken():
    assert detect_intent(
        "Malatya-Güney OSB'de kaç kişi istihdam ediliyor?"
    )["intent"] == "employment"


def test_single_osb_total_is_not_city_aggregation():
    assert detect_intent(
        "Siirt OSB'deki toplam istihdam kaçtır?"
    )["intent"] == "employment"
    assert detect_intent(
        "Siirt OSB'nin toplam istihdamı kaçtır?"
    )["intent"] == "employment"


def test_plural_city_scope_is_aggregation():
    assert detect_intent(
        "Siirt'teki OSB'lerin toplam istihdamı kaçtır?"
    )["intent"] == "aggregation"
    assert detect_intent(
        "Elazığ'daki OSB'lerde toplam kaç fabrika üretim yapıyor?"
    )["intent"] == "aggregation"


def test_existing_ambiguous_query_not_broken():
    assert detect_intent("Malatya OSB")["intent"] == "general"


def test_existing_listing_not_broken():
    assert detect_intent("Malatya'daki OSB'leri listele")["intent"] == "listing"
    assert detect_intent("Doğu Anadolu'daki OSB'leri listele")["intent"] == "listing"


def test_aggregation_intent():
    assert detect_intent(
        "Elazığ'daki OSB'lerin toplam istihdamı kaçtır?"
    )["intent"] == "aggregation"
    assert detect_intent("Elazığ'da kaç OSB var?")["intent"] == "aggregation"
