# -*- coding: utf-8 -*-
"""
MIC/DTA PDF Generator - Versión completa y robusta
- Fuentes Unicode (DejaVuSans) con fallback automático
- Helpers px→pt y coordenadas consistentes (solo trabajamos en pt dentro de dibujo)
- Ajuste de texto con búsqueda binaria (Campo 38) + márgenes y reservas de título
- Estilos cacheados y centralizados
- saveState()/restoreState() para evitar fugas de estado
- Limpieza segura de caracteres de control (sin comerse acentos)
- Refactors de cajas/títulos
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

# Relación px→pt usada en el layout original
PT_PER_PX = 0.75

# Offsets y márgenes estándar
# distancia desde el borde superior de la caja para el título
TITLE_OFFSET_PT = 24
# distancia adicional para subtítulo desde el título
SUBTITLE_OFFSET_PT = 16
FIELD_PADDING_PT = 8               # padding interno general de cajas
# altura reservada para título/subtítulo (para zonas de texto bajo títulos)
FIELD_TITLE_RESERVED_PT = 60

# Fuente por defecto (intentaremos Unicode primero)
FONT_REGULAR = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"
FALLBACK_REGULAR = "Helvetica"
FALLBACK_BOLD = "Helvetica-Bold"

# Tamaños por defecto
DEFAULT_FONT_SIZE = 12

# Debug global (activar/desactivar prints)
DEBUG = True


# =============================
#         UTILIDADES
# =============================

def px2pt(v):
    return v * PT_PER_PX


def log(msg):
    if DEBUG:
        try:
            print(msg)
        except UnicodeEncodeError:
            # Fallback para consolas que no soportan Unicode
            print(msg.encode('ascii', 'replace').decode('ascii'))


def safe_clean_text(text: str) -> str:
    """
    Limpieza universal: normaliza saltos de línea y remueve caracteres de control problemáticos
    (excepto \n y \t). NO elimina acentos ni caracteres Unicode válidos.
    """
    if text is None:
        return ""
    t = text.replace('\r\n', '\n').replace('\r', '\n')
    # Remover controles ASCII (mantiene \n y \t)
    t = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', t)
    return t


def find_ttf_candidate_paths():
    """
    Intenta descubrir rutas típicas de DejaVuSans en Linux/Mac/Windows.
    """
    candidates = [
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        # Windows (Microsoft Store Python no siempre ve Windows Fonts; probamos copias locales)
        os.path.expanduser(
            "~/AppData/Local/Microsoft/Windows/Fonts/DejaVuSans.ttf"),
        os.path.expanduser(
            "~/AppData/Local/Microsoft/Windows/Fonts/DejaVuSans-Bold.ttf"),
        # Windows ruta global (si el usuario instaló fuentes TTF)
        "C:\\Windows\\Fonts\\DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\DejaVuSans-Bold.ttf",
        # Mac
        "/Library/Fonts/DejaVuSans.ttf",
        "/Library/Fonts/DejaVuSans-Bold.ttf",
    ]
    return candidates


def _fonts_registered() -> bool:
    """Verifica si las fuentes actuales están registradas en reportlab."""
    try:
        regs = set(pdfmetrics.getRegisteredFontNames())
        return (FONT_REGULAR in regs) and (FONT_BOLD in regs)
    except Exception:
        return False


def register_unicode_fonts():
    """
    Registra DejaVuSans (regular y bold). Si falla, deja Helvetica como fallback silencioso.
    """
    global FONT_REGULAR, FONT_BOLD
    try:
        # Si ya están registradas, no volver a registrar
        already = FONT_REGULAR in pdfmetrics.getRegisteredFontNames(
        ) and FONT_BOLD in pdfmetrics.getRegisteredFontNames()
        if already:
            log("ℹ️ Fuentes DejaVuSans ya registradas.")
            return

        # Intentar encontrar archivos
        regs = find_ttf_candidate_paths()
        reg_path = None
        bold_path = None
        for p in regs:
            if os.path.exists(p):
                if p.lower().endswith("dejavusans.ttf"):
                    reg_path = p
                elif p.lower().endswith("dejavusans-bold.ttf"):
                    bold_path = p

        if reg_path and bold_path:
            pdfmetrics.registerFont(TTFont(FONT_REGULAR, reg_path))
            pdfmetrics.registerFont(TTFont(FONT_BOLD, bold_path))
            log(f"✅ Fuentes Unicode registradas: {reg_path}, {bold_path}")
        else:
            # Si no encontramos ambas, caer a Helvetica
            FONT_REGULAR = FALLBACK_REGULAR
            FONT_BOLD = FALLBACK_BOLD
            log("⚠️ No se encontraron DejaVuSans TTF; usando Helvetica como fallback.")
    except Exception as e:
        FONT_REGULAR = FALLBACK_REGULAR
        FONT_BOLD = FALLBACK_BOLD
        log(
            f"⚠️ No se pudieron registrar TTF Unicode ({e}); usando Helvetica.")


# Registrar fuentes al importar el módulo (evita 500 si se usa como librería)
register_unicode_fonts()


# =============================
#         ESTILOS CACHE
# =============================

_STYLES = None


def get_styles():
    """
    Cachea y devuelve estilos ParagraphStyle listos con fuentes Unicode (o fallback).
    """
    global _STYLES
    if _STYLES is not None:
        return _STYLES

    ss = getSampleStyleSheet()
    # Overwrite defaults to ensure Unicode-capable font
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
#          DIBUJO BASE
# =============================

def rect_pt(c, x_px, y_px, w_px, h_px, height_px, line_width=1.0, show=True):
    """
    Dibuja un rectángulo usando coordenadas en px del layout original,
    transformadas a pt. Devuelve (x_pt, y_pt, w_pt, h_pt).
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
    """
    Dibuja título y subtítulo en la parte superior de una caja ya creada (en pt).
    Defaults resueltos en tiempo de ejecución para evitar capturar fuentes no registradas.
    """
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
    # devuelve coordenadas útiles por si se usan
    return (x_pt + FIELD_PADDING_PT, y_pt + FIELD_PADDING_PT, w_pt - 2*FIELD_PADDING_PT, h_pt - 2*FIELD_PADDING_PT)


