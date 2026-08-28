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
    "boş parsel sayısı": "Boş Parsel Sayısı",
    "boş parsel": "Boş Parsel Sayısı",
    "imar parsel sayısı": "Parsel Sayısı (İmar)",
    "imar parsel": "Parsel Sayısı (İmar)",
    "bölge parsel sayısı": "Parsel Sayısı  (Bölge)",
    "bölge parsel": "Parsel Sayısı  (Bölge)",
    "toplam parsel sayısı": "Toplam Parsel Sayısı (Bölge ve Öngörü)",
    "toplam parsel": "Toplam Parsel Sayısı (Bölge ve Öngörü)",
    "öngörü parsel": "Öngörü Parsel",
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


def resolve_ranking_spec(query: str) -> tuple[str, str] | None:
    """Map ranking query wording to (verified CSV column name, MAX|MIN)."""

    normalized = query.strip().lower()

    if "en eski" in normalized:
        return ("OSB Kuruluş Yılı", "MIN")

    if "boş parsel" in normalized or "bos parsel" in normalized:
        return ("Boş Parsel Sayısı", "MAX")

    if "fabrika" in normalized:
        return ("Üretimdeki Toplam Fabrika Sayısı", "MAX")

    if any(kw in normalized for kw in ["istihdam", "çalışan", "calisan", "kişi", "kisi"]):
        return ("Toplam İstihdam", "MAX")

    return None


def rank_osbs(
    *,
    city: str | None = None,
    district: str | None = None,
    region: str | None = None,
    osb_type: str | None = None,
    stage: str | None = None,
    investment_program: str | None = None,
    earthquake_region: str | None = None,
    incentive_region: str | None = None,
    metric: str,
    operation: str = "MAX",
) -> dict[str, Any]:
    """Perform deterministic ranking over filtered OSB data without an LLM."""

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
    op_upper = operation.upper()

    result: dict[str, Any] = {
        "status": "not_found",
        "operation": op_upper,
        "metric": metric,
        "target_value": None,
        "formatted_target_value": None,
        "winners": [],
        "matched_count": matched_count,
        "valid_count": 0,
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

    if matched_count == 0 or metric not in filtered.columns:
        return result

    numeric_vals = pd.to_numeric(filtered[metric], errors="coerce")
    valid_mask = numeric_vals.notna()
    valid_count = int(valid_mask.sum())

    if valid_count == 0:
        return result

    valid_filtered = filtered[valid_mask].copy()
    valid_numeric = numeric_vals[valid_mask]

    if op_upper == "MAX":
        target_val = valid_numeric.max()
    elif op_upper == "MIN":
        target_val = valid_numeric.min()
    else:
        raise ValueError(f"Desteklenmeyen ranking işlemi: {operation}")

    winner_mask = valid_numeric == target_val
    winner_rows = valid_filtered[winner_mask]

    winners = []
    for _, row in winner_rows.iterrows():
        raw_id = row.get("OSB_ID")
        osb_id = int(raw_id) if pd.notna(raw_id) else None
        winners.append(
            {
                "osb_id": osb_id,
                "osb_name": str(row.get("OSB Adı", "")),
                "city": str(row.get("İl Adı", "")),
                "district": str(row.get("İlçe", "")),
                "value": target_val.item() if hasattr(target_val, "item") else target_val,
                "formatted_value": format_turkish_number(target_val),
            }
        )

    result.update(
        status="success",
        target_value=target_val.item() if hasattr(target_val, "item") else target_val,
        formatted_target_value=format_turkish_number(target_val),
        winners=winners,
        valid_count=valid_count,
    )

    return result
