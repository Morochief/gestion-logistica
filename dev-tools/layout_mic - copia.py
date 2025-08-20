from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT


def draw_campo39(c, x, y, w, h, height_px, pt_per_px):
    X = x * pt_per_px
    Y = (height_px - y - h) * pt_per_px
    W = w * pt_per_px
    H = h * pt_per_px

    styles = getSampleStyleSheet()
    style_es = ParagraphStyle('es',
                              parent=styles['Normal'],
                              fontName='Helvetica-Bold',
                              fontSize=11,
                              leading=13,
                              alignment=TA_LEFT,
                              leftIndent=0, rightIndent=0,
                              spaceAfter=3,
                              spaceBefore=0
                              )
    style_pt = ParagraphStyle('pt',
                              parent=styles['Normal'],
                              fontName='Helvetica',
                              fontSize=10,
                              leading=12,
                              alignment=TA_LEFT,
                              leftIndent=0, rightIndent=0,
                              spaceAfter=3,
                              spaceBefore=0
                              )
    style_firma = ParagraphStyle('firma',
                                 parent=styles['Normal'],
                                 fontName='Helvetica-Bold',
                                 fontSize=11,
                                 leading=13,
                                 alignment=TA_LEFT,
                                 leftIndent=0, rightIndent=0,
                                 spaceAfter=0,
                                 spaceBefore=10
                                 )

    txt_es = (
        "Declaramos que las informaciones presentadas en este Documento son expresión de verdad, "
        "que los datos referentes a las mercaderías fueron transcriptos exactamente conforme a la "
        "declaración del remitente, las cuales son de su exclusiva responsabilidad, y que esta operación "
        "obedece a lo dispuesto en el Convenio sobre Transporte Internacional Terrestre de los países del Cono Sur."
    )
    txt_pt = (
        "Declaramos que as informações prestadas neste Documento são a expressão de verdade que os dados referentes "
        "as mercadorias foram transcritos exatamente conforme a declaração do remetente, os quais são de sua exclusiva "
        "responsabilidade, e que esta operação obedece ao disposto no Convênio sobre Transporte Internacional Terrestre dos"
    )
    txt_firma = "39 Firma y sello del porteador / Assinatura e carimbo do"

    para_es = Paragraph(txt_es, style_es)
    para_pt = Paragraph(txt_pt, style_pt)
    para_firma = Paragraph(txt_firma, style_firma)
    f = Frame(X+8, Y+8, W-16, H-16, showBoundary=0)
    f.addFromList([para_es, para_pt, para_firma], c)


