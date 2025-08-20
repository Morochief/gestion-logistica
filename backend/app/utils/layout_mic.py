# -*- coding: utf-8 -*-
"""
MIC/DTA PDF Generator - Versión consolidada y estable
- Fuentes Unicode (DejaVuSans) con fallback automático (Helvetica)
- Helpers px→pt y coordenadas consistentes (solo trabajamos en pt dentro de dibujo)
- Ajuste de texto con búsqueda binaria (Campo 38) + márgenes y reservas de título
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
FIELD_TITLE_RESERVED_PT = 60

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
    return (x_pt + FIELD_PADDING_PT, y_pt + FIELD_PADDING_PT,
            w_pt - 2 * FIELD_PADDING_PT, h_pt - 2 * FIELD_PADDING_PT)

# =============================
#  AJUSTE DE TEXTO (CAMPO 38)
# =============================


def fit_text_box(
    c,
    text,
    x, y, w, h,
    font=None,
    min_font=8,
    max_font=14,
    leading_ratio=1.3,
    margin=12,
    title_reserved_h=0
):
    """
    Ajusta 'text' dentro del rectángulo (x,y,w,h) con búsqueda binaria del tamaño de fuente.
    Respeta \n del usuario y hace wrap por palabras. Dibuja el texto y retorna info de render.
    """
    if font is None:
        font = FONT_REGULAR

    text = safe_clean_text(text)
    if not text:
        return {'font_size_used': min_font, 'lines_drawn': 0, 'truncated': False,
                'effective_area': f"{w:.1f}x{h:.1f}"}

    eff_w = w - 2 * margin
    eff_h = h - 2 * margin - title_reserved_h
    if eff_w <= 0 or eff_h <= 0:
        return {'font_size_used': min_font, 'lines_drawn': 0, 'truncated': True,
                'effective_area': f"{w:.1f}x{h:.1f}"}

    def wrap_for_size(sz):
        lines = []
        for manu in text.split('\n'):
            if not manu.strip():
                lines.append("")
                continue
            words, cur = manu.split(), ""
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

    lo, hi, best_sz, best_lines = int(
        min_font), int(max_font), int(min_font), []

    while lo <= hi:
        mid = (lo + hi) // 2
        lines = wrap_for_size(mid)
        lh = mid * leading_ratio
        total_h = lh * len(lines)
        if total_h <= eff_h:
            best_sz, best_lines = mid, lines
            lo = mid + 1
        else:
            hi = mid - 1

    if not best_lines:
        best_sz = min_font
        best_lines = wrap_for_size(best_sz)

    c.saveState()
    try:
        c.setFont(font, best_sz)
        lh = best_sz * leading_ratio
        start_x = x + margin
        start_y = y + h - margin - title_reserved_h - best_sz

        max_lines = int(eff_h // lh) if lh > 0 else 0
        drawn = best_lines[:max_lines]
        truncated = len(best_lines) > max_lines

        for i, ln in enumerate(drawn):
            line_y = start_y - i * lh
            if line_y < y + margin:
                break
            c.drawString(start_x, line_y, ln)

        if truncated and drawn and max_lines > 0:
            truncate_y = start_y - max_lines * lh
            if truncate_y >= y + margin:
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
#   RENDER DE TEXTO GENERALES
# =============================


def draw_multiline_text_simple(c, text, x, y, w, h, font_size=10, font=None, margin=12):
    """
    Envuelve por palabras respetando ancho; respeta \n del usuario; aplica topes.
    """
    if font is None:
        font = FONT_REGULAR

    clean_text = safe_clean_text(text)

    eff_x = x + margin
    eff_y = y + margin
    eff_w = w - 2 * margin
    eff_h = h - 2 * margin
    if eff_w <= 0 or eff_h <= 0:
        return

    c.saveState()
    try:
        c.setFont(font, font_size)
        manual_lines = clean_text.split('\n')

        all_lines = []
        for manual_line in manual_lines:
            if not manual_line.strip():
                all_lines.append("")
                continue

            words = manual_line.split()
            current_line = ""
            for word in words:
                test_line = (current_line + " " +
                             word) if current_line else word
                if c.stringWidth(test_line, font, font_size) <= eff_w:
                    current_line = test_line
                else:
                    if current_line:
                        all_lines.append(current_line)
                    current_line = word

            if current_line:
                all_lines.append(current_line)

        line_height = font_size + 2
        max_lines = int(eff_h / line_height) if line_height > 0 else 0
        visible_lines = all_lines[:max_lines]

        start_y = eff_y + eff_h - font_size
        for i, line in enumerate(visible_lines):
            line_y = start_y - (i * line_height)
            if line_y < eff_y:
                break
            c.drawString(eff_x, line_y, line)

        if len(all_lines) > max_lines and max_lines > 0:
            truncate_y = start_y - (max_lines * line_height)
            if truncate_y >= eff_y:
                c.drawString(eff_x, truncate_y, "... (continúa)")
    finally:
        c.restoreState()


def draw_multiline_text(c, text, x, y, w, h, font_size=13, font=None, margin=12):
    """
    Si hay \n o texto muy largo usa método simple; si es corto, usa Paragraph/Frame.
    """
    if font is None:
        font = FONT_REGULAR

    clean_text = safe_clean_text(text)
    if '\n' in clean_text or len(clean_text) > 500:
        draw_multiline_text_simple(
            c, clean_text, x, y, w, h, font_size=font_size, font=font, margin=margin)
        return

    style = ParagraphStyle(
        name='multi',
        fontName=font,
        fontSize=font_size,
        leading=font_size + 2,
        alignment=TA_LEFT,
    )
    html_text = clean_text.replace('\n', '<br/>')

    try:
        para = Paragraph(html_text, style)
        frame = Frame(x + margin, y + margin, w - 2*margin, h - 2*margin,
                      showBoundary=0, leftPadding=4, rightPadding=4,
                      topPadding=4, bottomPadding=4)
        frame.addFromList([para], c)
    except Exception as e:
        log(f"❌ Error Paragraph/Frame: {e} → fallback simple")
        draw_multiline_text_simple(
            c, clean_text, x, y, w, h, font_size, font, margin)


def draw_single_line_text_with_bounds_corregida(c, text, x, y, w, h, font_size=14, font=None, margin=12):
    """
    Dibuja texto de una sola línea con topes y centrado vertical simple.
    """
    if font is None:
        font = FONT_REGULAR

    clean_text = safe_clean_text(text).replace('\n', ' ').replace('\r', ' ')
    if not clean_text:
        return

    eff_x = x + margin
    eff_y = y + margin
    eff_w = w - 2 * margin
    eff_h = h - 2 * margin
    if eff_w <= 0 or eff_h <= 0:
        return

    c.saveState()
    try:
        c.setFont(font, font_size)

        text_y = y + (h / 2) - (font_size / 4)
        if text_y < eff_y:
            text_y = eff_y + font_size
        elif text_y > eff_y + eff_h - font_size:
            text_y = eff_y + eff_h - font_size / 2

        max_chars = len(clean_text)
        while max_chars > 0:
            test_text = clean_text[:max_chars]
            if pdfmetrics.stringWidth(test_text, font, font_size) <= eff_w:
                break
            max_chars -= 1

        if max_chars < len(clean_text) and max_chars > 3:
            truncated_text = clean_text[:max_chars-3] + "..."
            if pdfmetrics.stringWidth(truncated_text, font, font_size) <= eff_w:
                clean_text = truncated_text
            else:
                clean_text = clean_text[:max_chars]
        elif max_chars > 0:
            clean_text = clean_text[:max_chars]
        else:
            clean_text = ""

        if clean_text:
            c.drawString(eff_x, text_y, clean_text)
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
    Formatea campos de entidades (33, 34, 35) incluyendo tipo y número de doc.
    """
    valor = mic_data.get(campo_key, "")
    if not valor:
        return ""

    if isinstance(valor, str):
        return valor

    if isinstance(valor, dict):
        partes = []
        if valor.get('nombre'):
            partes.append(valor['nombre'])
        if valor.get('direccion'):
            partes.append(valor['direccion'])

        ciudad = valor.get('ciudad', '')
        pais = valor.get('pais', '')
        if ciudad and pais:
            partes.append(f"{ciudad} - {pais}")
        elif ciudad:
            partes.append(ciudad)
        elif pais:
            partes.append(pais)

        tipo_doc = valor.get('tipo_documento', '')
        numero_doc = valor.get('numero_documento', '')
        if tipo_doc and numero_doc:
            partes.append(f"{tipo_doc}: {numero_doc}")
        elif numero_doc:
            partes.append(f"Doc: {numero_doc}")

        return '\n'.join(filter(None, partes))

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
    Campo 40 con control estricto de límites y truncamiento seguro.
    """
    if not valor:
        return

    margin = 6
    title_space = 45

    content_x = x_pt + margin
    content_y = y_pt + margin
    content_w = w_pt - 2 * margin
    content_h = h_pt - 2 * margin - title_space

    if content_w <= 0 or content_h <= 0:
        return

    font_size = 10
    font = FONT_REGULAR
    line_height = font_size + 1

    c.saveState()
    try:
        c.setFont(font, font_size)
        input_lines = safe_clean_text(valor).split('\n')
        final_lines = []

        for input_line in input_lines:
            if not input_line.strip():
                final_lines.append("")
                continue

            words = input_line.split()
            current_line = ""

            for word in words:
                test_line = (current_line + " " +
                             word) if current_line else word
                test_width = c.stringWidth(test_line, font, font_size)

                if test_width <= content_w:
                    current_line = test_line
                else:
                    if current_line:
                        final_lines.append(current_line)
                    current_line = word

                    if c.stringWidth(word, font, font_size) > content_w:
                        # si una sola palabra no entra, truncamos esa palabra
                        while word and c.stringWidth(word, font, font_size) > content_w:
                            word = word[:-1]
                        current_line = word

            if current_line:
                final_lines.append(current_line)

        max_lines = int(content_h / line_height)
        visible_lines = final_lines[:max_lines]

        start_y = content_y + content_h - font_size
        for i, line in enumerate(visible_lines):
            line_y = start_y - (i * line_height)
            if line_y >= content_y:
                c.drawString(content_x, line_y, line)

        if len(final_lines) > max_lines:
            truncate_y = start_y - (max_lines * line_height)
            if truncate_y >= content_y:
                c.drawString(content_x, truncate_y, "...")
    finally:
        c.restoreState()

# =============================
#   GENERADOR PRINCIPAL PDF
# =============================


def generar_micdta_pdf_con_datos(mic_data: dict, filename: str = "mic.pdf"):
    """
    Entry point para generar el PDF del MIC/DTA.
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
         "Marcas e números dos volumes, descrição das mercadorias", "campo_38"),
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
        draw_field_title(c, x_pt, y_pt, w_pt, h_pt, titulo, subtitulo)

        valor = obtener_valor_campo(mic_data, key, n) if key else ""

        if n in [33, 34, 35] and valor:
            valor = formatear_campo_entidad(mic_data, key)

        if n == 38:
            if valor:
                title_height_exact = 45
                fit_text_box(
                    c, valor, x=x_pt, y=y_pt, w=w_pt, h=h_pt,
                    font=FONT_REGULAR, min_font=8, max_font=14,
                    leading_ratio=1.3, margin=15, title_reserved_h=title_height_exact
                )
            continue

        if n == 40 and valor:
            draw_campo40_robust(c, x_pt, y_pt, w_pt, h_pt, valor)
            continue

        if valor:
            # Campos multilínea con contenido típico largo:
            if n in [1, 9, 33, 34, 35, 36, 37] or '\n' in valor or len(valor) > 80:
                x_frame = x_pt + FIELD_PADDING_PT
                y_frame = y_pt + FIELD_PADDING_PT
                w_frame = w_pt - 2 * FIELD_PADDING_PT
                h_frame = h_pt - 2 * FIELD_PADDING_PT - 30
                fs = 16 if n == 1 else 15 if n == 9 else 10
                draw_multiline_text_simple(
                    c, valor, x_frame, y_frame, w_frame, h_frame,
                    font_size=fs, font=FONT_REGULAR, margin=12
                )
            else:
                fs = 14
                draw_single_line_text_with_bounds_corregida(
                    c, valor, x_pt, y_pt, w_pt, h_pt, font_size=fs, font=FONT_REGULAR, margin=12
                )

    rect_pt(c, 55, 55, 1616.75, 2672.75, height_px, line_width=1)
    c.save()
    log(f"✅ PDF generado: {filename}")
