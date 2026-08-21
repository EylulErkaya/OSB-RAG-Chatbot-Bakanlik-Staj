import pandas as pd


def compare_candidate_field(candidates, field):
    """
    Birden fazla OSB adayının aynı alanındaki değerleri karşılaştırır.

    Sonuç:
        same      -> tüm adayların değeri aynı
        different -> adayların değerleri farklı
        missing   -> alan bulunamadı
    """

    values = []

    for candidate in candidates:
        value = candidate.get(field)

        if value is None:
            value = ""

        values.append(str(value).strip())

    if not values:
        return {
            "status": "missing",
            "values": []
        }

    unique_values = list(dict.fromkeys(values))

    if len(unique_values) == 1:
        return {
            "status": "same",
            "value": unique_values[0],
            "values": values
        }

    return {
        "status": "different",
        "values": values
    }