def draw_micdta_pdf(filename="micdta.pdf"):
    width_px, height_px = 1700, 2800
    pt_per_px = 0.75
    width_pt, height_pt = width_px * pt_per_px, height_px * pt_per_px

    c = canvas.Canvas(filename, pagesize=(width_pt, height_pt))
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)

    # ENCABEZADO
    x0, y0 = 55, 55
    rect_w, rect_h = 1616, 108.5
    c.setLineWidth(2)
    c.rect(x0 * pt_per_px, (height_px - y0 - rect_h) *
           pt_per_px, rect_w * pt_per_px, rect_h * pt_per_px)

    # MIC/DTA Box
    mic_x, mic_y = x0 + 24, y0 + 15
    mic_w, mic_h = 235, 70
    c.rect(mic_x * pt_per_px, (height_px - mic_y - mic_h) *
           pt_per_px, mic_w * pt_per_px, mic_h * pt_per_px)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString((mic_x + mic_w / 2) * pt_per_px,
                        (height_px - mic_y - mic_h / 2 - 12) * pt_per_px, "MIC/DTA")

    # Títulos principales
    title_x, title_y = x0 + 280, y0 + 36
    c.setFont("Helvetica-Bold", 20)
    c.drawString(title_x * pt_per_px, (height_px - title_y) * pt_per_px,
                 "Manifiesto Internacional de Carga por Carretera / Declaración de Tránsito Aduanero")
    c.setFont("Helvetica", 20)
    c.drawString(title_x * pt_per_px, (height_px - title_y - 38) * pt_per_px,
                 "Manifesto Internacional de Carga Rodoviária / Declaração de Trânsito")

    # ===================== CAMPOS ====================
    campos = [
        (1,  55, 162, 863, 450, "1 Nombre y domicilio del porteador",
         "Nome e endereço do transportador", ""),
        (2,  55, 610, 861, 142, "2 Rol de contribuyente",
         "Cadastro geral de contribuintes", ""),
        (3, 916, 162, 389, 169, "3 Tránsito aduanero", "Trânsito aduaneiro", ""),
        (4, 1305, 162, 365, 167, "4 Nº", "", ""),
        (5, 916, 330, 388, 115, "5 Hoja / Folha", "", ""),
        (6, 1305, 330, 365, 115, "6 Fecha de emisión", "Data de emissão", ""),
        (7, 916, 445, 752, 166, "7 Aduana, ciudad y país de partida",
         "Alfândega, cidade e país de partida", ""),
        (8, 916, 610, 752, 142, "8 Ciudad y país de destino final",
         "Cidade e país de destino final", ""),
        (9,  55, 750, 861, 165, "9 CAMION ORIGINAL: Nombre y domicilio del propietario",
         "CAMINHÃO ORIGINAL: Nome e endereço do proprietário", ""),
        (10, 55, 915, 417, 142, "10 Rol de contribuyente", "Cadastro geral de", ""),
        (11, 470, 915, 445, 142, "11 Placa de camión", "Placa do caminhão", ""),
        (12, 55, 1055, 417, 142, "12 Marca y número", "Marca e número", ""),
        (13, 470, 1055, 445, 142, "13 Capacidad de arrastre",
         "Capacidade de tração (t)", ""),
        (14, 55, 1197, 417, 135, "14 AÑO", "ANO", ""),
        (15, 470, 1197, 445, 135, "15 Semirremolque / Remolque",
         "Semi-reboque / Reboque", ""),
        (16, 915, 752, 753, 163, "16 CAMION SUSTITUTO: Nombre y domicilio del",
         "CAMINHÃO SUBSTITUTO: Nome e endereço do", ""),
        (17, 915, 915, 395, 140, "17 Rol de contribuyente", "Cadastro geral de", ""),
        (18, 1310, 915, 360, 140, "18 Placa del camión", "Placa do", ""),
        (19, 915, 1055, 395, 140, "19 Marca y número", "Marca e número", ""),
        (20, 1310, 1055, 360, 140, "20 Capacidad de arrastre",
         "Capacidade de tração", ""),
        (21, 915, 1195, 395, 135, "21 AÑO", "ANO", ""),
        (22, 1310, 1195, 360, 135, "22 Semirremolque / Remolque",
         "Semi-reboque / Reboque", ""),
        (23, 55, 1330, 313, 154, "23 Nº carta de porte", "Nº do conhecimento", ""),
        (24, 366, 1330, 550, 154, "24 Aduana de destino", "Alfândega de destino", ""),
        (25, 55, 1482, 313, 136, "25 Moneda", "Moeda", ""),
        (26, 366, 1482, 550, 136, "26 Origen de las mercaderías",
         "Origem das mercadorias", ""),
        (27, 55, 1618, 313, 136, "27 Valor FOT", "Valor FOT", ""),
        (28, 366, 1618, 275, 136, "28 Flete en U$S", "Flete em U$S", ""),
        (29, 641, 1618, 275, 136, "29 Seguro en U$S", "Seguro em U$S", ""),
        (30, 55, 1754, 313, 119, "30 Tipo de Bultos", "Tipo dos volumes", ""),
        (31, 366, 1754, 275, 119, "31 Cantidad de", "Quantidade de", ""),
        (32, 641, 1754, 275, 119, "32 Peso bruto", "Peso bruto", ""),
        (33, 915, 1330, 753, 154, "33 Remitente", "Remetente", ""),
        (34, 915, 1482, 753, 136, "34 Destinatario", "Destinatario", ""),
        (35, 915, 1618, 753, 136, "35 Consignatario", "Consignatário", ""),
        (36, 915, 1754, 753, 250, "36 Documentos anexos", "Documentos anexos", ""),
        (37, 55, 1873, 861, 131, "37 Número de precintos", "Número dos lacres", ""),
        (38, 55, 2004, 1613, 222, "38 Marcas y números de los bultos, descripción de las mercaderías",
         "Marcas e números dos volumes, descrição das mercadorias", ""),
        (39, 55, 2226, 838, 498, "Declaramos que las informaciones presentadas en este Documento son expresión de verdad, que los datos referentes a las mercaderías fueron transcriptos exactamente conforme a la declaración del remitente, las cuales son de su exclusiva responsabilidad, y que esta operación obedece a lo dispuesto en el Convenio sobre Transporte Internacional Terrestre de los países del Cono Sur.",
         "Declaramos que as informações prestadas neste Documento são a expressão de verdade que os dados referentes as mercadorias foram transcritos exatamente conforme a declaração do remetente, os quais são de sua exclusiva responsabilidade, e que esta operação obedece ao disposto no Convênio sobre Transporte Internacional Terrestre dos", "39 Firma y sello del porteador / Assinatura e carimbo do"),
        (40, 891, 2226, 780, 330, "40 Nº DTA, ruta y plazo de transporte",
         "Nº DTA, rota e prazo de transporte", ""),
        (41, 891, 2552, 780, 173, "41 Firma y sello de la Aduana de Partida",
         "Assinatura e carimbo de Alfândega de", ""),
    ]

    for n, x, y, w, h, titulo, subtitulo, extra in campos:
        if n == 39:
            draw_campo39(c, x, y, w, h, height_px, pt_per_px)
            continue

        # Dibuja el rectángulo
        c.rect(x * pt_per_px, (height_px - y - h) *
               pt_per_px, w * pt_per_px, h * pt_per_px)
        tx = (x + 8) * pt_per_px
        ty = (height_px - y - 24) * pt_per_px

        # Para 33, 34, 35 y 38: titulo y subtitulo juntos, el resto normal
        if n in [33, 34, 35, 38]:
            c.setFont("Helvetica-Bold", 13)
            if subtitulo:
                titulo_unido = f"{titulo} / {subtitulo}"
            else:
                titulo_unido = titulo
            c.drawString(tx, ty, titulo_unido)
            if extra:
                c.setFont("Helvetica-Bold", 13)
                c.drawString(tx, ty - 16, extra)
        else:
            c.setFont("Helvetica-Bold", 13)
            c.drawString(tx, ty, titulo)
            if subtitulo:
                c.setFont("Helvetica", 11)
                c.drawString(tx, ty - 16, subtitulo)
            if extra:
                c.setFont("Helvetica-Bold", 13)
                c.drawString(tx, ty - 32, extra)

    # Rectángulo grande externo
    c.rect(55 * pt_per_px, (height_px - 55 - 2672.75) *
           pt_per_px, 1616.75 * pt_per_px, 2672.75 * pt_per_px)
    c.save()


draw_micdta_pdf("plantilla_micdta.pdf")
