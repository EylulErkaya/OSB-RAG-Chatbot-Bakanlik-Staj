from typing import Any


# ============================================================
# CONTEXT BUILDER
# ============================================================

class ContextBuilder:
    """
    Retrieval sonuçlarını LLM'e gönderilebilecek
    güvenli ve düzenli bir context'e dönüştürür.

    Bu sınıf:
        - ambiguous / not_found durumlarını LLM'den uzak tutar
        - retrieval sonuçlarını temizler
        - metadata bilgilerini kullanır
        - eksik verileri context'e yanlış değer olarak koymaz
        - gerçek sektör adını retrieval metadata'sından alır
    """

    def build(self, retrieval_result: dict[str, Any]) -> dict[str, Any]:

        status = retrieval_result.get("status")
        
        # ====================================================
        # AMBIGUOUS
        # ====================================================

        if status == "ambiguous":

            candidates = retrieval_result.get(
                "candidates",
                []
            )

            return {
                "status": "ambiguous",
                "context": "",
                "llm_allowed": False,
                "message": self._build_ambiguous_message(
                    candidates
                ),
            }

        # ====================================================
        # NOT FOUND
        # ====================================================

        if status == "not_found":

            return {
                "status": "not_found",
                "context": "",
                "llm_allowed": False,
                "message": (
                    "Belirtilen OSB veri kaynağında "
                    "bulunamadı."
                ),
            }
            
            
        # ====================================================
        # LISTING
        # ====================================================

        if status == "listing":

            return self._build_listing_context(
                retrieval_result
            )

        # ====================================================
        # STRUCTURED AGGREGATION
        # ====================================================

        if status == "aggregation":

            return self._build_aggregation_context(
                retrieval_result
            )

        # ====================================================
        # BEKLENMEYEN DURUM
        # ====================================================

        if status != "success":

            return {
                "status": "error",
                "context": "",
                "llm_allowed": False,
                "message": (
                    "Retrieval işlemi başarılı "
                    "şekilde tamamlanamadı."
                ),
            }

        # ====================================================
        # SONUÇLAR
        # ====================================================

        results = retrieval_result.get(
            "results",
            []
        )

        if not results:

            return {
                "status": "no_results",
                "context": "",
                "llm_allowed": False,
                "message": (
                    "Soruyla ilişkili kaynak "
                    "bilgisi bulunamadı."
                ),
            }

        # ====================================================
        # CONTEXT OLUŞTUR
        # ====================================================

        context_blocks = []

        for index, result in enumerate(
            results,
            start=1
        ):

            block = self._build_result_block(
                result,
                index
            )

            if block:
                context_blocks.append(block)

        # ====================================================
        # HİÇBİR GEÇERLİ CONTEXT YOK
        # ====================================================

        if not context_blocks:

            return {
                "status": "no_valid_context",
                "context": "",
                "llm_allowed": False,
                "message": (
                    "Kaynaklarda kullanılabilir "
                    "bir bilgi bulunamadı."
                ),
            }

        # ====================================================
        # FINAL CONTEXT
        # ====================================================

        context = "\n\n".join(
            context_blocks
        )

        return {
            "status": "success",
            "context": context,
            "llm_allowed": True,
            "message": None,
            "context_osb_source": retrieval_result.get("context_osb_source"),
        }

    # ========================================================
    # RESULT BLOCK
    # ========================================================

    def _build_result_block(
        self,
        result: dict[str, Any],
        index: int,
    ) -> str | None:

        metadata = result.get(
            "metadata",
            {}
        )

        document = (
            result.get("document")
            or ""
        ).strip()

        chunk_type = metadata.get(
            "chunk_type"
        )

        # ====================================================
        # SECTOR
        # ====================================================

        if chunk_type == "sector":

            return self._build_sector_block(
                metadata,
                document,
                index
            )

        # ====================================================
        # OSB PARCEL
        # ====================================================

        if chunk_type == "osb_parcel":

            return self._build_osb_parcel_block(
                metadata,
                document,
                index
            )

        # ====================================================
        # OSB EMPLOYMENT
        # ====================================================

        if chunk_type == "osb_employment":

            return self._build_osb_employment_block(
                metadata,
                document,
                index
            )

        # ====================================================
        # OSB BASIC
        # ====================================================

        if chunk_type == "osb_basic":

            return self._build_osb_basic_block(
                metadata,
                document,
                index
            )

        # ====================================================
        # FALLBACK
        # ====================================================

        if document:

            return (
                f"[Kaynak {index}]\n"
                f"{document}"
            )

        return None

    # ========================================================
    # SECTOR CONTEXT
    # ========================================================

    def _build_sector_block(
        self,
        metadata: dict[str, Any],
        document: str,
        index: int,
    ) -> str:

        osb_name = metadata.get(
            "osb_adi",
            "Bilinmiyor"
        )

        sector_name = metadata.get(
            "sektor_adi"
        )

        # Gerçek sektör adı metadata'dan alınır.
        if not sector_name:

            sector_name = (
                "Sektör adı kaynak metadata'sında "
                "bulunmamaktadır."
            )

        nc = metadata.get("nc")
        ps = metadata.get("ps")
        fs = metadata.get("fs")
        employment = metadata.get(
            "istihdam"
        )

        lines = [
            f"[Kaynak {index}]",
            f"OSB: {osb_name}",
            f"Sektör: {sector_name}",
        ]

        self._add_value(
            lines,
            "NC",
            nc
        )

        self._add_value(
            lines,
            "PS",
            ps
        )

        self._add_value(
            lines,
            "FS",
            fs
        )

        # NaN / None ise kesinlikle değer yazılmaz.
        if self._is_missing(employment):

            lines.append(
                "İstihdam: "
                "Bu sektör için kayıtlı istihdam "
                "verisi bulunmamaktadır."
            )

        else:

            self._add_value(
                lines,
                "İstihdam",
                employment
            )

        return "\n".join(lines)

    # ========================================================
    # PARCEL CONTEXT
    # ========================================================

    def _build_osb_parcel_block(
        self,
        metadata: dict[str, Any],
        document: str,
        index: int,
    ) -> str:

        return (
            f"[Kaynak {index}]\n"
            f"{document}"
        )

    # ========================================================
    # EMPLOYMENT CONTEXT
    # ========================================================

    def _build_osb_employment_block(
        self,
        metadata: dict[str, Any],
        document: str,
        index: int,
    ) -> str:

        return (
            f"[Kaynak {index}]\n"
            f"{document}"
        )

    # ========================================================
    # BASIC CONTEXT
    # ========================================================

    def _build_osb_basic_block(
        self,
        metadata: dict[str, Any],
        document: str,
        index: int,
    ) -> str:

        return (
            f"[Kaynak {index}]\n"
            f"{document}"
        )

    # ========================================================
    # VALUE
    # ========================================================

    @staticmethod
    def _add_value(
        lines: list[str],
        label: str,
        value: Any,
    ) -> None:

        if ContextBuilder._is_missing(value):
            return

        lines.append(
            f"{label}: "
            f"{ContextBuilder._clean_value(value)}"
        )

    # ========================================================
    # MISSING VALUE
    # ========================================================

    @staticmethod
    def _is_missing(value: Any) -> bool:

        if value is None:
            return True

        try:
            return bool(value != value)
        except Exception:
            return False

    # ========================================================
    # VALUE CLEANING
    # ========================================================

    @staticmethod
    def _clean_value(value: Any) -> Any:

        if isinstance(value, float):

            if value.is_integer():
                return int(value)

        return value

    # ========================================================
    # AMBIGUOUS MESSAGE
    # ========================================================

    @staticmethod
    def _build_ambiguous_message(
        candidates: list[dict[str, Any]]
    ) -> str:

        if not candidates:

            return (
                "Birden fazla OSB kaydı bulundu. "
                "Lütfen hangi OSB'yi kastettiğinizi belirtin."
            )

        lines = [
            "Birden fazla OSB kaydı bulundu.",
            "Lütfen hangisini kastettiğinizi seçin:",
            "",
        ]

        for index, candidate in enumerate(
            candidates,
            start=1
        ):

            name = candidate.get(
                "name",
                "Bilinmeyen OSB"
            )
            

            city = candidate.get(
                "city"
            )

            district = candidate.get(
                "district"
            )
            
            osb_type = candidate.get("osb_type")
            sicil_no = candidate.get("sicil_no")
            kurulus_yili = candidate.get("kurulus_yili")

            if city and district:
                lines.append(
                    f"{index}. {name} "
                    f"— {city} / {district}"
                )

            if osb_type:
                lines.append(
                    f"   Tür: {osb_type}"
                )

            if sicil_no:
                lines.append(
                    f"   Sicil No: {sicil_no}"
                )

            if kurulus_yili:
                lines.append(
                    f"   Kuruluş Yılı: {kurulus_yili}"
                )

            elif city:

                lines.append(
                    f"{index}. {name} "
                    f"— {city}"
                )

            else:

                lines.append(
                    f"{index}. {name}"
                )

        lines.append("")

        lines.append(
            f"Lütfen 1-{len(candidates)} "
            "arasında bir seçim yapın."
        )

        return "\n".join(lines)
    
        # ========================================================
    # LISTING CONTEXT
    # ========================================================

    def _build_listing_context(
        self,
        retrieval_result: dict[str, Any],
    ) -> dict[str, Any]:

        results = retrieval_result.get(
            "results",
            []
        )

        total_count = retrieval_result.get(
            "total_count",
            0
        )

        limit = retrieval_result.get(
            "limit",
            10
        )

        offset = retrieval_result.get(
            "offset",
            0
        )

        returned_count = retrieval_result.get(
            "returned_count",
            len(results)
        )

        # ====================================================
        # SONUÇ YOK
        # ====================================================

        if not results:

            return {
                "status": "listing",
                "context": "",
                "llm_allowed": False,
                "message": (
                    "Belirtilen filtrelere uygun "
                    "OSB bulunamadı."
                ),
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "returned_count": returned_count,
            }

        # ====================================================
        # LISTING CONTEXT
        # ====================================================

        context_blocks = []

        for index, result in enumerate(
            results,
            start=offset + 1
        ):

            name = result.get(
                "name",
                "Bilinmeyen OSB"
            )

            city = result.get("city")
            district = result.get("district")
            region = result.get("region")
            osb_type = result.get("type")
            stage = result.get("stage")

            lines = [
                f"[OSB {index}]",
                f"OSB: {name}",
            ]

            if city:
                lines.append(
                    f"İl: {city}"
                )

            if district:
                lines.append(
                    f"İlçe: {district}"
                )

            if region:
                lines.append(
                    f"Bölge: {region}"
                )

            if osb_type:
                lines.append(
                    f"OSB Türü: {osb_type}"
                )

            if stage:
                lines.append(
                    f"Aşama: {stage}"
                )

            context_blocks.append(
                "\n".join(lines)
            )

        # ====================================================
        # PAGINATION BİLGİSİ
        # ====================================================

        pagination_info = (
            f"Toplam OSB sayısı: {total_count}\n"
            f"Bu yanıtta gösterilen kayıt sayısı: "
            f"{returned_count}\n"
            f"Başlangıç konumu: {offset}\n"
            f"Sayfa limiti: {limit}"
        )

        context = (
            pagination_info
            + "\n\n"
            + "\n\n".join(context_blocks)
        )

        return {
            "status": "listing",
            "context": context,
            "llm_allowed": True,
            "message": None,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "returned_count": returned_count,
        }

    def _build_aggregation_context(
        self,
        retrieval_result: dict[str, Any],
    ) -> dict[str, Any]:
        aggregation = retrieval_result.get("aggregation", {})

        if aggregation.get("status") != "success":
            filters = aggregation.get("filters", {})
            location = filters.get("city") or filters.get("region") or "belirtilen filtreler"
            return {
                "status": "not_found",
                "context": "",
                "llm_allowed": False,
                "message": f"{location} için eşleşen OSB kaydı bulunamadı.",
            }

        filters = aggregation.get("filters", {})
        location_lines = []
        labels = {
            "city": "Şehir",
            "district": "İlçe",
            "region": "Bölge",
            "osb_type": "OSB Türü",
            "stage": "Aşama",
            "investment_program": "Yatırım Programı",
            "earthquake_region": "Deprem Bölgesi",
            "incentive_region": "Teşvik Bölgesi",
        }
        for key, label in labels.items():
            if filters.get(key):
                location_lines.append(f"{label}: {filters[key]}")

        operation = "Toplam" if aggregation.get("operation") == "sum" else "Sayı"
        metric = aggregation.get("metric") or "OSB Sayısı"
        total = aggregation.get("formatted_total")
        context_lines = [
            "AGGREGATION RESULT",
            *location_lines,
            f"İşlem: {operation}",
            f"Metrik: {metric}",
            f"Eşleşen OSB sayısı: {aggregation.get('matched_count', 0)}",
            f"Geçerli veri sayısı: {aggregation.get('valid_count', 0)}",
            f"Eksik veri sayısı: {aggregation.get('missing_count', 0)}",
            f"Hazır sonuç: {total}",
            "Bu sayıyı kendin hesaplama; hazır sonucu değiştirmeden kullan.",
        ]

        return {
            "status": "aggregation",
            "context": "\n".join(context_lines),
            "llm_allowed": True,
            "message": None,
        }
