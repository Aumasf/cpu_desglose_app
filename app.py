import os
import uuid

from flask import Flask, render_template, request, send_file

from config import TMP_DIR, DEFAULT_LOGO_PATH
from services.extract_items import extract_descriptions_from_excel
from services.pdf_builder_simple import build_pdf_from_template_simple


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB


def _ensure_dirs():
    os.makedirs(TMP_DIR, exist_ok=True)


@app.get("/")
def index():
    return render_template("index.html", error=None)


@app.post("/generate")
def generate():
    _ensure_dirs()

    try:
        if "excel" not in request.files:
            return render_template("index.html", error="No se subió el Excel.")

        excel = request.files["excel"]
        if not excel or excel.filename.strip() == "":
            return render_template("index.html", error="No se subió el Excel.")

        run_id = str(uuid.uuid4())
        excel_path = os.path.join(TMP_DIR, f"oferta_{run_id}.xlsx")
        excel.save(excel_path)

        # Logo opcional
        logo_path = DEFAULT_LOGO_PATH
        if "logo" in request.files:
            logo = request.files["logo"]
            if logo and logo.filename.strip() != "":
                ext = os.path.splitext(logo.filename)[1].lower() or ".png"
                logo_path = os.path.join(TMP_DIR, f"logo_{run_id}{ext}")
                logo.save(logo_path)

        descriptions = extract_descriptions_from_excel(excel_path)
        if not descriptions:
            return render_template(
                "index.html",
                error="No se encontraron descripciones en el Excel (revisá el encabezado: Descripción / Descripción del Bien / etc.)."
            )

        out_pdf = os.path.join(TMP_DIR, f"CPU_simple_{run_id}.pdf")
        build_pdf_from_template_simple(
            descriptions=descriptions,
            out_pdf_path=out_pdf,
            logo_path=logo_path
        )

        return send_file(out_pdf, as_attachment=True, download_name="CPU_simple.pdf")

    except Exception as e:
        return render_template("index.html", error=f"Error: {e}")


if __name__ == "__main__":
    app.run(debug=True)