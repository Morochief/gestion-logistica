# -*- coding: utf-8 -*-
"""
MIC/DTA PDF Generator - Versión consolidada y estable
- Fuentes Unicode (DejaVuSans) con fallback automático (Helvetica)
- Helpers px→pt y coordenadas consistentes (solo trabajamos en pt dentro de dibujo)
- fit_text_box aplicado a TODOS los campos para mejor presentación
- Ajuste de texto con búsqueda binaria optimizado
- Estilos cacheados y centralizados
- saveState()/restoreState() para evitar fugas de estado
- Limpieza segura de caracteres de control (sin comerse acentos)
- Refactors de cajas/títulos
- Valores por defecto y "******" (16–22)
- Entidades con tipo y número de documento
"""

import os
import re
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# =============================
#        CONFIG / CONSTANTES
# =============================

PT_PER_PX = 0.75

TITLE_OFFSET_PT = 24
SUBTITLE_OFFSET_PT = 16
FIELD_PADDING_PT = 8
FIELD_TITLE_RESERVED_PT = 60  # (se mantiene, no se usa directamente)

# CAMBIO: reserva de espacio para encabezados (título+subtítulo)
HEADER_RESERVED_PT = 56

FONT_REGULAR = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"
FALLBACK_REGULAR = "Helvetica"
FALLBACK_BOLD = "Helvetica-Bold"

DEBUG = False  # poné True si querés logs

# =============================
#         UTILIDADES
# =============================


def px2pt(v: float) -> float:
    return v * PT_PER_PX


def log(msg: str):
    if DEBUG:
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode('ascii', 'replace').decode('ascii'))


def safe_clean_text(text: str) -> str:
    """
    Limpia saltos de línea y remueve controles ASCII (excepto \n y \t).
    """
    if text is None:
        return ""
    t = text.replace('\r\n', '\n').replace('\r', '\n')
    t = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', t)
    return t


def find_ttf_candidate_paths():
    return [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        os.path.expanduser(
            "~/AppData/Local/Microsoft/Windows/Fonts/DejaVuSans.ttf"),
        os.path.expanduser(
            "~/AppData/Local/Microsoft/Windows/Fonts/DejaVuSans-Bold.ttf"),
        "C:\\Windows\\Fonts\\DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\DejaVuSans-Bold.ttf",
        "/Library/Fonts/DejaVuSans.ttf",
        "/Library/Fonts/DejaVuSans-Bold.ttf",
    ]


def register_unicode_fonts():
    """
    Registra DejaVuSans (regular/bold) si están disponibles, sino cae a Helvetica.
    """
    global FONT_REGULAR, FONT_BOLD
    try:
        regs = set(pdfmetrics.getRegisteredFontNames())
        if FONT_REGULAR in regs and FONT_BOLD in regs:
            return

        reg_path, bold_path = None, None
        for p in find_ttf_candidate_paths():
            if os.path.exists(p):
                if p.lower().endswith("dejavusans.ttf"):
                    reg_path = reg_path or p
                elif p.lower().endswith("dejavusans-bold.ttf"):
                    bold_path = bold_path or p

        if reg_path and bold_path:
            pdfmetrics.registerFont(TTFont(FONT_REGULAR, reg_path))
            pdfmetrics.registerFont(TTFont(FONT_BOLD, bold_path))
            log(f"✅ Fuentes registradas: {reg_path} / {bold_path}")
        else:
            FONT_REGULAR = FALLBACK_REGULAR
            FONT_BOLD = FALLBACK_BOLD
            log("⚠️ No se halló DejaVuSans. Usando Helvetica.")
    except Exception as e:
        FONT_REGULAR = FALLBACK_REGULAR
        FONT_BOLD = FALLBACK_BOLD
        log(
            f"⚠️ No se pudieron registrar fuentes Unicode ({e}). Usando Helvetica.")


register_unicode_fonts()

# =============================
#         ESTILOS CACHE
# =============================

_STYLES = None


def get_styles():
    global _STYLES
    if _STYLES is not None:
        return _STYLES

    ss = getSampleStyleSheet()
    ss["Normal"].fontName = FONT_REGULAR
    ss["Normal"].fontSize = 10
    ss["Normal"].leading = 12

    ss.add(ParagraphStyle(
        'esBold', parent=ss['Normal'], fontName=FONT_BOLD, fontSize=11, leading=13, alignment=TA_LEFT))
    ss.add(ParagraphStyle(
        'es', parent=ss['Normal'], fontName=FONT_REGULAR, fontSize=10, leading=12, alignment=TA_LEFT))
    ss.add(ParagraphStyle('firma', parent=ss['Normal'], fontName=FONT_BOLD,
           fontSize=11, leading=13, alignment=TA_LEFT, spaceBefore=10))
    ss.add(ParagraphStyle('transportador',
           parent=ss['Normal'], fontName=FONT_BOLD, fontSize=14, leading=16, alignment=TA_LEFT, spaceBefore=20))

    _STYLES = ss
    return _STYLES

