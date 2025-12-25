import io
from typing import Optional

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

from pypdf import PdfReader, PdfWriter

from config import (
    PDF_TEMPLATE_PATH,
    LOGO_X, LOGO_Y, LOGO_W, LOGO_H,
    DESC_X, DESC_Y,
    FONT_NAME, FONT_SIZE,
    DESC_MAX_WIDTH, LINE_HEIGHT,
)


def _wrap_text(c: canvas.Canvas, text: str, max_width: float):
    """
    Parte el texto en líneas usando el ancho real de la fuente actual.
    """
    words = text.split()
    lines = []
    cur = []
    for w in words:
        test = (" ".join(cur + [w])).strip()
        if c.stringWidth(test, FONT_NAME, FONT_SIZE) <= max_width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def build_pdf_from_template_simple(
    descriptions: list[str],
    out_pdf_path: str,
    logo_path: Optional[str] = None,
):
    """
    Genera un PDF: por cada descripción crea 1 página:
      template_desglose.pdf (fondo) + logo (arriba derecha) + descripción (posición fija)
    """
    if not descriptions:
        raise ValueError("No se encontraron descripciones para imprimir.")

    base = PdfReader(PDF_TEMPLATE_PATH)
    base_page = base.pages[0]  # usa primera página del template

    writer = PdfWriter()

    for desc in descriptions:
        # 1) overlay en memoria
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)

        # Fuente (sin calibri.ttf -> Helvetica estable)
        c.setFont(FONT_NAME, FONT_SIZE)

        # Logo (1 por hoja)
        if logo_path:
            try:
                img = ImageReader(logo_path)
                c.drawImage(img, LOGO_X, LOGO_Y, width=LOGO_W, height=LOGO_H, mask="auto")
            except Exception:
                # si el logo falla, no rompemos todo el PDF
                pass

        # Descripción (solo esto)
        lines = _wrap_text(c, desc, DESC_MAX_WIDTH)
        y = DESC_Y
        for line in lines[:3]:  # límite razonable para no invadir otras celdas
            c.drawString(DESC_X, y, line)
            y -= LINE_HEIGHT

        c.showPage()
        c.save()
        packet.seek(0)

        overlay_reader = PdfReader(packet)
        overlay_page = overlay_reader.pages[0]

        # 2) merge overlay sobre el template
        new_page = base_page  # pypdf permite copiar con merge
        # Para no mutar el base_page original, lo clonamos:
        new_page = new_page.clone()
        new_page.merge_page(overlay_page)

        writer.add_page(new_page)

    with open(out_pdf_path, "wb") as f:
        writer.write(f)