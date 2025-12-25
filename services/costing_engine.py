from __future__ import annotations

from typing import Any, Dict, List

from .utils import safe_int


def build_cpu_pages(items: List[Dict[str, Any]], fecha_str: str) -> List[Dict[str, Any]]:
    """
    Convierte items (Excel + Match) en CPUs completos para el PDF.

    Claves esperadas del item:
      - nro, descripcion, unidad, cantidad, precio_total_iva
      - a_herramientas, a_materiales (vienen de match_engine)
    """
    cpus: List[Dict[str, Any]] = []

    for it in items:
        # ✅ Normalización obligatoria (acá se arreglan los KeyError)
        it.setdefault("a_herramientas", "herramientas de mano")
        it.setdefault("a_materiales", "consumibles varios")
        it.setdefault("b_mano_obra", 0)  # si no calculás MO todavía, dejalo en 0

        nro = safe_int(it.get("nro", 0))
        desc = str(it.get("descripcion", "") or "")
        unidad = str(it.get("unidad", "") or "")
        cantidad = float(it.get("cantidad", 1.0) or 1.0)
        precio_total_iva = safe_int(it.get("precio_total_iva", 0))

        # Si tu precio_total_iva ya es el total por la cantidad, el unitario adoptado es:
        # unitario = total / cantidad
        if cantidad <= 0:
            cantidad = 1.0

        costo_unitario_adoptado = int(round(precio_total_iva / cantidad))

        # --- CPU mínimo coherente ---
        cpu: Dict[str, Any] = {
            "fecha": fecha_str,
            "item_nro": nro,
            "descripcion": desc,
            "unidad_medida": unidad,
            "raw_qty": cantidad,

            # A - Herramientas
            "a_herramientas": it["a_herramientas"],
            "a_modelo": "",
            "a_horas": 0,
            "a_costo_horario": 0,
            "a_total": 0,

            # B - Mano de obra
            "b_no_aplica": True if safe_int(it.get("b_mano_obra", 0)) == 0 else False,
            "b_total": safe_int(it.get("b_mano_obra", 0)),

            # C / D (simple)
            "c_produccion": 1,
            "costo_produccion_ab": 0,
            "d_costo_unitario_ejecucion": 0,

            # E - Materiales (texto)
            "is_labor": False,
            "e_rows": [],
            "e_total": 0,
            "a_materiales": it["a_materiales"],  # para usarlo en el PDF

            # F - Transporte
            "f_dtm": 0.00,
            "f_consumo": 0.05,
            "f_costo_unit": 10000,
            "f_total": 0,

            # Totales (si no calculás todavía, dejás 0)
            "costo_directo_total": 0,
            "gastos_generales": 0,
            "impuestos_retenciones": 0,
            "costo_unitario_total": 0,
            "iva": 0,
            "costo_unitario_adoptado": costo_unitario_adoptado,
        }

        # Si querés que “costo_unitario_adoptado” sea exactamente el precio_total_iva:
        # cpu["costo_unitario_adoptado"] = precio_total_iva

        cpus.append(cpu)

    return cpus