# =============================
#   AJUSTE DE TEXTO (CAMPO 38)
# =============================

def fit_text_box(c, text, x, y, w, h, font=None, min_font=8, max_font=14, leading_ratio=1.3, margin=12, title_reserved_h=0):
    """
    Ajusta texto a un rectángulo (pt) con búsqueda binaria de tamaño de fuente.
    Respeta saltos de línea del usuario y hace wrap por palabras.
    Dibuja el texto al final. Devuelve dict con info de renderizado.
    Permite reservar espacio para un título en la parte superior.
    """
    if font is None:
        font = FONT_REGULAR

    text = safe_clean_text(text)
    if not text:
        return {'font_size_used': min_font, 'lines_drawn': 0, 'truncated': False, 'effective_area': f"{w:.1f}x{h:.1f}"}

    eff_w = w - 2 * margin
    # Restar la altura del título del área efectiva
    eff_h = h - 2 * margin - title_reserved_h
    if eff_w <= 0 or eff_h <= 0:
        return {'font_size_used': min_font, 'lines_drawn': 0, 'truncated': True, 'effective_area': f"{w:.1f}x{h:.1f}"}

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

    # Búsqueda binaria para encontrar el tamaño de fuente óptimo
    while lo <= hi:
        mid = (lo + hi) // 2
        lines = wrap_for_size(mid)
        lh = mid * leading_ratio
        total_h = lh * len(lines)

        if total_h <= eff_h:
            # El texto cabe con este tamaño, intentar uno más grande
            best_sz, best_lines = mid, lines
            lo = mid + 1
        else:
            # El texto no cabe, probar con tamaño más pequeño
            hi = mid - 1

    # Si no encontramos un tamaño que funcione, usar el mínimo
    if not best_lines:
        best_sz = min_font
        best_lines = wrap_for_size(best_sz)

    c.saveState()
    try:
        c.setFont(font, best_sz)
        lh = best_sz * leading_ratio
        start_x = x + margin

        # Posicionar el texto desde la parte superior del área efectiva
        # (debajo del área reservada para título)
        start_y = y + h - margin - title_reserved_h - best_sz

        max_lines = int(eff_h // lh) if lh > 0 else 0
        drawn = best_lines[:max_lines]
        truncated = len(best_lines) > max_lines

        for i, ln in enumerate(drawn):
            line_y = start_y - i * lh
            # Verificar que la línea esté dentro de los límites
            if line_y < y + margin:
                break
            c.drawString(start_x, line_y, ln)

        # Indicador de truncamiento solo si hay espacio
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
#      MULTILÍNEA GENERALES
# =============================

def draw_multiline_text_simple(c, text, x, y, w, h, font_size=9, font=None, margin=12):
    """
    Método simple con manejo explícito de \n (sin Frame).
    Envuelve por palabras respetando el ancho.
    Aplica topes (márgenes) en todos los lados.
    Defaults resueltos en tiempo de ejecución.
    """
    if font is None:
        font = FONT_REGULAR

    clean_text = safe_clean_text(text)

    # Aplicar topes/márgenes en todos los lados
    eff_x = x + margin
    eff_y = y + margin
    eff_w = w - 2 * margin
    eff_h = h - 2 * margin

    # Verificar que el área efectiva sea válida
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
            # Verificar que la línea esté dentro de los límites verticales
            if line_y < eff_y:
                break
            c.drawString(eff_x, line_y, line)

        # Indicador de truncamiento solo si hay espacio
        if len(all_lines) > max_lines and max_lines > 0:
            truncate_y = start_y - (max_lines * line_height)
            if truncate_y >= eff_y:
                c.drawString(eff_x, truncate_y, "... (continúa)")
    finally:
        c.restoreState()


def draw_multiline_text(c, text, x, y, w, h, font_size=13, font=None, margin=12):
    """
    Método híbrido:
    - Si hay saltos de línea o texto muy largo, usa método simple (sin Frame)
    - Caso contrario (texto corto), usa Paragraph/Frame para mejor calidad
    - Aplica topes/márgenes consistentes en ambos casos
    Defaults resueltos en tiempo de ejecución.
    """
    if font is None:
        font = FONT_REGULAR

    clean_text = safe_clean_text(text)
    if '\n' in clean_text or len(clean_text) > 500:
        log(f"🎯 Texto con saltos o largo ({len(clean_text)} chars) → método simple")
        draw_multiline_text_simple(
            c, clean_text, x, y, w, h, font_size=font_size, font=font, margin=margin)
        return

    log(f"🔍 Texto corto ({len(clean_text)} chars) → método Frame")
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
        # Aplicar topes/márgenes al Frame también
        frame = Frame(x + margin, y + margin, w - 2*margin, h - 2*margin,
                      showBoundary=0, leftPadding=4, rightPadding=4,
                      topPadding=4, bottomPadding=4)
        frame.addFromList([para], c)
    except Exception as e:
        log(f"❌ Error en Paragraph/Frame: {e} → fallback simple")
        draw_multiline_text_simple(
            c, clean_text, x, y, w, h, font_size, font, margin)


def draw_single_line_text_with_bounds(c, text, x, y, w, h, font_size=14, font=None, margin=12):
    """
    Dibuja texto de una sola línea con topes en todos los lados.
    Trunca el texto si es necesario para que no se salga de los límites.
    Posiciona el texto correctamente debajo del área de título.
    """
    if font is None:
        font = FONT_REGULAR

    clean_text = safe_clean_text(text).replace('\n', ' ').replace('\r', ' ')
    if not clean_text:
        return

    # Aplicar topes/márgenes
    eff_x = x + margin
    eff_y = y + margin
    eff_w = w - 2 * margin
    eff_h = h - 2 * margin

    # Verificar que el área efectiva sea válida
    if eff_w <= 0 or eff_h <= 0:
        return

    c.saveState()
    try:
        c.setFont(font, font_size)

        # Posicionar el texto en la parte superior del área efectiva (debajo del título)
        # Usar la misma lógica que los otros campos para consistencia
        text_y = y + h - TITLE_OFFSET_PT - SUBTITLE_OFFSET_PT - 34

        # Verificar que esté dentro de los límites verticales
        if text_y < eff_y or text_y > eff_y + eff_h:
            return

        # Verificar que el texto quepa horizontalmente, truncar si es necesario
        max_chars = len(clean_text)
        while max_chars > 0:
            test_text = clean_text[:max_chars]
            if c.stringWidth(test_text, font, font_size) <= eff_w:
                break
            max_chars -= 1

        if max_chars < len(clean_text) and max_chars > 3:
            # Agregar "..." si se truncó
            truncated_text = clean_text[:max_chars-3] + "..."
            if c.stringWidth(truncated_text, font, font_size) <= eff_w:
                clean_text = truncated_text
            else:
                clean_text = clean_text[:max_chars]
        elif max_chars > 0:
            clean_text = clean_text[:max_chars]
        else:
            clean_text = ""

        # Dibujar el texto solo si hay espacio y está dentro de los límites
        if clean_text:
            c.drawString(eff_x, text_y, clean_text)

    finally:
        c.restoreState()


# =============================
#         CAMPO 39 (firma)
# =============================

def normalized_date(mic_data):
    """
    Devuelve fecha para Campo 39 desde mic_data si existe; si no, hoy.
    """
    for k in ('campo_6_fecha', 'fecha_emision', 'fecha'):
        v = (mic_data or {}).get(k, '')
        if v:
            return v
    return datetime.now().strftime('%d/%m/%Y')


def draw_campo39(c, x_px, y_px, w_px, h_px, height_px, mic_data=None):
    """
    Campo 39: texto legal, línea de firma y transportador + fecha.
    Usa estilos cacheados y Unicode.
    """
    styles = get_styles()
    X, Y, W, H = px2pt(x_px), px2pt(
        height_px - y_px - h_px), px2pt(w_px), px2pt(h_px)

    # Rectángulo (no hay títulos aquí)
    c.saveState()
    try:
        c.rect(X, Y, W, H)
    finally:
        c.restoreState()

    # Textos legales
    txt_es = ("Declaramos que las informaciones presentadas en este Documento son expresión de verdad, "
              "que los datos referentes a las mercaderías fueron transcriptos exactamente conforme a la "
              "declaración del remitente, las cuales son de su exclusiva responsabilidad, y que esta operación "
              "obedece a lo dispuesto en el Convenio sobre Transporte Internacional Terrestre de los países del Cono Sur.")
    txt_pt = ("Declaramos que as informações prestadas neste Documento são a expressão de verdade que os dados referentes "
              "às mercadorias foram transcritos exatamente conforme a declaração do remetente, os quais são de sua exclusiva "
              "responsabilidade, e que esta operação obedece ao disposto no Convênio sobre Transporte Internacional Terrestre.")
    txt_firma = "39 Firma y sello del porteador / Assinatura e carimbo do transportador"

    # Transportador y fecha
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

    if DEBUG:
        log(f"🚛 Campo 39 - Transportador: '{nombre_transportador}'")
        log(f"📅 Campo 39 - Fecha: '{fecha_actual}'")

    # Crear párrafos y dibujar
    para_es = Paragraph(txt_es, styles['es'])
    para_pt = Paragraph(txt_pt, styles['es'])
    para_firma = Paragraph(txt_firma, styles['firma'])
    para_transportador = Paragraph(
        nombre_transportador, styles['transportador'])

    # Frame para el bloque completo (con padding interno)
    c.saveState()
    try:
        f = Frame(X + FIELD_PADDING_PT, Y + FIELD_PADDING_PT, W - 2 *
                  FIELD_PADDING_PT, H - 2*FIELD_PADDING_PT, showBoundary=0)
        f.addFromList([para_es, para_pt, para_firma, para_transportador], c)
    finally:
        c.restoreState()

    # Fecha en la parte inferior izquierda
    c.saveState()
    try:
        c.setFont(FONT_REGULAR, 12)
        c.drawString(X + FIELD_PADDING_PT + 4, Y + 25,
                     f"Data / Fecha: {fecha_actual}")
    finally:
        c.restoreState()


# =============================
#    FUNCIÓN ESPECIALIZADA CAMPO 40
# =============================

def draw_campo40_robust(c, x_pt, y_pt, w_pt, h_pt, valor):
    """
    Función robusta específicamente para el Campo 40.
    Garantiza que el texto se mantenga dentro de los límites.
    """
    if not valor:
        return

    log("🎯 Campo 40: Usando función robusta")

    # Área de contenido
    margin = 6  # Margen más pequeño para Campo 40
    title_space = 45  # Espacio reservado para título

    content_x = x_pt + margin
    content_y = y_pt + margin
    content_w = w_pt - 2 * margin
    content_h = h_pt - 2 * margin - title_space

    if content_w <= 0 or content_h <= 0:
        log(f"❌ Área de contenido inválida: {content_w}x{content_h}")
        return

    # Parámetros optimizados
    font_size = 10
    font = FONT_REGULAR
    line_height = font_size + 1

    c.saveState()
    try:
        c.setFont(font, font_size)

        # Procesar texto línea por línea
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

                    # Verificar si una sola palabra es muy larga
                    if c.stringWidth(word, font, font_size) > content_w:
                        # Truncar palabra larga
                        while word and c.stringWidth(word, font, font_size) > content_w:
                            word = word[:-1]
                        current_line = word

            if current_line:
                final_lines.append(current_line)

        # Calcular cuántas líneas caben
        max_lines = int(content_h / line_height)
        visible_lines = final_lines[:max_lines]

        # Dibujar líneas
        start_y = content_y + content_h - font_size
        for i, line in enumerate(visible_lines):
            line_y = start_y - (i * line_height)
            if line_y >= content_y:  # Verificar límites
                c.drawString(content_x, line_y, line)

        # Indicador de truncamiento
        if len(final_lines) > max_lines:
            truncate_y = start_y - (max_lines * line_height)
            if truncate_y >= content_y:
                c.drawString(content_x, truncate_y, "...")

        log(f"✅ Campo 40 procesado: {len(visible_lines)}/{len(final_lines)} líneas")

    finally:
        c.restoreState()


# =============================
#   GENERADOR PRINCIPAL PDF
# =============================

def generar_micdta_pdf_con_datos(mic_data, filename="mic_{id}.pdf"):
    # Garantizar registro por si el módulo se importó antes de tener las fuentes
    register_unicode_fonts()

    log("🔄 Iniciando generación de PDF MIC...")
    log(f"📋 Campos recibidos: {len(mic_data or {})}")

    # Debug: mostrar campos no vacíos
    if DEBUG and mic_data:
        log("\n" + "="*50)
        log("🔍 DATOS COMPLETOS RECIBIDOS (no vacíos):")
        for key, value in mic_data.items():
            if value:
                s = str(value)
                log(f"  {key}: {s[:100]}{'...' if len(s) > 100 else ''}")
        log("="*50 + "\n")

    # Resolución base
    width_px, height_px = 1700, 2800
    width_pt, height_pt = px2pt(width_px), px2pt(height_px)

    # Preparar canvas
    c = canvas.Canvas(filename, pagesize=(width_pt, height_pt))
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)

    # Encabezado
    x0, y0 = 55, 55
    rect_w, rect_h = 1616, 108.5
    # Caja externa del encabezado
    rect_pt(c, x0, y0, rect_w, rect_h, height_px, line_width=2)
    # Caja MIC/DTA
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

    # DEFINICIÓN DE CAMPOS
    campos = [
        (1,  55, 162, 863, 450, "1 Nombre y domicilio del porteador",
         "Nome e endereço do transportador", "campo_1_transporte"),
        (2,  55, 610, 861, 142, "2 Rol de contribuyente",
         "Cadastro geral de contribuintes", "campo_2_numero"),
        (3, 916, 162, 389, 169, "3 Tránsito aduanero", "Trânsito aduaneiro", None),
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
         "CAMINHÃO SUBSTITUTO: Nome e endereço do", "campo_16_asteriscos_1"),
        (17, 915, 915, 395, 140, "17 Rol de contribuyente",
         "Cadastro geral de", "campo_17_asteriscos_2"),
        (18, 1310, 915, 360, 140, "18 Placa del camión",
         "Placa do", "campo_18_asteriscos_3"),
        (19, 915, 1055, 395, 140, "19 Marca y número",
         "Marca e número", "campo_19_asteriscos_4"),
        (20, 1310, 1055, 360, 140, "20 Capacidad de arrastre",
         "Capacidade de tração", "campo_20_asteriscos_5"),
        (21, 915, 1195, 395, 135, "21 AÑO", "ANO", "campo_21_asteriscos_6"),
        (22, 1310, 1195, 360, 135, "22 Semirremolque / Remolque",
         "Semi-reboque / Reboque", "campo_22_asteriscos_7"),
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

    # LOOP DE CAMPOS COMPLETO CORREGIDO
    for n, x, y, w, h, titulo, subtitulo, key in campos:
        if n == 39:
            # Campo 39 especial
            draw_campo39(c, x, y, w, h, height_px, mic_data)
            continue

        # Caja
        x_pt, y_pt, w_pt, h_pt = rect_pt(
            c, x, y, w, h, height_px, line_width=1)

        # Títulos (si hay)
        tx_pt, ty_pt, tw_pt, th_pt = draw_field_title(
            c, x_pt, y_pt, w_pt, h_pt, titulo, subtitulo)

        # Campo 38: ajuste dinámico de fuente con posicionamiento exacto
        if n == 38:
            log(f"🎯 PROCESANDO CAMPO 38 (posicionamiento exacto)")
            valor = (mic_data or {}).get(key, "")

            title_height_exact = 45  # 24pt + 16pt + 5pt espacio mínimo

            fit = fit_text_box(
                c,
                valor,
                x=x_pt,
                y=y_pt,
                w=w_pt,
                h=h_pt,
                font=FONT_REGULAR,
                min_font=8,
                max_font=14,
                leading_ratio=1.3,
                margin=15,
                title_reserved_h=title_height_exact
            )
            log(f"✅ Campo 38 → fuente {fit['font_size_used']}, líneas {fit['lines_drawn']}, truncado={fit['truncated']}")
            continue

        # Campo 40: Usar función robusta especializada
        if n == 40 and key and (mic_data or {}).get(key):
            draw_campo40_robust(c, x_pt, y_pt, w_pt, h_pt, mic_data[key])
            continue

        # Campos multilínea con documentos (1, 9, 33, 34, 35)
        if n in [1, 9, 33, 34, 35] and key and (mic_data or {}).get(key):
            log(f"🖼️ Campo multilínea {n} con topes aplicados")

            # Área interna segura para texto (debajo de título)
            x_frame = x_pt + FIELD_PADDING_PT
            y_frame = y_pt + FIELD_PADDING_PT
            w_frame = w_pt - 2 * FIELD_PADDING_PT
            h_frame = h_pt - 2 * FIELD_PADDING_PT - 30  # margen extra para no pisar títulos

            # Tamaños específicos solicitados:
            #  - Campo 1: 16 pt
            #  - Campo 9: 15 pt
            #  - Otros multilínea (33,34,35): 10 pt
            if n == 1:
                font_size_multiline = 16
            elif n == 9:
                font_size_multiline = 15
            else:
                font_size_multiline = 10

            log(f"   ➜ Usando font_size={font_size_multiline}pt en campo {n} con topes")

            # Usamos SIEMPRE el método simple con topes aplicados
            draw_multiline_text_simple(
                c,
                mic_data[key],
                x_frame,
                y_frame,
                w_frame,
                h_frame,
                font_size=font_size_multiline,
                font=FONT_REGULAR,
                margin=12  # Aplicar topes de 12pt en todos los lados
            )
            continue

        # Campo 12: lógica de 2 líneas con topes aplicados
        if n == 12 and key and (mic_data or {}).get(key):
            val = str(mic_data[key])
            lines = val.split('\n')

            # Aplicar topes/márgenes
            margin = 12
            eff_x = x_pt + margin
            eff_y = y_pt + margin
            eff_w = w_pt - 2 * margin
            eff_h = h_pt - 2 * margin

            log(f"🔤 Campo 12 (2 líneas) con topes aplicados")

            c.saveState()
            try:
                if len(lines) >= 1 and eff_w > 0 and eff_h > 0:
                    c.setFont(FONT_REGULAR, 12)
                    # Posición de primera línea con topes
                    line1_y = y_pt + h_pt - TITLE_OFFSET_PT - SUBTITLE_OFFSET_PT - 34
                    # Verificar que esté dentro de los límites verticales
                    if line1_y >= eff_y and line1_y <= eff_y + eff_h:
                        # Truncar texto si es muy largo para el ancho disponible
                        text1 = lines[0]
                        max_chars = len(text1)
                        while max_chars > 0:
                            test_text = text1[:max_chars]
                            if c.stringWidth(test_text, FONT_REGULAR, 12) <= eff_w:
                                break
                            max_chars -= 1
                        if max_chars > 0:
                            c.drawString(eff_x, line1_y, text1[:max_chars])

                if len(lines) >= 2 and lines[1].strip() and eff_w > 0 and eff_h > 0:
                    c.setFont(FONT_REGULAR, 11)
                    # Posición de segunda línea con topes
                    line2_y = y_pt + h_pt - TITLE_OFFSET_PT - SUBTITLE_OFFSET_PT - 50
                    # Verificar que esté dentro de los límites verticales
                    if line2_y >= eff_y and line2_y <= eff_y + eff_h:
                        # Truncar texto si es muy largo para el ancho disponible
                        text2 = lines[1]
                        max_chars = len(text2)
                        while max_chars > 0:
                            test_text = text2[:max_chars]
                            if c.stringWidth(test_text, FONT_REGULAR, 11) <= eff_w:
                                break
                            max_chars -= 1
                        if max_chars > 0:
                            c.drawString(eff_x, line2_y, text2[:max_chars])
            finally:
                c.restoreState()
            continue

        # Campos normales con topes aplicados
        if key and (mic_data or {}).get(key):
            valor = str(mic_data[key])
            size = 14
            if n == 12 and len(valor) > 50:
                size = 11

            # Determinar si el campo necesita multilínea basado en longitud del texto
            # Campos como 36, 37 que suelen tener texto largo necesitan multilínea
            needs_multiline = (
                len(valor) > 80 or  # Texto largo
                # Campos específicos que suelen tener texto largo
                n in [36, 37] or
                '\n' in valor  # Texto con saltos de línea explícitos
            )

            if needs_multiline:
                log(f"🖼️ Campo {n} (multilínea automática) con topes aplicados")

                # Área interna segura para texto (debajo de título)
                x_frame = x_pt + FIELD_PADDING_PT
                y_frame = y_pt + FIELD_PADDING_PT
                w_frame = w_pt - 2 * FIELD_PADDING_PT
                h_frame = h_pt - 2 * FIELD_PADDING_PT - 30  # margen extra para no pisar títulos

                # Usar método multilínea con topes
                draw_multiline_text_simple(
                    c,
                    valor,
                    x_frame,
                    y_frame,
                    w_frame,
                    h_frame,
                    font_size=size,
                    font=FONT_REGULAR,
                    margin=12  # Aplicar topes de 12pt en todos los lados
                )
            else:
                log(f"🔤 Campo {n} (una línea) con topes aplicados")

                # Área para texto (debajo de título/subtítulo)
                text_x = x_pt
                text_y = y_pt
                text_w = w_pt
                text_h = h_pt - FIELD_TITLE_RESERVED_PT  # Reservar espacio para título

                # Usar la nueva función con topes
                draw_single_line_text_with_bounds(
                    c, valor, text_x, text_y, text_w, text_h,
                    font_size=size, font=FONT_REGULAR, margin=12
                )

    # Rectángulo grande externo
    rect_pt(c, 55, 55, 1616.75, 2672.75, height_px, line_width=1)

    c.save()
    log(f"✅ PDF generado exitosamente: {filename}")

    # Resumen final (opcional)
    if DEBUG:
        campos_documentos = {
            'campo_1_transporte': 'Transportador',
            'campo_33_datos_campo1_crt': 'Remitente',
            'campo_34_datos_campo4_crt': 'Destinatario',
            'campo_35_datos_campo6_crt': 'Consignatario'
        }
        log("🎯 RESUMEN DE CAMPOS CON DOCUMENTOS:")
        for key, descripcion in campos_documentos.items():
            val = (mic_data or {}).get(key)
            if val:
                lines_count = len(safe_clean_text(val).split('\n'))
                log(f"   📋 {descripcion}: {lines_count} líneas")
            else:
                log(f"   ❌ {descripcion}: Sin datos")

        log("🎯 RESUMEN - MÉTODO DE RENDERIZADO CON TOPES:")
        log("   📋 Campos 1, 9, 33, 34, 35 → Multilínea con topes (12pt) ✅")
        log("   📦 Campo 38 → Ajuste dinámico con topes (15pt) ✅")
        log("   🎯 Campo 40 → Función robusta con topes (6pt) ✅")
        log("   📄 Campo 12 → 2 líneas con topes (12pt) ✅")
        log("   🔤 Otros campos → 1 línea con topes (12pt) ✅")
        log("   🛡️ TODOS LOS CAMPOS CON TOPES APLICADOS ✅")
        log("   🔍 Debug completo: ACTIVADO ✅")


