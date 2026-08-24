import math
from typing import Any


def sanitize_for_json(value: Any) -> Any:
    """
    JSON/JSONB kolonlarına yazılmadan önce veriyi temizler.

    NaN ve Infinity değerlerini None'a çevirir.
    Dict ve list yapılarında recursive olarak çalışır.
    """

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None

        return value

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

    return value