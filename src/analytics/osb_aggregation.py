"""Deterministic aggregations over normalized OSB data."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.retrieval.osb_resolver import filter_osbs


METRIC_ALIASES = {
    "toplam istihdam": "Toplam İstihdam",
    "istihdam": "İstihdam",
    "çalışan": "İstihdam",
    "üretimdeki toplam fabrika sayısı": "Üretimdeki Toplam Fabrika Sayısı",
    "üretimde kaç fabrika": "Üretimdeki Toplam Fabrika Sayısı",
    "fabrika": "Üretimdeki Toplam Fabrika Sayısı",
    "boş parsel": "Boş Parsel Sayısı",
    "toplam parsel": "Toplam Parsel Sayısı (Bölge ve Öngörü)",
    "üretimdeki toplam parsel sayısı": "Üretimdeki Toplam Parsel Sayısı",
    "üretimde kaç parsel": "Üretimdeki Toplam Parsel Sayısı",
}


def resolve_metric(query: str) -> str | None:
    """Map supported user wording to a verified CSV column name."""

    normalized = query.strip().lower()
    for phrase in sorted(METRIC_ALIASES, key=len, reverse=True):
        if phrase in normalized:
            return METRIC_ALIASES[phrase]
    return None


def format_turkish_number(value: int | float) -> str:
    """Format a number deterministically using Turkish separators."""

    numeric = float(value)
    if numeric.is_integer():
        return f"{int(numeric):,}".replace(",", ".")

    formatted = f"{numeric:,.2f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def aggregate_osbs(
    *,
    city: str | None = None,
    district: str | None = None,
    region: str | None = None,
    osb_type: str | None = None,
    stage: str | None = None,
    investment_program: str | None = None,
    earthquake_region: str | None = None,
    incentive_region: str | None = None,
    metric: str | None = None,
    operation: str = "sum",
) -> dict[str, Any]:
    """Aggregate filtered OSB data without vector retrieval or an LLM."""

    if operation not in {"sum", "count"}:
        raise ValueError(f"Desteklenmeyen aggregation işlemi: {operation}")

    filtered = filter_osbs(
        city=city,
        district=district,
        region=region,
        osb_type=osb_type,
        stage=stage,
        investment_program=investment_program,
        earthquake_region=earthquake_region,
        incentive_region=incentive_region,
    )
    matched_count = len(filtered)

    result: dict[str, Any] = {
        "status": "success" if matched_count else "not_found",
        "operation": operation,
        "metric": metric,
        "total": None,
        "formatted_total": None,
        "matched_count": matched_count,
        "valid_count": matched_count if operation == "count" else 0,
        "missing_count": 0,
        "filters": {
            "city": city,
            "district": district,
            "region": region,
            "osb_type": osb_type,
            "stage": stage,
            "investment_program": investment_program,
            "earthquake_region": earthquake_region,
            "incentive_region": incentive_region,
        },
    }

    if operation == "count":
        result["total"] = matched_count
        result["formatted_total"] = format_turkish_number(matched_count)
        return result

    if metric not in filtered.columns:
        return {**result, "status": "invalid_metric"}

    values = pd.to_numeric(filtered[metric], errors="coerce")
    valid_count = int(values.notna().sum())
    total = values.sum()
    result.update(
        total=total.item() if hasattr(total, "item") else total,
        formatted_total=format_turkish_number(total),
        valid_count=valid_count,
        missing_count=matched_count - valid_count,
    )
    return result
