from __future__ import annotations

import io
from typing import Any, Dict, List, Optional

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader


# ====== AJUSTES FINOS (calibración) ======
PAGE_W, PAGE_H = A4

# Header: fecha | item | descripción
Y_HEADER = 742  # sube/baja esta Y según el template
X_FECHA = 62
X_ITEM = 150
X_DESC = 210

# Logo arriba derecha
LOGO_W_PT = 72  # ~2.5 cm
LOGO_H_PT = 72  # aproximado (se mantiene proporcional si querés)
LOGO_PAD_RIGHT = 40
LOGO_PAD_TOP = 40

# Tipografía base (ReportLab usa Helvetica; Calibri real requiere registrar TTF)
FONT_NAME = "Helvetica"
FONT_SIZE = 8  # más pequeño para que sea legible sin encimar


def _wrap_text(c: canvas.Canvas, text: str, max_width: float) -> List[str]:
    """
    Wrap simple por ancho (sin hyphenation), usando el font ya seteado en canvas.
    """
    words = (text or "").split()
    if not words:
        return [""]

    lines: List[str] = []
    current = words[0]
    for w in words[1:]:
        test = current + " " + w
        if c.stringWidth(test, FONT_NAME, FONT_SIZE) <= max_width:
            current = test
        else:
            lines.append(current)
            current = w
    lines.append(current)
    return lines


def build_pdf_from_template(
    template_pdf_bytes: bytes,
    items: List[Dict[str, Any]],
    fecha_ddmmyyyy: str,
    logo_bytes: Optional[bytes],
    default_logo_bytes: Optional[bytes],
) -> bytes:
    """
    Por cada item genera 1 página:
      - Usa template PDF como base
      - Pega overlay con logo + fecha + item + descripción
    """
    base_reader = PdfReader(io.BytesIO(template_pdf_bytes))
    if len(base_reader.pages) < 1:
        raise ValueError("El template PDF no tiene páginas.")

    base_page = base_reader.pages[0]  # siempre usamos la primera página como “molde”
    writer = PdfWriter()

    chosen_logo = logo_bytes or default_logo_bytes

    for it in items:
        # 1) Crear overlay PDF (1 página)
        overlay_buf = io.BytesIO()
        c = canvas.Canvas(overlay_buf, pagesize=A4)

        c.setFont(FONT_NAME, FONT_SIZE)

        # Logo
        if chosen_logo:
            try:
                img = ImageReader(io.BytesIO(chosen_logo))
                x_logo = PAGE_W - LOGO_PAD_RIGHT - LOGO_W_PT
                y_logo = PAGE_H - LOGO_PAD_TOP - LOGO_H_PT
                c.drawImage(img, x_logo, y_logo, width=LOGO_W_PT, height=LOGO_H_PT, mask="auto")
            except Exception:
                pass

        # Header: fecha | item | descripcion
        nro = it.get("nro", "")
        try:
            nro_str = str(int(float(nro)))  # evita "1.0"
        except Exception:
            nro_str = str(nro)

        desc = str(it.get("descripcion", "") or "")
        desc = desc.strip()

        c.drawString(X_FECHA, Y_HEADER, fecha_ddmmyyyy)
        c.drawString(X_ITEM, Y_HEADER, nro_str)

        # descripción wrap (2-3 líneas máximo para no encimar)
        max_width = PAGE_W - X_DESC - 40
        lines = _wrap_text(c, desc, max_width=max_width)
        max_lines = 3
        line_height = 10
        for i, line in enumerate(lines[:max_lines]):
            c.drawString(X_DESC, Y_HEADER - i * line_height, line)

        c.showPage()
        c.save()
        overlay_buf.seek(0)

        overlay_reader = PdfReader(overlay_buf)
        overlay_page = overlay_reader.pages[0]

        # 2) Clonar página template y merge overlay
        new_page = base_page  # pypdf maneja copy internamente al add_page
        writer.add_page(new_page)
        writer.pages[-1].merge_page(overlay_page)

    out_buf = io.BytesIO()
    writer.write(out_buf)
    return out_buf.getvalue()