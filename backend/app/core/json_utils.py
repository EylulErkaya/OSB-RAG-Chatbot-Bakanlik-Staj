import math
from datetime import date, datetime
from typing import Any

import pandas as pd


def sanitize_for_json(value: Any) -> Any:
    """
    JSON/JSONB kolonlarına yazılmadan önce veriyi temizler.

    NaN, NaT ve Infinity değerlerini None'a çevirir.
    Dict ve list yapılarında recursive olarak çalışır.
    """

    if isinstance(value, dict):
        return {
            key: sanitize_for_json(val)
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [
            sanitize_for_json(item)
            for item in value
        ]

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None

        return value

    # pandas.isna numpy scalar'larını, pandas.NA'yı ve NaT'yi de kapsar.
    # Koleksiyon değerlerinde belirsiz boolean sonucu verebildiği için, bu
    # kontrolden önce dict/list olarak recursive işlenir.
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    # numpy scalar'ları (örn. int64/float32) standart Python değerlerine
    # dönüştürerek JSON encoder'ın kabul ettiği tipe indirger.
    item = getattr(value, "item", None)
    if callable(item):
        try:
            normalized_value = item()
        except ValueError:
            normalized_value = value

        if normalized_value is not value:
            return sanitize_for_json(normalized_value)

    return value
