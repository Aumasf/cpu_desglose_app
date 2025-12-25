from __future__ import annotations

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash

from config import (
    SECRET_KEY,
    APP_PASSWORD,
    TEMPLATE_PDF_PATH,
    DEFAULT_LOGO_PATH,
)

from services.extract_items import extract_items_from_excel_bytes
from services.pdf_builder import build_pdf_from_template


app = Flask(__name__)
app.secret_key = SECRET_KEY


def _is_logged_in() -> bool:
    return bool(session.get("logged_in"))


@app.get("/")
def home():
    if not _is_logged_in():
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd and APP_PASSWORD and pwd == APP_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))
        flash("Contraseña incorrecta.")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.post("/generate")
def generate():
    if not _is_logged_in():
        return redirect(url_for("login"))

    # Excel obligatorio
    excel_file = request.files.get("excel")
    if not excel_file or excel_file.filename.strip() == "":
        flash("Debes subir un archivo Excel.")
        return redirect(url_for("home"))

    excel_bytes = excel_file.read()
    if not excel_bytes:
        flash("El Excel está vacío o no se pudo leer.")
        return redirect(url_for("home"))

    # Fecha obligatoria (viene como YYYY-MM-DD desde <input type="date">)
    date_raw = request.form.get("fecha", "").strip()
    if not date_raw:
        flash("Debes elegir una fecha.")
        return redirect(url_for("home"))

    try:
        dt = datetime.strptime(date_raw, "%Y-%m-%d")
        fecha_ddmmyyyy = dt.strftime("%d/%m/%Y")
    except ValueError:
        flash("Fecha inválida. Usa el selector calendario.")
        return redirect(url_for("home"))

    # Logo opcional
    logo_file = request.files.get("logo")
    logo_bytes = None
    if logo_file and logo_file.filename.strip():
        logo_bytes = logo_file.read()
        if not logo_bytes:
            logo_bytes = None

    # Cargar template PDF
    if not TEMPLATE_PDF_PATH.exists():
        flash(f"No existe el template PDF en: {TEMPLATE_PDF_PATH}")
        return redirect(url_for("home"))
    template_pdf_bytes = TEMPLATE_PDF_PATH.read_bytes()

    # Cargar logo default
    default_logo_bytes = DEFAULT_LOGO_PATH.read_bytes() if DEFAULT_LOGO_PATH.exists() else None

    # Extraer ítems del Excel
    try:
        _meta, items = extract_items_from_excel_bytes(excel_bytes)
    except Exception as e:
        flash(str(e))
        return redirect(url_for("home"))

    # Construir PDF
    try:
        pdf_bytes = build_pdf_from_template(
            template_pdf_bytes=template_pdf_bytes,
            items=items,
            fecha_ddmmyyyy=fecha_ddmmyyyy,
            logo_bytes=logo_bytes,
            default_logo_bytes=default_logo_bytes,
        )
    except Exception as e:
        flash(f"Error generando PDF: {e}")
        return redirect(url_for("home"))

    return send_file(
        os.path.join("tmp", "desglose.pdf"),
        as_attachment=True,
        download_name="desglose.pdf",
        mimetype="application/pdf",
        data=pdf_bytes,  # Flask moderno permite data=bytes
    )


if __name__ == "__main__":
    app.run(debug=True)