# =============================
#     DIBUJO BASE DE CAJAS
# =============================


def rect_pt(c, x_px, y_px, w_px, h_px, height_px, line_width=1.0, show=True):
    """
    Dibuja rectángulo con coords en px (layout) convertidas a pt (ReportLab).
    Retorna (x_pt, y_pt, w_pt, h_pt).
    """
    x, y, w, h = px2pt(x_px), px2pt(
        height_px - y_px - h_px), px2pt(w_px), px2pt(h_px)
    if show:
        c.saveState()
        c.setLineWidth(line_width)
        c.rect(x, y, w, h)
        c.restoreState()
    return x, y, w, h


def draw_field_title(c, x_pt, y_pt, w_pt, h_pt, titulo, subtitulo, title_font=None, sub_font=None):
    if title_font is None:
        title_font = FONT_BOLD
    if sub_font is None:
        sub_font = FONT_REGULAR

    c.saveState()
    try:
        tx = x_pt + FIELD_PADDING_PT
        ty = y_pt + h_pt - TITLE_OFFSET_PT
        if titulo:
            c.setFont(title_font, 13)
            c.drawString(tx, ty, titulo)
        if subtitulo:
            c.setFont(sub_font, 11)
            c.drawString(tx, ty - SUBTITLE_OFFSET_PT, subtitulo)
    finally:
        c.restoreState()
    # Devuelve área de contenido (con padding)
    return (x_pt + FIELD_PADDING_PT, y_pt + FIELD_PADDING_PT,
            w_pt - 2 * FIELD_PADDING_PT, h_pt - 2 * FIELD_PADDING_PT)

# =============================
#  AJUSTE DE TEXTO OPTIMIZADO
# =============================


def get_field_config(campo_numero):
    """
    Config específica por campo.
    Solo tocamos tamaños de fuente y alto reservado para que el cuerpo empiece más arriba
    (sin mover las cajas ni cambiar draw_field_title).
    """

    # ---- CAMPOS GRANDES DE LISTADOS / TEXTOS LARGOS ----
    if campo_numero == 38:
        return {
            'min_font': 5,        # antes 4
            'max_font': 12,
            'leading_ratio': 1.12,
            'margin': 8,
            'title_reserved_h': 52,   # antes 56 → más área útil
            'allow_multiline': True
        }

    # Campo 39 se maneja aparte (Paragraph/Frame), no entra aquí.

    # ---- ENTIDADES (mejor lectura) 33,34,35 ----
    if campo_numero in [33, 34, 35]:
        return {
            'min_font': 9,          # mantenemos legibilidad alta
            'max_font': 14,
            'leading_ratio': 1.18,  # un poco menos de interlineado para que entren más líneas
            'margin': 4,            # margen más chico => más ancho útil
            'title_reserved_h': 34,  # menos reserva arriba => el cuerpo empieza más arriba
            'allow_multiline': True
        }

    # ---- CAMPO 9 (propietario) y 37 (precintos) ----
    if campo_numero == 9:
        return {
            'min_font': 7,        # sube un poco
            'max_font': 14,
            'leading_ratio': 1.15,
            'margin': 6,
            'title_reserved_h': 44,   # menos reserva → empieza más arriba
            'allow_multiline': True
        }
    if campo_numero == 37:
        return {
            'min_font': 7,
            'max_font': 12,
            'leading_ratio': 1.12,
            'margin': 6,
            'title_reserved_h': 42,   # baja la reserva
            'allow_multiline': True
        }

    # ---- BLOQUE DE TOTALES PEQUEÑOS 30,31,32 (1 sola línea) ----
    if campo_numero in [30, 31, 32]:
        return {
            'min_font': 9,        # más grande para que se note
            'max_font': 16,
            'leading_ratio': 1.2,
            'margin': 6,
            'title_reserved_h': 28,   # clave: antes ~56 → ahora 24 para que aparezcan
            'allow_multiline': False  # 1 línea; recorta con "..."
        }

    # ---- MEDIANOS 7,8,24,26 (ligero ajuste) ----
    if campo_numero in [7, 8, 24, 26]:
        return {
            'min_font': 7,
            'max_font': 14,
            'leading_ratio': 1.2,
            'margin': 6,
            'title_reserved_h': 48,   # un poco menos que 56
            'allow_multiline': True
        }

    # Campos pequeños de una línea
    else:
        return {
            'min_font': 8,            # sube base general para mejor lectura
            'max_font': 16,
            'leading_ratio': 1.2,
            'margin': 6,
            'title_reserved_h': 48,   # menos que 56 para ganar área
            'allow_multiline': False
        }