# =============================
#          PRUEBA LOCAL
# =============================

def test_campo38():
    """
    Prueba de Campo 38 con texto largo y verificación de generación de PDF.
    """
    log("🧪 INICIANDO PRUEBA DEL CAMPO 38 (versión completa)")
    test_data = {
        'campo_38_datos_campo11_crt': (
            "1572 CAJAS QUE DICEN CONTENER: CARNE RESFRIADA DE BOVINO SEM OSSO "
            "15 CAJAS DE CONTRA FILE (BIFES) (STEAK CHORIZO) (ESTANCIA 92); 42 CAJAS DE CONTRA FILE "
            "(BIFES) (STEAK CHORIZO) (ESTANCIA 92); 42 CAJAS DE CONTRA FILE (BIFES) (STEAK CHORIZO) "
            "(ESTANCIA 92); 158 CAJAS DE BIFE ANCHO CON HUESO (COSTELA JANELA) (ESTANCIA 92); "
            "42 CAJAS DE PICANHA (TAPA DE CUADRIL) (ESTANCIA 92); 42 CAJAS DE LOMO (FILE MIGNON) "
            "(ESTANCIA 92); 126 CAJAS DE EYE OF ROUND (PECETO) (ESTANCIA 92); 84 CAJAS DE ASADO DE TIRA "
            "(COSTELA JANELA) (ESTANCIA 92); 84 CAJAS DE EYE OF ROUND (PECETO) (ESTANCIA 92) ..."
        ),
        'campo_1_transporte': 'EMPRESA TRANSPORTADORA TEST\nRUA TESTE 123\nCIUDAD - PAÍS',
        'campo_6_fecha': '02/08/2025'
    }
    out = "test_campo38_corregido.pdf"
    generar_micdta_pdf_con_datos(test_data, out)
    if os.path.exists(out):
        log(f"✅ PRUEBA EXITOSA: generado {out}")
    else:
        log("❌ PRUEBA FALLÓ: no se encontró el PDF")


