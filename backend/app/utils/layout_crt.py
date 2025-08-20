from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black


def dibujar_lineas_dinamicas(c, lineas):
    ancho_pagina, alto_pagina = A4

    # === Dibuja rectángulos y círculo CRT ===
    for i, linea in enumerate(lineas):
        c.setStrokeColor(black)
        if linea.get('tipo') == 'rect':
            x = linea['x']
            y_ill = linea['y']
            ancho = linea['ancho']
            alto = linea['alto']
            grosor = linea['grosor']
            y_pdf = alto_pagina - y_ill - alto
            c.setLineWidth(grosor)
            c.rect(x, y_pdf, ancho, alto, stroke=1, fill=0)
        elif linea.get('tipo') == 'circle':
            x_centro = linea['x']
            y_ill = linea['y']
            radio = linea['radio']
            grosor = linea['grosor']
            y_pdf = alto_pagina - y_ill
            c.setLineWidth(grosor)
            c.setStrokeColor(black)
            c.circle(x_centro, y_pdf, radio, stroke=1, fill=0)
            # Texto central "CRT"
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 17)
            c.drawCentredString(x_centro, y_pdf-6, "CRT")

            # === Bloque de títulos a la derecha del círculo ===
            texto_titulo = [
                "Conhecimento Internacional",
                "de Transporte Rodoviário",
                "Carta de Porte Internacional",
                "por Carretera"
            ]
            x_texto = x_centro + radio + 16  # Espaciado a la derecha del círculo
            y_texto = y_pdf + 14  # Arriba del centro del círculo
            c.setFont("Helvetica-Bold", 9)
            line_spacing = 11
            for idx, linea_txt in enumerate(texto_titulo):
                c.drawString(x_texto, y_texto - idx * line_spacing, linea_txt)

            # === Texto legal multilínea - REPOSICIONADO al lado de los títulos ===
            texto_legal = (
                "O transporte realizado ao amparo deste Cohecimento de Transporte Internacional esta sujeito as disposicoes do Convenio "
                "sobre o Contrato de Transporte e a Responsabilidade Civil do transportador no transporte terrestre Internacional de "
                "Mercadorias, as quais anulan toda estipulacao contraria as mesmas em perjuizo do remetente oudo consignatario.- "
                "El transporte realizado bajo esta Carta de Porte Internacional está sujeto a las disposiciones del Convenio sobre el "
                "Contrato de Transporte y la Responsabilidad Civil del Portador en el Transporte Terrestre Internacional de Mercancias, las "
                "cuales anulan toda estipulación que se aparte de ellas en perjuicio del remitente o del consignatario."
            )

            # Posición al lado de los títulos
            x_legal = x_texto + 150  # Al lado derecho de los títulos
            y_legal_start = y_texto + 4
            ancho_disponible = 29 + 540 - x_legal - 5

            c.setFont("Helvetica", 6)
            c.setFillColor(black)

            # Función para dividir texto en líneas que caben en el ancho disponible
            def dividir_texto_en_lineas(texto, ancho_max, fuente, tamaño):
                palabras = texto.split()
                lineas = []
                linea_actual = ""
                for palabra in palabras:
                    test_linea = linea_actual + " " + palabra if linea_actual else palabra
                    ancho_test = c.stringWidth(test_linea, fuente, tamaño)
                    if ancho_test <= ancho_max:
                        linea_actual = test_linea
                    else:
                        if linea_actual:
                            lineas.append(linea_actual)
                        linea_actual = palabra
                if linea_actual:
                    lineas.append(linea_actual)
                return lineas

            lineas_legales = dividir_texto_en_lineas(
                texto_legal, ancho_disponible, "Helvetica", 6)

            espacio_entre_lineas = 6
            for i, linea in enumerate(lineas_legales):
                y_pos = y_legal_start - (i * espacio_entre_lineas)
                if y_pos > y_pdf - radio:
                    c.drawString(x_legal, y_pos, linea)

    # === Títulos y leyendas ===
    alto_pagina = A4[1]
    c.setFont("Helvetica-Bold", 8)
    x_titulo = 35
    y_titulo_ill = 87
    y_titulo_pdf = alto_pagina - y_titulo_ill
    c.drawString(x_titulo, y_titulo_pdf,
                 "1- Nome e endereco do remetente/Nombre y domicilio del remitente")
    x_titulo2 = 300
    y_titulo2_ill = 87
    y_titulo2_pdf = alto_pagina - y_titulo2_ill
    c.drawString(x_titulo2, y_titulo2_pdf, "2- Número / Número")
    x_titulo3 = 300
    y_titulo3_ill = 105
    y_titulo3_pdf = alto_pagina - y_titulo3_ill
    c.setFont("Helvetica-Bold", 7.02)
    c.drawString(x_titulo3, y_titulo3_pdf,
                 "3- Nome e endereco do transportador/Nombre y domicilio del portador")
    x_titulo4 = 35
    y_titulo4_ill = 149
    y_titulo4_pdf = alto_pagina - y_titulo4_ill
    c.setFont("Helvetica-Bold", 7.02)
    c.drawString(x_titulo4, y_titulo4_pdf,
                 "4- Nome e endereco do destinatario / Nombre y domicilio del destinatario")
    x_titulo6 = 35
    y_titulo6_ill = 208
    y_titulo6_pdf = alto_pagina - y_titulo6_ill
    c.setFont("Helvetica-Bold", 7.02)
    c.drawString(x_titulo6, y_titulo6_pdf,
                 "6- Nome e endereco do consignatario / Nombre y domicilio del consignatario")
    x_titulo9 = 35
    y_titulo9_ill = 267
    y_titulo9_pdf = alto_pagina - y_titulo9_ill
    c.setFont("Helvetica-Bold", 7.02)
    c.drawString(x_titulo9, y_titulo9_pdf, "9- Notificar a: / Notificar a:")
    x_titulo5 = 300
    y_titulo5_ill = 170
    y_titulo5_pdf = alto_pagina - y_titulo5_ill
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_titulo5, y_titulo5_pdf,
                 "5- Local e pais de emisao / Lugar y país de emisión")
    x_titulo7 = 300
    y_titulo7_ill = 207
    y_titulo7_pdf = alto_pagina - y_titulo7_ill
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x_titulo7, y_titulo7_pdf,
                 "7- Local, pais e data que o transportador se responsabiliza pela mercadoria")
    c.drawString(x_titulo7, y_titulo7_pdf - 10,
                 "Lugar, país y fecha en que el portador se hace cargo de las mercancias")
    x_titulo8 = 300
    y_titulo8_ill = 255
    y_titulo8_pdf = alto_pagina - y_titulo8_ill
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_titulo8, y_titulo8_pdf,
                 "8- Localidade, pais e prazo de entrega / Lugar, país y plazo de entrega")
    x_titulo10 = 300
    y_titulo10_ill = 292
    y_titulo10_pdf = alto_pagina - y_titulo10_ill
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_titulo10, y_titulo10_pdf,
                 "10- Transporte sucessivos/Porteadores sucesivos")
    x_titulo11 = 35
    y_titulo11_ill = 325
    y_titulo11_pdf = alto_pagina - y_titulo11_ill
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x_titulo11, y_titulo11_pdf,
                 "11- Quantidade e categoria de volumes, marcas e números, tipos de mercaderías, contelners e acessórios.")
    c.drawString(x_titulo11, y_titulo11_pdf - 10,
                 "Cantidad y clase de bultos, marcas y números, tipo de mercancías, contenedores y accesorios")
    x_titulo12 = 412
    y_titulo12_ill = 326
    y_titulo12_pdf = alto_pagina - y_titulo12_ill
    c.setFont("Helvetica-Bold", 7.98)
    c.drawString(x_titulo12, y_titulo12_pdf,
                 "12- Peso bruto en Kg./ Peso bruto em Kg.")
    c.drawString(x_titulo12, y_titulo12_pdf - 10, "PB:")
    c.drawString(x_titulo12, y_titulo12_pdf - 25, "PN:")
    x_titulo13 = 412
    y_titulo13_ill = 361
    y_titulo13_pdf = alto_pagina - y_titulo13_ill
    c.setFont("Helvetica-Bold", 7.50)
    c.drawString(x_titulo13, y_titulo13_pdf,
                 "13-Volume em m3/ Volumen en m.cu.")
    x_titulo14 = 412
    y_titulo14_ill = 380
    y_titulo14_pdf = alto_pagina - y_titulo14_ill
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_titulo14, y_titulo14_pdf, "14- Valor / Valor")
    c.drawString(x_titulo14, y_titulo14_pdf - 25, "   Moeda/ Moneda:")
    c.drawString(x_titulo14, y_titulo14_pdf - 50, "   INCOTERMS:")
    x_titulo15 = 37
    y_titulo15_ill = 442
    y_titulo15_pdf = alto_pagina - y_titulo15_ill
    c.setFont("Helvetica-Bold", 7.02)
    c.drawString(x_titulo15, y_titulo15_pdf, "15- Custos a pagar")
    c.drawString(x_titulo15, y_titulo15_pdf - 8, "Gastos a pagar")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_titulo15, y_titulo15_pdf - 18, "Frete / Flete")
    x_titulo15_1 = 137
    y_titulo15_1_ill = 442
    y_titulo15_1_pdf = alto_pagina - y_titulo15_1_ill
    c.setFont("Helvetica-Bold", 6)
    c.drawString(x_titulo15_1 + 2, y_titulo15_1_pdf, "Valor Remitente")
    c.drawString(x_titulo15_1 + 2, y_titulo15_1_pdf - 8, "Monto Remitente")
    x_titulo15_2 = 204
    y_titulo15_2_ill = 442
    y_titulo15_2_pdf = alto_pagina - y_titulo15_2_ill
    c.setFont("Helvetica-Bold", 6)
    c.drawString(x_titulo15_2 + 7, y_titulo15_2_pdf, "Moeda")
    c.drawString(x_titulo15_2 + 7, y_titulo15_2_pdf - 8, "Moneda")
    x_titulo15_3 = 240
    y_titulo15_3_ill = 442
    y_titulo15_3_pdf = alto_pagina - y_titulo15_3_ill
    c.setFont("Helvetica-Bold", 6)
    c.drawString(x_titulo15_3 - 1, y_titulo15_3_pdf, "Valor Destinatario")
    c.drawString(x_titulo15_3 - 1, y_titulo15_3_pdf - 8, "Monto Destinatario")
    x_titulo15_4 = 37
    y_titulo15_4_ill = 535
    y_titulo15_4_pdf = alto_pagina - y_titulo15_4_ill
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_titulo15_4, y_titulo15_4_pdf, "Total / Total")
    x_titulo16 = 302
    y_titulo16_ill = 442
    y_titulo16_pdf = alto_pagina - y_titulo16_ill
    c.setFont("Helvetica-Bold", 6.50)
    c.drawString(x_titulo16, y_titulo16_pdf,
                 "16- Declaraçao do valor das mercaderias/ Declaración del valor de las mercaderias")
    c.drawString(x_titulo16, y_titulo16_pdf - 8,
                 "                                                     FCA U$S")
    x_titulo17 = 302
    y_titulo17_ill = 460
    y_titulo17_pdf = alto_pagina - y_titulo17_ill
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_titulo17, y_titulo17_pdf,
                 "17- Documentos Anexos / Documentos Anexos")
    c.drawString(x_titulo17, y_titulo17_pdf - 10,
                 "FACTURA DE  EXPORTACIÓN Nº:")
    c.drawString(x_titulo17, y_titulo17_pdf - 25, "Nº DE DESPACHO: ")
    x_titulo18 = 302
    y_titulo18_ill = 532
    y_titulo18_pdf = alto_pagina - y_titulo18_ill
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_titulo18, y_titulo18_pdf,
                 "18- Instruçoes sobre formalidades de alfandega")
    c.drawString(x_titulo18, y_titulo18_pdf - 10,
                 "Instrucciones sobre formalidades de aduana")
    x_titulo19 = 37
    y_titulo19_ill = 544
    y_titulo19_pdf = alto_pagina - y_titulo19_ill
    c.setFont("Helvetica-Bold", 6.90)
    c.drawString(x_titulo19, y_titulo19_pdf,
                 "19- Valor do frete Externo / Monto del Flete Externo")
    x_titulo20 = 37
    y_titulo20_ill = 564
    y_titulo20_pdf = alto_pagina - y_titulo20_ill
    c.setFont("Helvetica-Bold", 6.90)
    c.drawString(x_titulo20, y_titulo20_pdf,
                 "20- Valor do Reembolso Contra Entrega / Monto de Reembolso Contra Entrega ")
    x_titulo21 = 37
    y_titulo21_ill = 588
    y_titulo21_pdf = alto_pagina - y_titulo21_ill
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_titulo21, y_titulo21_pdf,
                 "21- Nome e assinatura do remetente ou seu representante")
    c.drawString(x_titulo21, y_titulo21_pdf - 10,
                 "Nombre y firma del remetente ou seu representante")
    c.drawString(x_titulo21, y_titulo21_pdf - 60, "Data / Fecha")
    x_titulo22 = 302
    y_titulo22_ill = 588
    y_titulo22_pdf = alto_pagina - y_titulo22_ill
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_titulo22, y_titulo22_pdf,
                 "22- Declaraçoes e observaçoes / Declaraciones y observaciones")
    x_titulo23 = 37
    y_titulo23_ill = 665
    y_titulo23_pdf = alto_pagina - y_titulo23_ill
    c.setFont("Helvetica-Bold", 6)
    c.drawString(x_titulo23, y_titulo23_pdf,
                 "As mercadorias consignadas neste Conhecimiento de Transporte foran recebidas pelo")
    c.drawString(x_titulo23, y_titulo23_pdf - 6,
                 "transportador aparentemente em bom estado, sob as condicoes gerais que figuram ")
    c.drawString(x_titulo23, y_titulo23_pdf - 12, "no verso.")
    c.drawString(x_titulo23, y_titulo23_pdf - 18,
                 "Las mercaderías consignadas en esta Carta de Porte fueron recibidas por el portador ")
    c.drawString(x_titulo23, y_titulo23_pdf - 24,
                 "aparentemente en buen estado, bajo las condiciones generales que figuran al dorso.")
    c.drawString(x_titulo23, y_titulo23_pdf - 30,
                 "23- Nome e assinatura do transportador ou seu representante")
    c.drawString(x_titulo23, y_titulo23_pdf - 36,
                 "Nombre y firma del transportador o su representante")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_titulo23, y_titulo23_pdf - 90, "Data / Fecha")
    x_titulo24 = 302
    y_titulo24_ill = 666
    y_titulo24_pdf = alto_pagina - y_titulo24_ill
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_titulo24, y_titulo24_pdf,
                 "24- Nome e assinatura do destinatário ou seu representante")
    c.drawString(x_titulo24, y_titulo24_pdf - 10,
                 "Nombre y firma del destinatario o su representante")
    c.drawString(x_titulo24, y_titulo24_pdf - 89, "Data / Fecha")
    x_titulo24b = 34
    y_titulo24b_ill = 773
    y_titulo24b_pdf = alto_pagina - y_titulo24b_ill
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x_titulo24b, y_titulo24b_pdf,
                 "1º Via- Primeiro Original para o Remetente. Unico Valido para Retirar as Mercaderias / Primer Original para el Remitente. Único Válido para retirar las mercaderia")


