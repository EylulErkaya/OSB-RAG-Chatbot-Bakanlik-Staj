import json

from backend.app.core.json_utils import sanitize_for_json
import numpy as np
import pandas as pd


def main():
    data = {
        "normal": 123,
        "nan_value": float("nan"),
        "positive_inf": float("inf"),
        "negative_inf": float("-inf"),
        "numpy_nan": np.float32("nan"),
        "pandas_na": pd.NA,
        "nat": pd.NaT,
        "numpy_integer": np.int64(7),
        "nested": {
            "value": float("nan")
        },
        "list": [
            1,
            float("nan"),
            {"x": float("inf")}
        ]
    }

    result = sanitize_for_json(data)

    print("Temizlenmiş veri:")
    print(result)

    assert result["normal"] == 123
    assert result["nan_value"] is None
    assert result["positive_inf"] is None
    assert result["negative_inf"] is None
    assert result["numpy_nan"] is None
    assert result["pandas_na"] is None
    assert result["nat"] is None
    assert result["numpy_integer"] == 7
    assert result["nested"]["value"] is None
    assert result["list"][1] is None
    assert result["list"][2]["x"] is None
    json.dumps(result, allow_nan=False)

    print()
    print("✓ JSON sanitizer testi başarılı")


if __name__ == "__main__":
    main()