def fit_text_box_universal(
    c,
    text,
    x, y, w, h,
    campo_numero,
    font=None
):
    """
    Ajusta texto usando configuración específica por campo.
    """
    if font is None:
        font = FONT_REGULAR

    text = safe_clean_text(text)
    if not text:
        return {'font_size_used': 8, 'lines_drawn': 0, 'truncated': False,
                'effective_area': f"{w:.1f}x{h:.1f}"}

    config = get_field_config(campo_numero)

    eff_w = w - 2 * config['margin']
    eff_h = h - 2 * config['margin'] - config['title_reserved_h']

    if eff_w <= 0 or eff_h <= 0:
        return {'font_size_used': config['min_font'], 'lines_drawn': 0, 'truncated': True,
                'effective_area': f"{w:.1f}x{h:.1f}"}

    def wrap_text_for_size(sz):
        if not config['allow_multiline']:
            # Para campos de una línea, simplemente truncar
            single_line = text.replace('\n', ' ').replace('\r', ' ')
            max_chars = len(single_line)
            while max_chars > 0:
                test_text = single_line[:max_chars]
                if c.stringWidth(test_text, font, sz) <= eff_w:
                    break
                max_chars -= 1

            if max_chars < len(single_line) and max_chars > 3:
                return [single_line[:max_chars-3] + "..."]
            elif max_chars > 0:
                return [single_line[:max_chars]]
            else:
                return [""]

        # Para campos multilinea
        lines = []
        for manual_line in text.split('\n'):
            if not manual_line.strip():
                lines.append("")
                continue
            words, cur = manual_line.split(), ""
            for word in words:
                test = (cur + " " + word) if cur else word
                if c.stringWidth(test, font, sz) <= eff_w:
                    cur = test
                else:
                    if cur:
                        lines.append(cur)
                    cur = word
            if cur:
                lines.append(cur)
        return lines

    # Búsqueda binaria del tamaño óptimo
    lo, hi = config['min_font'], config['max_font']
    best_sz, best_lines = config['min_font'], []

    while lo <= hi:
        mid = (lo + hi) // 2
        lines = wrap_text_for_size(mid)
        lh = mid * config['leading_ratio']
        total_h = lh * len(lines)

        if total_h <= eff_h:
            best_sz, best_lines = mid, lines
            lo = mid + 1
        else:
            hi = mid - 1

    if not best_lines:
        best_sz = config['min_font']
        best_lines = wrap_text_for_size(best_sz)

    # Dibujar el texto
    c.saveState()
    try:
        c.setFont(font, best_sz)
        lh = best_sz * config['leading_ratio']
        start_x = x + config['margin']
        start_y = y + h - config['margin'] - \
            config['title_reserved_h'] - best_sz

        max_lines = int(eff_h // lh) if lh > 0 else 0
        drawn = best_lines[:max_lines]
        truncated = len(best_lines) > max_lines

        for i, ln in enumerate(drawn):
            line_y = start_y - i * lh
            if line_y < y + config['margin']:
                break
            c.drawString(start_x, line_y, ln)

        # Mostrar "..." solo si realmente es necesario y hay espacio
        if truncated and drawn and max_lines > 0 and best_sz <= config['min_font'] + 2:
            if len(drawn) < max_lines:  # Solo si hay espacio para una línea más
                truncate_y = start_y - len(drawn) * lh
                if truncate_y >= y + config['margin']:
                    c.drawString(start_x, truncate_y, "...")

        return {
            'font_size_used': best_sz,
            'lines_drawn': len(drawn),
            'truncated': truncated,
            'effective_area': f"{eff_w:.1f}x{eff_h:.1f}"
        }
    finally:
        c.restoreState()

# =============================
#      CAMPOS ESPECIALES
# =============================


def obtener_valor_campo(mic_data, key, campo_numero):
    """
    Obtiene el valor de un campo con defaults para casos especiales.
    """
    valor = ""
    if key and mic_data:
        valor = mic_data.get(key, "")

    if 16 <= campo_numero <= 22:
        if not valor or str(valor).strip() == "":
            return "******"

    if campo_numero == 13 and (not valor or str(valor).strip() == ""):
        return "45 TON"

    if campo_numero == 4 and (not valor or str(valor).strip() == ""):
        return "PROVISORIO"

    if campo_numero == 5 and (not valor or str(valor).strip() == ""):
        return "1 / 1"

    if campo_numero == 26 and (not valor or str(valor).strip() == ""):
        return "520-PARAGUAY"

    if campo_numero == 25 and (not valor or str(valor).strip() == ""):
        return "DOLAR AMERICANO"

    return str(valor) if valor else ""


def formatear_campo_entidad(mic_data, campo_key):
    """
    Formatea campos de entidades (33, 34, 35) asegurando que siempre
    se muestre tipo y número de documento, incluso si viene embebido en el nombre.
    """
    valor = mic_data.get(campo_key, "")
    if not valor:
        return ""

    if isinstance(valor, str):
        return valor

    if isinstance(valor, dict):
        nombre = (valor.get('nombre') or "").strip()
        direccion = (valor.get('direccion') or "").strip()
        ciudad = (valor.get('ciudad') or "").strip()
        pais = (valor.get('pais') or "").strip()

        tipo_doc = (valor.get('tipo_documento') or "").strip()
        numero_doc = (valor.get('numero_documento') or "").strip()

        # fallback: si no vienen separados, buscar "RUC"/"CNPJ"/"Doc" en el nombre o direccion
        if not numero_doc:
            for campo in [nombre, direccion]:
                if campo and ("RUC" in campo or "CNPJ" in campo or "Doc" in campo):
                    numero_doc = campo
                    tipo_doc = ""  # ya viene embebido
                    break

        doc_str = ""
        if tipo_doc and numero_doc:
            doc_str = f"{tipo_doc}: {numero_doc}"
        elif numero_doc:
            doc_str = numero_doc

        lineas = []

        # Primera línea: nombre + doc
        if nombre and doc_str:
            lineas.append(f"{nombre} — {doc_str}")
        elif nombre:
            lineas.append(nombre)
        elif doc_str:
            lineas.append(doc_str)

        if direccion:
            lineas.append(direccion)

        if ciudad and pais:
            lineas.append(f"{ciudad} - {pais}")
        elif ciudad:
            lineas.append(ciudad)
        elif pais:
            lineas.append(pais)

        return "\n".join(lineas)

    return str(valor)


def normalized_date(mic_data):
    for k in ('campo_6_fecha', 'fecha_emision', 'fecha'):
        v = (mic_data or {}).get(k, '')
        if v:
            return v
    return datetime.now().strftime('%d/%m/%Y')


def draw_campo39(c, x_px, y_px, w_px, h_px, height_px, mic_data=None):
    """
    Campo 39: texto legal, línea de firma, transportador + fecha.
    """
    styles = get_styles()
    X, Y, W, H = px2pt(x_px), px2pt(
        height_px - y_px - h_px), px2pt(w_px), px2pt(h_px)

    c.saveState()
    try:
        c.rect(X, Y, W, H)
    finally:
        c.restoreState()

    txt_es = ("Declaramos que las informaciones presentadas en este Documento son expresión de verdad, "
              "que los datos referentes a las mercaderías fueron transcriptos exactamente conforme a la "
              "declaración del remitente, las cuales son de su exclusiva responsabilidad, y que esta operación "
              "obedece a lo dispuesto en el Convenio sobre Transporte Internacional Terrestre de los países del Cono Sur.")
    txt_pt = ("Declaramos que as informações prestadas neste Documento são a expressão de verdade que os dados referentes "
              "às mercadorias foram transcritos exatamente conforme a declaração do remetente, os quais são de sua exclusiva "
              "responsabilidade, e que esta operação obedece ao disposto no Convênio sobre Transporte Internacional Terrestre.")
    txt_firma = "39 Firma y sello del porteador / Assinatura e carimbo do transportador"

    nombre_transportador = ""
    if mic_data:
        nombre_transportador = (
            mic_data.get('campo_1_transporte', '') or
            mic_data.get('transportadora_nombre', '') or
            mic_data.get('transportadora', '') or
            "TRANSPORTADOR"
        )
        if '\n' in nombre_transportador:
            nombre_transportador = nombre_transportador.split('\n')[0].strip()
    fecha_actual = normalized_date(mic_data)

    para_es = Paragraph(txt_es, styles['es'])
    para_pt = Paragraph(txt_pt, styles['es'])
    para_firma = Paragraph(txt_firma, styles['firma'])
    para_transportador = Paragraph(
        nombre_transportador, styles['transportador'])

    c.saveState()
    try:
        f = Frame(X + FIELD_PADDING_PT, Y + FIELD_PADDING_PT,
                  W - 2*FIELD_PADDING_PT, H - 2*FIELD_PADDING_PT, showBoundary=0)
        f.addFromList([para_es, para_pt, para_firma, para_transportador], c)
    finally:
        c.restoreState()

    c.saveState()
    try:
        c.setFont(FONT_REGULAR, 12)
        c.drawString(X + FIELD_PADDING_PT + 4, Y + 25,
                     f"Data / Fecha: {fecha_actual}")
    finally:
        c.restoreState()


def draw_campo40_robust(c, x_pt, y_pt, w_pt, h_pt, valor):
    """
    Campo 40 usando fit_text_box_universal.
    """
    if not valor:
        return

    # Usar la función universal para el campo 40
    fit_text_box_universal(c, valor, x_pt, y_pt, w_pt, h_pt, 40, FONT_REGULAR)


DOC_PATTERNS = [
    r'(CNPJ\s*:\s*[\d./-]+)',
    r'(RUC\s*:\s*[\d.-]+)',
    r'(Doc(?:umento)?\s*:\s*[\w\d./-]+)'
]


def _buscar_doc_en_texto(texto: str):
    if not texto:
        return None
    for pat in DOC_PATTERNS:
        m = re.search(pat, texto, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def validar_entidades_33_34_35(mic_data: dict, autofix=False):
    """
    Valida que 33/34/35 tengan tipo_documento y numero_documento.
    Si autofix=True, intenta extraer un doc embebido (CNPJ/RUC/Doc) de "nombre"/"direccion"
    y lo coloca en numero_documento (tipo_documento queda vacío si no se pudo separar).
    """
    claves = {
        33: 'campo_33_datos_campo1_crt',
        34: 'campo_34_datos_campo4_crt',
        35: 'campo_35_datos_campo6_crt',
    }

    problemas = []
    for n, key in claves.items():
        val = mic_data.get(key)
        if not isinstance(val, dict):
            print(
                f"⚠️ Campo {n}: no es dict o está vacío ({type(val).__name__}).")
            problemas.append(n)
            continue

        tipo = (val.get('tipo_documento') or "").strip()
        numero = (val.get('numero_documento') or "").strip()

        if not numero:
            # intentar extraer del nombre o dirección
            doc_embebido = _buscar_doc_en_texto(
                (val.get('nombre') or "") + " " + (val.get('direccion') or ""))
            if doc_embebido and autofix:
                # si viene como "CNPJ: 12.345..." lo ponemos entero en numero_documento
                val['numero_documento'] = doc_embebido
                # no forzamos tipo si no podemos separarlo
                val.setdefault('tipo_documento', '')
                numero = doc_embebido

        if not numero or not tipo:  # aún falta algo
            faltantes = []
            if not tipo:
                faltantes.append("tipo_documento")
            if not numero:
                faltantes.append("numero_documento")
            print(f"❌ Campo {n}: faltan {', '.join(faltantes)} en {key}.")
            problemas.append(n)
        else:
            print(f"✅ Campo {n}: {tipo}: {numero}")

    if not problemas:
        print("🎉 33/34/35 OK: todos con tipo y número de documento.")
    else:
        print(f"🔎 Revisa campos: {problemas} (ver mensajes arriba).")

    return problemas


# =============================
#   GENERADOR PRINCIPAL PDF
# =============================


def generar_micdta_pdf_con_datos(mic_data: dict, filename: str = "mic.pdf"):
    """
    Entry point para generar el PDF del MIC/DTA.
    Ahora TODOS los campos usan fit_text_box_universal.
    """
    register_unicode_fonts()

    width_px, height_px = 1700, 2800
    width_pt, height_pt = px2pt(width_px), px2pt(height_px)

    c = canvas.Canvas(filename, pagesize=(width_pt, height_pt))
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)

    # Encabezado
    x0, y0 = 55, 55
    rect_w, rect_h = 1616, 108.5
    rect_pt(c, x0, y0, rect_w, rect_h, height_px, line_width=2)

    mic_x, mic_y = x0 + 24, y0 + 15
    mic_w, mic_h = 235, 70
    mx, my, mw, mh = rect_pt(c, mic_x, mic_y, mic_w,
                             mic_h, height_px, line_width=1)

    c.saveState()
    try:
        c.setFont(FONT_BOLD, 28)
        c.drawCentredString(mx + mw / 2, my + mh / 2 - 12, "MIC/DTA")
        title_x, title_y = x0 + 280, y0 + 36
        c.setFont(FONT_BOLD, 20)
        c.drawString(px2pt(title_x), px2pt(height_px - title_y),
                     "Manifiesto Internacional de Carga por Carretera / Declaración de Tránsito Aduanero")
        c.setFont(FONT_REGULAR, 20)
        c.drawString(px2pt(title_x), px2pt(height_px - title_y - 38),
                     "Manifesto Internacional de Carga Rodoviária / Declaração de Trânsito")
    finally:
        c.restoreState()

    campos = [
        (1,  55, 162, 863, 450, "1 Nombre y domicilio del porteador",
         "Nome e endereço do transportador", "campo_1_transporte"),
        (2,  55, 610, 861, 142, "2 Rol de contribuyente",
         "Cadastro geral de contribuintes", "campo_2_numero"),
        (3, 916, 162, 389, 169, "3 Tránsito aduanero",
         "Trânsito aduaneiro", "campo_3_transporte"),
        (4, 1305, 162, 365, 167, "4 Nº", "", "campo_4_estado"),
        (5, 916, 330, 388, 115, "5 Hoja / Folha", "", "campo_5_hoja"),
        (6, 1305, 330, 365, 115, "6 Fecha de emisión",
         "Data de emissão", "campo_6_fecha"),
        (7, 916, 445, 752, 166, "7 Aduana, ciudad y país de partida",
         "Alfândega, cidade e país de partida", "campo_7_pto_seguro"),
        (8, 916, 610, 752, 142, "8 Ciudad y país de destino final",
         "Cidade e país de destino final", "campo_8_destino"),
        (9,  55, 750, 861, 165, "9 CAMION ORIGINAL: Nombre y domicilio del propietario",
         "CAMINHÃO ORIGINAL: Nome e endereço do proprietário", "campo_9_datos_transporte"),
        (10, 55, 915, 417, 142, "10 Rol de contribuyente",
         "Cadastro geral de", "campo_10_numero"),
        (11, 470, 915, 445, 142, "11 Placa de camión",
         "Placa do caminhão", "campo_11_placa"),
        (12, 55, 1055, 417, 142, "12 Marca y número",
         "Marca e número", "campo_12_modelo_chasis"),
        (13, 470, 1055, 445, 142, "13 Capacidad de arrastre",
         "Capacidade de tração (t)", "campo_13_siempre_45"),
        (14, 55, 1197, 417, 135, "14 AÑO", "ANO", "campo_14_anio"),
        (15, 470, 1197, 445, 135, "15 Semirremolque / Remolque",
         "Semi-reboque / Reboque", "campo_15_placa_semi"),
        (16, 915, 752, 753, 163, "16 CAMION SUSTITUTO: Nombre y domicilio del",
         "CAMINHÃO SUBSTITUTO: Nome e endereço do", "campo_16"),
        (17, 915, 915, 395, 140, "17 Rol de contribuyente",
         "Cadastro geral de", "campo_17"),
        (18, 1310, 915, 360, 140, "18 Placa del camión", "Placa do", "campo_18"),
        (19, 915, 1055, 395, 140, "19 Marca y número", "Marca e número", "campo_19"),
        (20, 1310, 1055, 360, 140, "20 Capacidad de arrastre",
         "Capacidade de tração", "campo_20"),
        (21, 915, 1195, 395, 135, "21 AÑO", "ANO", "campo_21"),
        (22, 1310, 1195, 360, 135, "22 Semirremolque / Remolque",
         "Semi-reboque / Reboque", "campo_22"),
        (23, 55, 1330, 313, 154, "23 Nº carta de porte",
         "Nº do conhecimento", "campo_23_numero_campo2_crt"),
        (24, 366, 1330, 550, 154, "24 Aduana de destino",
         "Alfândega de destino", "campo_24_aduana"),
        (25, 55, 1482, 313, 136, "25 Moneda", "Moeda", "campo_25_moneda"),
        (26, 366, 1482, 550, 136, "26 Origen de las mercaderías",
         "Origem das mercadorias", "campo_26_pais"),
        (27, 55, 1618, 313, 136, "27 Valor FOT",
         "Valor FOT", "campo_27_valor_campo16"),
        (28, 366, 1618, 275, 136, "28 Flete en U$S",
         "Flete em U$S", "campo_28_total"),
        (29, 641, 1618, 275, 136, "29 Seguro en U$S",
         "Seguro em U$S", "campo_29_seguro"),
        (30, 55, 1754, 313, 119, "30 Tipo de Bultos",
         "Tipo dos volumes", "campo_30_tipo_bultos"),
        (31, 366, 1754, 275, 119, "31 Cantidad de",
         "Quantidade de", "campo_31_cantidad"),
        (32, 641, 1754, 275, 119, "32 Peso bruto",
         "Peso bruto", "campo_32_peso_bruto"),
        (33, 915, 1330, 753, 154, "33 Remitente",
         "Remetente", "campo_33_datos_campo1_crt"),
        (34, 915, 1482, 753, 136, "34 Destinatario",
         "Destinatario", "campo_34_datos_campo4_crt"),
        (35, 915, 1618, 753, 136, "35 Consignatario",
         "Consignatário", "campo_35_datos_campo6_crt"),
        (36, 915, 1754, 753, 250, "36 Documentos anexos",
         "Documentos anexos", "campo_36_factura_despacho"),
        (37, 55, 1873, 861, 131, "37 Número de precintos",
         "Número dos lacres", "campo_37_valor_manual"),
        (38, 55, 2004, 1613, 222, "38 Marcas y números de los bultos, descripción de las mercaderías",
         "Marcas e números dos volumes, descrição das mercadorias", "campo_38_datos_campo11_crt"),
        (39, 55, 2226, 838, 498, "", "", None),
        (40, 891, 2226, 780, 326, "40 Nº DTA, ruta y plazo de transporte",
         "Nº DTA, rota e prazo de transporte", "campo_40_tramo"),
        (41, 891, 2552, 780, 175, "41 Firma y sello de la Aduana de Partida",
         "Assinatura e carimbo de Alfândega de", None),
    ]

    for n, x, y, w, h, titulo, subtitulo, key in campos:
        if n == 39:
            draw_campo39(c, x, y, w, h, height_px, mic_data)
            continue

        x_pt, y_pt, w_pt, h_pt = rect_pt(
            c, x, y, w, h, height_px, line_width=1)
        # CAMBIO: usar el área de contenido devuelta para empezar más abajo
        cx, cy, cw, ch = draw_field_title(
            c, x_pt, y_pt, w_pt, h_pt, titulo, subtitulo)

        valor = obtener_valor_campo(mic_data, key, n) if key else ""

        if n in [33, 34, 35] and valor:
            valor = formatear_campo_entidad(mic_data, key)

        # APLICAR fit_text_box_universal a TODOS los campos con valor
        if valor and n != 39:  # El 39 tiene manejo especial
            log(f"📝 Campo {n}: Aplicando fit_text_box_universal")
            result = fit_text_box_universal(
                c, valor, cx, cy, cw, ch, n, FONT_REGULAR)
            if DEBUG:
                log(f"   → Fuente: {result['font_size_used']}pt, Líneas: {result['lines_drawn']}, "
                    f"Truncado: {result['truncated']}, Área: {result['effective_area']}")

    # Borde exterior
    rect_pt(c, 55, 55, 1616.75, 2672.75, height_px, line_width=1)
    c.save()
    log(f"✅ PDF generado: {filename}")


# =============================
#     FUNCIONES DE TESTING
# =============================

def test_mic_pdf():
    """
    Función de prueba para generar un PDF con datos de ejemplo.
    """
    mic_data_ejemplo = {
        'campo_1_transporte': 'TRANSPORTES EJEMPLO S.A.\nAv. Principal 123\nAsunción - Paraguay\nTeléfono: +595 21 123456',
        'campo_2_numero': '80012345-1',
        'campo_3_transporte': 'TRANSITO NACIONAL',
        'campo_4_estado': 'DEFINITIVO',
        'campo_5_hoja': '1 / 1',
        'campo_6_fecha': '15/08/2025',
        'campo_7_pto_seguro': 'ADUANA CENTRAL - ASUNCIÓN - PARAGUAY',
        'campo_8_destino': 'PUERTO DE SANTOS - SÃO PAULO - BRASIL',
        'campo_9_datos_transporte': 'JUAN PÉREZ CONDUCTOR\nCédula: 1.234.567\nLicencia Profesional: AB123456\nVencimiento: 31/12/2025',
        'campo_10_numero': '1234567-8',
        'campo_11_placa': 'ABC-1234',
        'campo_12_modelo_chasis': 'MERCEDES BENZ ATEGO 2426\nChasis: WDB9704241L123456',
        'campo_13_siempre_45': '45 TON',
        'campo_14_anio': '2020',
        'campo_15_placa_semi': 'REM-5678',
        'campo_16': '******',
        'campo_17': '******',
        'campo_18': '******',
        'campo_19': '******',
        'campo_20': '******',
        'campo_21': '******',
        'campo_22': '******',
        'campo_23_numero_campo2_crt': 'CRT-2025-001234',
        'campo_24_aduana': 'ADUANA DE SANTOS - BRASIL',
        'campo_25_moneda': 'DOLAR AMERICANO',
        'campo_26_pais': '520-PARAGUAY',
        'campo_27_valor_campo16': '125,500.00',
        'campo_28_total': '8,500.00',
        'campo_29_seguro': '1,255.00',
        'campo_30_tipo_bultos': 'CONTENEDORES',
        'campo_31_cantidad': '2',
        'campo_32_peso_bruto': '28,750 KG',
        'campo_33_datos_campo1_crt': {
            'nombre': 'EXPORTADORA PARAGUAYA S.A.',
            'direccion': 'Av. Mariscal López 1234',
            'ciudad': 'Asunción',
            'pais': 'Paraguay',
            'tipo_documento': 'RUC',
            'numero_documento': '80012345-1'
        },
        'campo_34_datos_campo4_crt': {
            'nombre': 'IMPORTADORA BRASILEIRA LTDA.',
            'direccion': 'Rua das Flores 567',
            'ciudad': 'São Paulo',
            'pais': 'Brasil',
            'tipo_documento': 'CNPJ',
            'numero_documento': '12.345.678/0001-90'
        },
        'campo_35_datos_campo6_crt': {
            'nombre': 'AGENTE ADUANERO SANTOS',
            'direccion': 'Porto de Santos, Armazém 15',
            'ciudad': 'Santos',
            'pais': 'Brasil',
            'tipo_documento': 'CNPJ',
            'numero_documento': '98.765.432/0001-11'
        },
        'campo_36_factura_despacho': 'FACTURA COMERCIAL Nº FC-2025-0567\nDECLARACIÓN DE EXPORTACIÓN Nº DE-2025-1234\nCERTIFICADO DE ORIGEN Nº CO-2025-0890\nPÓLIZA DE SEGURO Nº PS-2025-4567',
        'campo_37_valor_manual': 'PRECINTO ADUANA: ADU-2025-789123\nPRECINTO EMPRESA: EMP-2025-456789\nPRECINTO CONTENEDOR 1: CONT-ABC123456\nPRECINTO CONTENEDOR 2: CONT-DEF789012',
        'campo_38_datos_campo11_crt': '''CONTENEDOR 1: TCLU-1234567-8
Marca: MAERSK LINE
Peso tara: 2,200 KG
Peso neto: 12,550 KG
Mercadería: PRODUCTOS ALIMENTICIOS PROCESADOS
- Conservas de carne bovina (300 cajas x 12 unidades)
- Aceite de soja refinado (200 bidones x 20 litros)
- Harina de trigo (150 bolsas x 50 kg)

CONTENEDOR 2: MSKU-9876543-2
Marca: MSC
Peso tara: 2,300 KG
Peso neto: 13,700 KG
Mercadería: PRODUCTOS MANUFACTURADOS
- Calzados de cuero (500 pares, varios modelos)
- Textiles confeccionados (300 prendas)
- Artículos de marroquinería (100 unidades)

Valor total FOB: USD 125,500.00
Condiciones: CIF Santos
Incoterms 2020''',
        'campo_40_tramo': '''DTA Nº: DTA-2025-001234
RUTA AUTORIZADA:
Origen: Asunción, Paraguay
Destino: Santos, Brasil
Tránsito por: Ciudad del Este - Foz do Iguaçu - Curitiba - São Paulo

PLAZO DE TRANSPORTE: 7 días calendario
Fecha inicio: 15/08/2025
Fecha vencimiento: 22/08/2025

OBSERVACIONES:
- Carga refrigerada
- Manipulación con cuidado especial
- Seguro contratado por USD 127,000.00'''
    }

    print("🚀 Generando PDF de prueba con fit_text_box_universal en todos los campos...")
    generar_micdta_pdf_con_datos(mic_data_ejemplo, "mic_test_universal.pdf")
    print("✅ PDF de prueba generado: mic_test_universal.pdf")


if __name__ == "__main__":
    # Activar debug para ver los logs
    DEBUG = True
    test_mic_pdf()
