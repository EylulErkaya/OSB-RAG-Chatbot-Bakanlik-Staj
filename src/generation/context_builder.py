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

        names = []

        for candidate in candidates:

            name = candidate.get(
                "name",
                "Bilinmeyen OSB"
            )

            district = candidate.get(
                "district"
            )

            if district:
                names.append(
                    f"{name} ({district})"
                )
            else:
                names.append(name)

        return (
            "Birden fazla OSB kaydı bulundu. "
            "Lütfen hangisini kastettiğinizi belirtin:\n"
            + "\n".join(
                f"- {name}"
                for name in names
            )
        )   