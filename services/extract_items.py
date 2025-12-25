import openpyxl
import unicodedata


def _norm(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )
    s = " ".join(s.split())
    return s


ACCEPTED_HEADERS = {
    "descripcion",
    "descripciones",
    "descripcion del bien",
    "descripcion del item",
    "descripcion del ítem",
    "descripcion del blen",     # typo común
    "descripcion del bien",     # repetido a propósito (ok)
}


def _find_header(ws, scan_rows: int = 30):
    max_row = min(scan_rows, ws.max_row)
    for r in range(1, max_row + 1):
        for c in range(1, ws.max_column + 1):
            v = ws.cell(row=r, column=c).value
            if not v:
                continue
            if _norm(v) in ACCEPTED_HEADERS:
                return r, c
    return None, None


def extract_descriptions_from_excel(excel_path: str) -> list[str]:
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    ws = wb.active

    header_row, desc_col = _find_header(ws, scan_rows=30)
    if not desc_col:
        return []

    out = []
    for r in range(header_row + 1, ws.max_row + 1):
        v = ws.cell(row=r, column=desc_col).value
        if v is None:
            continue
        s = str(v).strip()
        if s:
            out.append(s)

    return out