def test_campo40_desbordamiento():
    """
    Prueba específica para el campo 40 que se desborda.
    """
    log("🧪 INICIANDO PRUEBA DEL CAMPO 40 (desbordamiento)")
    test_data = {
        'campo_40_tramo': (
            "ORIGEN: CAMPESTRE S.A.-CIUDAD DEL ESTE SALIDA: CIUDAD DEL ESTE-CIUDAD DEL ESTE "
            "DESTINO: PUERTO DE SANTOS-BRASIL RUTA: BR-277, BR-116, SP-150 "
            "PLAZO: 72 HORAS DESDE LA SALIDA"
        ),
        'campo_1_transporte': 'EMPRESA TRANSPORTADORA TEST',
        'campo_6_fecha': '02/08/2025'
    }
    out = "test_campo40_topes.pdf"
    generar_micdta_pdf_con_datos(test_data, out)
    if os.path.exists(out):
        log(f"✅ PRUEBA CAMPO 40 EXITOSA: generado {out}")
    else:
        log("❌ PRUEBA CAMPO 40 FALLÓ: no se encontró el PDF")


def test_campo38_ajuste_dinamico():
    """
    Prueba del ajuste dinámico de tamaño en campo 38 con diferentes cantidades de texto.
    """
    log("🧪 INICIANDO PRUEBA CAMPO 38 - AJUSTE DINÁMICO DE TAMAÑO")

    # Texto corto - debería usar fuente grande (cerca de 14pt)
    test_data_corto = {
        'campo_38_datos_campo11_crt': "TEXTO CORTO PARA PROBAR FUENTE GRANDE",
        'campo_1_transporte': 'EMPRESA TEST',
        'campo_6_fecha': '02/08/2025'
    }

    # Texto medio - debería usar fuente intermedia
    test_data_medio = {
        'campo_38_datos_campo11_crt': (
            "TEXTO MEDIO PARA PROBAR AJUSTE AUTOMÁTICO DE FUENTE. "
            "ESTE TEXTO TIENE MÁS CONTENIDO QUE EL ANTERIOR PERO NO ES EXCESIVAMENTE LARGO. "
            "DEBERÍA USAR UNA FUENTE INTERMEDIA ENTRE 8 Y 14 PUNTOS."
        ),
        'campo_1_transporte': 'EMPRESA TEST',
        'campo_6_fecha': '02/08/2025'
    }

    # Texto largo - debería usar fuente pequeña (cerca de 8pt)
    test_data_largo = {
        'campo_38_datos_campo11_crt': (
            "1572 CAJAS QUE DICEN CONTENER: CARNE RESFRIADA DE BOVINO SEM OSSO "
            "15 CAJAS DE CONTRA FILE (BIFES) (STEAK CHORIZO) (ESTANCIA 92); 42 CAJAS DE CONTRA FILE "
            "(BIFES) (STEAK CHORIZO) (ESTANCIA 92); 42 CAJAS DE CONTRA FILE (BIFES) (STEAK CHORIZO) "
            "(ESTANCIA 92); 158 CAJAS DE BIFE ANCHO CON HUESO (COSTELA JANELA) (ESTANCIA 92); "
            "42 CAJAS DE PICANHA (TAPA DE CUADRIL) (ESTANCIA 92); 42 CAJAS DE LOMO (FILE MIGNON) "
            "(ESTANCIA 92); 126 CAJAS DE EYE OF ROUND (PECETO) (ESTANCIA 92); 84 CAJAS DE ASADO DE TIRA "
            "(COSTELA JANELA) (ESTANCIA 92); 84 CAJAS DE EYE OF ROUND (PECETO) (ESTANCIA 92); "
            "PESO BRUTO: 3.904,614 KG; PESO NETO: 3.654,574 KG; NCM: 0201.20.00; "
            "FACTURA COMERCIAL: 001-002-0000954; CERTIFICADO SANITARIO: SENACSA-2025-001"
        ),
        'campo_1_transporte': 'EMPRESA TEST',
        'campo_6_fecha': '02/08/2025'
    }

    # Generar PDFs para cada caso
    casos = [
        (test_data_corto, "test_campo38_texto_corto.pdf", "CORTO"),
        (test_data_medio, "test_campo38_texto_medio.pdf", "MEDIO"),
        (test_data_largo, "test_campo38_texto_largo.pdf", "LARGO")
    ]

    for data, filename, tipo in casos:
        log(f"\n--- GENERANDO PDF PARA TEXTO {tipo} ---")
        generar_micdta_pdf_con_datos(data, filename)
        if os.path.exists(filename):
            log(f"✅ PRUEBA TEXTO {tipo} EXITOSA: generado {filename}")
        else:
            log(f"❌ PRUEBA TEXTO {tipo} FALLÓ: no se encontró {filename}")

    log("\n🎯 RESUMEN: Se generaron 3 PDFs para demostrar el ajuste dinámico de fuente")
    log("   📄 Texto corto → fuente grande (cerca de 14pt)")
    log("   📄 Texto medio → fuente intermedia (10-12pt)")
    log("   📄 Texto largo → fuente pequeña (cerca de 8pt)")
    log("   📍 En todos los casos, el texto empieza justo debajo del título")


# =============================
#        PUNTO DE ENTRADA
# =============================

if __name__ == "__main__":
    # 1) Registrar fuentes Unicode (DejaVuSans) con fallback automático
    register_unicode_fonts()

    log("📋 CÓDIGO COMPLETO MIC/DTA PDF - Versión robusta")
    log("🎯 Highlights:")
    log("   ✅ Campo 38 con ajuste dinámico (búsqueda binaria) y márgenes")
    log("   ✅ Fuentes Unicode (DejaVuSans) para acentos/ñ/ç")
    log("   ✅ Helpers px→pt y coordenadas consistentes")
    log("   ✅ saveState()/restoreState() para aislar estilos")
    log("   ✅ Estilos cacheados y refactors de cajas/títulos")
    log("   ✅ Debug detallado activable")

    # 2) Ejecutar prueba opcional:
    # test_campo38()

    # Si querés generar con tus datos reales:
    # mic_data = {...}
    # generar_micdta_pdf_con_datos(mic_data, "mic_real.pdf")