lineas = [
    # [0] Encabezado: banda superior
    {"tipo": "rect", "x": 29, "y": 29,  "ancho": 540,  "alto": 48,   "grosor": 1},
    # [1] Círculo CRT en el encabezado (esquina izquierda)
    {"tipo": "circle", "x": 29+28, "y": 29+24, "radio": 19, "grosor": 2},
    # [2] 1- Remitente
    {"tipo": "rect", "x": 29, "y": 77,  "ancho": 267,  "alto": 64,   "grosor": 1},
    # [3] 2- Número CRT
    {"tipo": "rect", "x": 296, "y": 77, "ancho": 273,  "alto": 20,   "grosor": 1},
    # [4] 4- Destinatario
    {"tipo": "rect", "x": 29, "y": 141, "ancho": 267,  "alto": 59,   "grosor": 1},
    # [5] 6- Consignatario
    {"tipo": "rect", "x": 29, "y": 200, "ancho": 267,  "alto": 59,   "grosor": 1},
    # [6] 9- Notificar a
    {"tipo": "rect", "x": 29, "y": 259, "ancho": 267,  "alto": 56,   "grosor": 1},
    # [7] 3- Transportador (Nombre y dirección)
    {"tipo": "rect", "x": 296, "y": 97, "ancho": 273,  "alto": 66,   "grosor": 1},
    # [8] 5- Lugar y país de emisión
    {"tipo": "rect", "x": 296, "y": 163, "ancho": 273,  "alto": 37,   "grosor": 1},
    # [9] 7- Lugar y fecha que el transportador se responsabiliza
    {"tipo": "rect", "x": 296, "y": 200, "ancho": 273,  "alto": 43,   "grosor": 1},
    # [10] 8- Lugar y plazo de entrega
    {"tipo": "rect", "x": 296, "y": 243, "ancho": 273,  "alto": 37,   "grosor": 1},
    # [11] 10- Transportes sucesivos
    {"tipo": "rect", "x": 296, "y": 280, "ancho": 273,  "alto": 35,   "grosor": 1},
    # [12] 11- Mercancía (descripción principal)
    {"tipo": "rect", "x": 29,  "y": 315, "ancho": 382,  "alto": 119,  "grosor": 1},
    # [13] 12- Peso bruto
    {"tipo": "rect", "x": 411, "y": 315, "ancho": 158,  "alto": 39,   "grosor": 1},
    # [14] 13- Volumen
    {"tipo": "rect", "x": 411, "y": 354, "ancho": 158,  "alto": 17,   "grosor": 1},
    # [15] 14- Valor / Moneda / Incoterms
    {"tipo": "rect", "x": 411, "y": 371, "ancho": 158,  "alto": 63,   "grosor": 1},
    # [16] 16- Declaración de valor
    {"tipo": "rect", "x": 296, "y": 434, "ancho": 273,  "alto": 19,   "grosor": 1},
    # [17] 17- Documentos anexos
    {"tipo": "rect", "x": 296, "y": 453, "ancho": 273,  "alto": 69,   "grosor": 1},
    # [18] 18- Instrucciones de aduana
    {"tipo": "rect", "x": 296, "y": 522, "ancho": 273,  "alto": 58,   "grosor": 1},
    # [19] 22- Declaraciones y observaciones
    {"tipo": "rect", "x": 296, "y": 580, "ancho": 273,  "alto": 77,   "grosor": 1},
    # [20] 23- Firma transportador
    {"tipo": "rect", "x": 29,  "y": 657, "ancho": 267,  "alto": 104,  "grosor": 1},
    # [21] 24- Firma destinatario
    {"tipo": "rect", "x": 296, "y": 657, "ancho": 273,  "alto": 104,  "grosor": 1},
    # [22] 21- Firma remitente
    {"tipo": "rect", "x": 29,  "y": 580, "ancho": 267,  "alto": 77,   "grosor": 1},
    # [23] 20- Reembolso contra entrega
    {"tipo": "rect", "x": 29,  "y": 555, "ancho": 267,  "alto": 25,   "grosor": 1},
    # [24] 19- Flete externo
    {"tipo": "rect", "x": 29,  "y": 537, "ancho": 267,  "alto": 18,   "grosor": 1},
    # [25] 15- Total
    {"tipo": "rect", "x": 29,  "y": 522, "ancho": 267,  "alto": 15,   "grosor": 1},
    # [26] 15- Costos: Frete/Flete Remitente (celda izquierda)
    {"tipo": "rect", "x": 29,  "y": 434, "ancho": 107,  "alto": 19,   "grosor": 1},
    # [27] 15- Costos: Monto Remitente (celda izquierda abajo)
    {"tipo": "rect", "x": 29,  "y": 453, "ancho": 107,  "alto": 69,   "grosor": 1},
    # [28] 15- Costos: Valor remitente (centro arriba)
    {"tipo": "rect", "x": 136, "y": 434, "ancho": 70,   "alto": 19,   "grosor": 1},
    # [29] 15- Costos: Monto remitente (centro abajo)
    {"tipo": "rect", "x": 136, "y": 453, "ancho": 70,   "alto": 69,   "grosor": 1},
    # [30] 15- Costos: Moeda (centro-derecha arriba)
    {"tipo": "rect", "x": 206, "y": 434, "ancho": 31,   "alto": 19,   "grosor": 1},
    # [31] 15- Costos: Moneda (centro-derecha abajo)
    {"tipo": "rect", "x": 206, "y": 453, "ancho": 31,   "alto": 69,   "grosor": 1},
    # [32] 15- Costos: Valor destinatario (derecha arriba)
    {"tipo": "rect", "x": 237, "y": 434, "ancho": 59,   "alto": 19,   "grosor": 1},
    # [33] 15- Costos: Monto destinatario (derecha abajo)
    {"tipo": "rect", "x": 237, "y": 453, "ancho": 59,   "alto": 69,   "grosor": 1},
    # [34] Pie de página
    {"tipo": "rect", "x": 29,  "y": 761, "ancho": 540,  "alto": 17,   "grosor": 1},
]

# ----- Ejemplo de uso -----
output = BytesIO()
c = canvas.Canvas(output, pagesize=A4)
dibujar_lineas_dinamicas(c, lineas)
c.save()

with open('CRT.pdf', 'wb') as f:
    f.write(output.getvalue())
