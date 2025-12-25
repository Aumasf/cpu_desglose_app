from dataclasses import dataclass

@dataclass(frozen=True)
class BlockCoords:
    x0: float
    y0: float

# Dos formularios por hoja
BLOCK_1 = BlockCoords(x0=0, y0=0)
BLOCK_2 = BlockCoords(x0=0, y0=-395)

# Bajá TODO el overlay un poquito si está "muy arriba"
GLOBAL_Y_SHIFT = -18  # probá -12, -18, -24

# Header (fila 3)
FECHA_X = 55
FECHA_Y = 785

ITEM_X = 250
ITEM_Y = 785

DESC_X = 305
DESC_Y = 785
DESC_MAX_WIDTH = 235

# Logo único por hoja (arriba derecha)
PAGE_LOGO_X = 430
PAGE_LOGO_Y = 812
PAGE_LOGO_W = 140
PAGE_LOGO_H = 45

# Cajas de texto
A_HERRAMIENTAS_X = 70
A_HERRAMIENTAS_Y = 625
A_HERRAMIENTAS_MAXW = 470

B_MANO_OBRA_X = 70
B_MANO_OBRA_Y = 545
B_MANO_OBRA_MAXW = 470

E_MATERIALES_X = 70
E_MATERIALES_Y = 445
E_MATERIALES_MAXW = 470