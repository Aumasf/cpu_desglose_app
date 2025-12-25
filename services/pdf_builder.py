import os
import io

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# --- Fuente Calibri: si no está instalada, NO rompemos ---
def _set_font_safe(c: canvas.Canvas, size: int):
    # Intento Calibri; si no está, fallback a Helvetica (sin crash)
    try:
        c.setFont("Calibri", size)
    except Exception:
        c.setFont("Helvetica", size)

def _draw_logo_once_per_page(c: canvas.Canvas, logo_path: str):
    if not logo_path or not os.path.exists(logo_path):
        return

    # Ajustes: logo arriba derecha
    # (tocá SOLO estos valores si querés afinar)
    page_w, page_h = A4
    x = page_w - 160
    y = page_h - 110
    w = 140
    h = 60
    try:
        c.drawImage(logo_path, x, y, width=w, height=h, preserveAspectRatio=True, mask='auto')
    except Exception:
        # si el logo falla, seguimos igual
        pass

def _draw_text_block(c: canvas.Canvas, x, y, text, size=8, max_chars=120):
    if text is None:
        return
    s = str(text).strip()
    if not s:
        return

    # recorte simple (mínimo riesgo) para que no "rompa" todo el template
    if len(s) > max_chars:
        s = s[:max_chars-3] + "..."

    _set_font_safe(c, size)
    c.drawString(x, y, s)

def _make_overlay_page(page_data: dict, fecha: str, logo_path: str, half: str):
    """
    half: 'top' o 'bottom' para las dos planillas por hoja.
    page_data: dict con datos del item para imprimir.
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)

    # 1 logo por hoja (lo dibujamos en overlay; si se llama dos veces para top/bottom,
    # lo dibujamos SOLO cuando half == 'top'
    if half == "top":
        _draw_logo_once_per_page(c, logo_path)

    # Coordenadas base (A4 en puntos). Ajustes mínimos para legibilidad.
    # Si está "muy arriba", bajamos el baseline.
    # IMPORTANTÍSIMO: tocá SOLO estos valores para afinar, no cambies lógica.
    page_w, page_h = A4
    base_y = page_h - 110  # antes estaban muy arriba; esto baja

    # offset para la mitad inferior
    if half == "bottom":
        base_y -= 395  # distancia entre formulario superior e inferior (ajustable)

    # === Campos principales en la fila que mencionaste (fecha - item - descripción) ===
    # Estos X son aproximados y seguros; se afinan luego.
    x_fecha = 35
    x_item = 210
    x_desc = 270
    y_row3 = base_y - 20

    item_nro = page_data.get("item") or page_data.get("nro") or page_data.get("numero") or ""
    desc = page_data.get("descripcion") or page_data.get("desc") or ""

    _draw_text_block(c, x_fecha, y_row3, fecha, size=8, max_chars=30)
    _draw_text_block(c, x_item, y_row3, str(item_nro), size=8, max_chars=10)
    _draw_text_block(c, x_desc, y_row3, desc, size=7, max_chars=90)

    # === Texto de Herramientas / Materiales (mínimo para que se lea) ===
    # En tu template van en secciones A/B/E. Por ahora solo imprimimos líneas cortas
    # y más chicas para que NO se empaste.
    herramientas = page_data.get("herramientas") or page_data.get("tools") or ""
    materiales = page_data.get("materiales") or page_data.get("materials") or ""

    # Posiciones aproximadas dentro del cuadro (afinables)
    _draw_text_block(c, 60, base_y - 135, herramientas, size=7, max_chars=70)
    _draw_text_block(c, 60, base_y - 235, materiales, size=7, max_chars=70)

    c.save()
    packet.seek(0)
    return PdfReader(packet).pages[0]

def build_pdf_from_template(
    template_pdf_path: str,
    output_pdf_path: str,
    pages_data=None,
    cpus=None,
    fecha: str = "",
    logo_path: str = "",
    **kwargs
):
    """
    COMPATIBLE y ANTIRUPTURA:
    - acepta pages_data o cpus (por si app.py viejo manda cpus=...)
    - ignora kwargs extra (para que nunca más explote por nombres)
    """

    if pages_data is None and cpus is not None:
        pages_data = cpus
    if pages_data is None:
        pages_data = []

    reader = PdfReader(template_pdf_path)
    writer = PdfWriter()

    # El template debe tener 1 página A4 con 2 formularios.
    template_page = reader.pages[0]

    # Render: 2 items por hoja A4 (top/bottom)
    i = 0
    while i < len(pages_data):
        # duplicamos template para cada hoja final
        base = template_page

        # overlay top
        top_data = pages_data[i]
        overlay_top = _make_overlay_page(top_data, fecha, logo_path, half="top")
        base.merge_page(overlay_top)

        # overlay bottom si existe el segundo item
        if i + 1 < len(pages_data):
            bottom_data = pages_data[i + 1]
            overlay_bottom = _make_overlay_page(bottom_data, fecha, logo_path, half="bottom")
            base.merge_page(overlay_bottom)

        writer.add_page(base)
        i += 2

    with open(output_pdf_path, "wb") as f:
        writer.write(f)