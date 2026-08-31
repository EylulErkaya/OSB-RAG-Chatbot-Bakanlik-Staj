"""
src/retrieval/field_resolver.py

Kullanıcının doğal Türkçe sorgusundan hangi veritabanı / Excel alanını (column name)
istediğini tespit eder ve alan değerlerini esnek şekilde çözer.
"""

from typing import Optional, Any
import pandas as pd


FIELD_MAPPINGS = [
    (
        [
            "evrak kayıt tarihi",
            "evrak kayıt tarihi nedir",
            "evrak tarihi nedir",
            "kayıt tarihi nedir",
            "evrak kayıt tarihi?",
            "evrak tarihi",
            "kayıt tarihi",
        ],
        "Evrak Kayıt Tarihi",
    ),
    (
        [
            "kuruluş yılı kaç",
            "kuruluş yılı nedir",
            "kuruluş yılı",
            "kurulus yili",
            "kaç yılında kuruldu",
            "ne zaman kuruldu",
        ],
        "OSB Kuruluş Yılı",
    ),
    (
        [
            "kuruluş tarihi nedir",
            "kuruluş tarihi",
            "kurulus tarihi",
        ],
        "OSB Kuruluş Tarihi",
    ),
    (
        [
            "hangi bölgede bulunuyor",
            "hangi bölgede",
            "bölgesi neresi",
            "bölge neresi",
            "hangi bölge",
        ],
        "Bölge",
    ),
    (
        [
            "hangi ilde",
            "hangi il",
            "ili nedir",
            "ili ne",
        ],
        "İl Adı",
    ),
    (
        [
            "hangi ilçede",
            "hangi ilçe",
            "ilçesi nedir",
            "ilçesi ne",
        ],
        "İlçe",
    ),
    (
        [
            "teşvik bölgesi",
            "kaçıncı teşvik",
        ],
        "Teşvik Bölgelerine Göre İller",
    ),
    (
        [
            "osb türü",
            "türü nedir",
            "türü ne",
            "hangi tür",
            "sektörü nedir",
            "sektörü ne",
            "sektörü",
        ],
        "OSB Türü",
    ),
    (
        [
            "sicil numarası nedir",
            "sicil numarası",
            "sicil no nedir",
            "sicil no",
            "sicil numarasi",
        ],
        "Sicil No",
    ),
    (
        [
            "kaç hektar",
            "büyüklüğü ne kadar",
            "büyüklüğü kaç",
            "bölge büyüklüğü",
        ],
        "Bölge Büyüklüğü (Ha)",
    ),
    (
        [
            "kaç boş parsel var",
            "kaç boş parsel",
            "boş parsel kaç",
            "boş parsel sayısı",
        ],
        "Boş Parsel Sayısı (n)",
    ),
    (
        [
            "öngörülen istihdam kaç",
            "öngörü istihdam kaç",
            "öngörülen istihdam ne kadar",
            "öngörülen istihdam",
            "öngörü istihdam",
        ],
        "Öngörü İstihdam",
    ),
    (
        [
            "kaç kişi istihdam ediliyor",
            "istihdam sayısı nedir",
            "istihdamı kaç",
            "kaç kişi çalışıyor",
            "istihdam",
        ],
        "İstihdam",
    ),
    (
        [
            "kaç fabrika üretimde",
            "üretimde kaç fabrika var",
            "üretimdeki fabrika sayısı",
            "üretimdeki toplam fabrika sayısı",
            "üretimdeki toplam fabrika",
        ],
        "Üretimdeki Toplam Fabrika Sayısı",
    ),
    (
        [
            "üretimde kaç parsel var",
            "üretimde kaç parsel",
            "üretimdeki parsel sayısı",
            "üretimdeki toplam parsel sayısı",
            "üretimdeki toplam parsel",
        ],
        "Üretimdeki Toplam Parsel Sayısı",
    ),
    (
        [
            "geliş tarihleri",
            "geliş tarihi",
        ],
        "Geliş Tarihleri",
    ),
    (
        [
            "aşama detayı",
        ],
        "Aşama Detayı",
    ),
    (
        [
            "aşama",
            "hangi aşamada",
        ],
        "Aşama",
    ),
]

SPECIFIC_SECTOR_KEYWORDS = [
    "gıda", "gida", "tekstil", "otomotiv", "kimya", "makine", "elektrik", "metal",
    "plastik", "deri", "maden", "ambalaj", "mobilya", "eczacılık", "eczacilik",
]


def detect_requested_field(query: str) -> Optional[str]:
    """
    Kullanıcının sorgusundan hangi OSB alanını istediğini tespit eder.
    """
    if not query:
        return None

    normalized_query = query.lower().strip()

    has_specific_sector = any(kw in normalized_query for kw in SPECIFIC_SECTOR_KEYWORDS)

    for keywords, field_name in FIELD_MAPPINGS:
        if field_name == "OSB Türü" and has_specific_sector:
            continue

        for keyword in keywords:
            if keyword in normalized_query:
                return field_name

    return None


def get_field_value_from_dict(row_data: dict[str, Any], field_name: str) -> Optional[Any]:
    """
    Candidate dictionary veya row dictionary içinden field_name değerini
    esnek sütun eşleme ile (newline, boşluk farklarına karşı korumalı) çeker.
    """
    if not row_data or not field_name:
        return None

    # Exact match first
    if field_name in row_data:
        val = row_data[field_name]
        if val is not None and not pd.isna(val):
            return clean_field_value(val)

    # Normalize key match
    target_key = field_name.replace("\n", " ").strip().lower()
    for key, val in row_data.items():
        norm_key = str(key).replace("\n", " ").strip().lower()
        if norm_key == target_key:
            if val is not None and not pd.isna(val):
                return clean_field_value(val)

    return None


def clean_field_value(val: Any) -> str:
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    return str(val).strip()
