from __future__ import annotations

import math
from typing import Any, Optional


def safe_int(v: Any, default: int = 0) -> int:
    try:
        if v is None:
            return default
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, (int,)):
            return int(v)
        if isinstance(v, float):
            if math.isnan(v) or math.isinf(v):
                return default
            return int(round(v))
        s = str(v).strip()
        if not s:
            return default
        # quita separadores comunes
        s = s.replace("Gs.", "").replace("Gs", "").strip()
        s = s.replace(".", "").replace(",", "")
        return int(s)
    except Exception:
        return default


def format_gs(v: Any) -> str:
    n = safe_int(v, 0)
    # 1.234.567 estilo PY
    s = f"{n:,}".replace(",", ".")
    return s