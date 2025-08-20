from reportlab.lib.pagesizes import A4


def dibujar_lineas_dinamicas(c, lineas):
    ancho_pagina, alto_pagina = A4

    for linea in lineas:
        if linea.get('tipo') == 'rect':
            x = linea['x']
            y_ill = linea['y']
            ancho = linea['ancho']
            alto = linea['alto']
            grosor = linea['grosor']
            y_pdf = alto_pagina - y_ill - alto

            if x + ancho > ancho_pagina:
                ancho = ancho_pagina - x
            if y_pdf < 0:
                y_pdf = 0
            if y_pdf + alto > alto_pagina:
                alto = alto_pagina - y_pdf

            c.setLineWidth(grosor)
            c.rect(x, y_pdf, ancho, alto, stroke=1, fill=0)

        elif linea.get('tipo') == 'circle':
            x_centro = linea['x']
            y_ill = linea['y']
            radio = linea['radio']
            grosor = linea['grosor']
            y_pdf = alto_pagina - y_ill

            c.setLineWidth(grosor)
            c.circle(x_centro, y_pdf, radio, stroke=1, fill=0)

            texto = "CRT"
            c.setFont("Helvetica-Bold", radio * 0.8)
            text_width = c.stringWidth(texto, "Helvetica-Bold", radio * 0.8)
            c.drawString(x_centro - text_width / 2,
                         y_pdf - (radio * 0.4), texto)

            texto_largo = (
                "Conhecimento Internacional\n"
                "de Transporte Rodoviário\n"
                "Carta de Porte Internacional"
            )
            c.setFont("Helvetica-Bold", 10)
            text_x = x_centro + radio + 10
            text_y = y_pdf + radio / 2
            for i, linea_texto in enumerate(texto_largo.split('\n')):
                c.drawString(text_x, text_y - (i * 12), linea_texto)

            texto_adicional = (
                "O transporte realizado ao amparo deste Cohecimento de Transporte Internacional esta sujeito as disposicoes do Convenio\n"
                "sobre o Contrato de Transporte e a Responsabilidade Civil do transportador no transporte terrestre Internacional de\n"
                "Mercadorias, as quais anulan toda estipulacao contraria as mesmas em perjuizo do remetente oudo consignatario.-\n"
                "El transporte realizado bajo esta Carta de Porte Internacional está sujeto a las disposiciones del Convenio sobre el\n"
                "Contrato de Transporte y la Responsabilidad Civil del Portador en el Transporte Terrestre Internacional de Mercancias, las"
            )
            c.setFont("Helvetica", 6)
            text_x2 = text_x + 150
            text_y2 = text_y
            line_height = 7
            for i, linea_texto in enumerate(texto_adicional.split('\n')):
                c.drawString(text_x2, text_y2 - (i * line_height), linea_texto)

        else:
            x = linea['x']
            y_ill = linea['y']
            grosor = linea['grosor']
            y_pdf = alto_pagina - y_ill

            if linea.get('vertical'):
                alto = linea.get('alto', 0)
                y_pdf -= alto
                c.setLineWidth(grosor)
                c.line(x, y_pdf, x, y_pdf + alto)
            else:
                ancho = linea.get('ancho', 0)
                y_pdf -= grosor
                c.setLineWidth(grosor)
                c.line(x, y_pdf, x + ancho, y_pdf)

    # ----- Títulos y leyendas -----
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
    y_titulo4_ill = 147
    y_titulo4_pdf = alto_pagina - y_titulo4_ill
    c.setFont("Helvetica-Bold", 7.02)
    c.drawString(x_titulo4, y_titulo4_pdf,
                 "4- Nome e endereco do destinatario / Nombre y domicilio del destinatario")

    x_titulo6 = 35
    y_titulo6_ill = 206
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
    c.setFont("Helvetica-Bold", 7.02)
    c.drawString(x_titulo15_1, y_titulo15_1_pdf, "Valor Remitente")
    c.drawString(x_titulo15_1, y_titulo15_1_pdf - 8, "Monto Remitente")

    x_titulo15_2 = 204
    y_titulo15_2_ill = 442
    y_titulo15_2_pdf = alto_pagina - y_titulo15_2_ill
    c.setFont("Helvetica-Bold", 7.02)
    c.drawString(x_titulo15_2, y_titulo15_2_pdf, "Moeda")
    c.drawString(x_titulo15_2, y_titulo15_2_pdf - 8, "Moneda")

    x_titulo15_3 = 234
    y_titulo15_3_ill = 442
    y_titulo15_3_pdf = alto_pagina - y_titulo15_3_ill
    c.setFont("Helvetica-Bold", 7.02)
    c.drawString(x_titulo15_3, y_titulo15_3_pdf, "Valor Destinatario")
    c.drawString(x_titulo15_3, y_titulo15_3_pdf - 8, "Monto Destinatario")

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
                 "Nombre y firma del remitente o su representante")
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

    x_titulo24 = 34
    y_titulo24_ill = 773
    y_titulo24_pdf = alto_pagina - y_titulo24_ill
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x_titulo24, y_titulo24_pdf,
                 "1º Via- Primeiro Original para o Remetente. Unico Valido para Retirar as Mercaderias / Primer Original para el Remitente. Único Válido para retirar las mercaderia")


# ------------ Tu lista de líneas original --------------
lineas = [
    {'tipo': 'rect', 'x': 30, 'y': 30, 'ancho': 539.4386,
        'alto': 748.08, 'grosor': 0.96},
    {'x': 30, 'y': 77.9328, 'ancho': 539.3751, 'grosor': 0.0352},
    {'x': 297.5332, 'y': 77.9328, 'grosor': 0.0371,
        'alto': 240.36, 'vertical': True},
    {'x': 30, 'y': 139.4818, 'ancho': 267.7952, 'grosor': 0.0177},
    {'x': 297.5332, 'y': 97.7377, 'ancho': 272, 'grosor': 0.0353},
    {'x': 297.5332, 'y': 162.0965, 'ancho': 272, 'grosor': 0.01},
    {'x': 30, 'y': 198.8629, 'ancho': 539.3751, 'grosor': 0.0556},
    {'x': 297.5332, 'y': 246.8517, 'ancho': 272, 'grosor': 0.0338},
    {'x': 30, 'y': 259.5733, 'ancho': 267.5239, 'grosor': 0.0371},
    {'x': 297.5332, 'y': 282.043, 'ancho': 271.5196, 'grosor': 0.0629},
    {'x': 30, 'y': 318.8183, 'ancho': 539.053, 'grosor': 0.0567},
    {'x': 411.7408, 'y': 318.8183, 'grosor': 0.0772,
        'alto': 116.3083, 'vertical': True},
    {'x': 411.7408, 'y': 354.7168, 'ancho': 157.2844, 'grosor': 0.149},
    {'x': 411.7408, 'y': 372.8309, 'ancho': 157.2964, 'grosor': 0.0275},
    {'x': 30, 'y': 434.9716, 'ancho': 538.897, 'grosor': 0.1288},
    {'x': 30, 'y': 451.7938, 'ancho': 538.875, 'grosor': 0.0703},
    {'x': 299.591, 'y': 435.1, 'grosor': 0.1406, 'alto': 327.4, 'vertical': True},
    {'x': 30, 'y': 525, 'ancho': 538.7799, 'grosor': 0.0056, 'vertical': False},
    {'x': 30, 'y': 537, 'ancho': 269.6, 'grosor': 0.0047, 'vertical': False},
    {'x': 30, 'y': 580.46, 'ancho': 538.703, 'grosor': 0.0586},
    {'x': 30, 'y': 556.4932, 'ancho': 269.6, 'grosor': 0.0384, 'vertical': False},
    {'x': 30, 'y': 655.3766, 'ancho': 539, 'grosor': 0.0868, 'vertical': False},
    {'x': 30, 'y': 762.4586, 'ancho': 538, 'grosor': 0.0772, 'vertical': False},
    {'x': 134.5703, 'y': 434.9716, 'grosor': 0.1406, 'alto': 90, 'vertical': True},
    {'x': 203.5, 'y': 434.9716, 'grosor': 0.1406, 'alto': 90, 'vertical': True},
    {'x': 232.57, 'y': 434.9716, 'grosor': 0.1406, 'alto': 90, 'vertical': True},
    {'tipo': 'circle', 'x': 55, 'y': 55, 'radio': 20, 'grosor': 0.8}
]

# ------------ Ejemplo de uso stand-alone (comentado para backend Flask) --------------
# from reportlab.pdfgen import canvas
# from io import BytesIO
# output = BytesIO()
# c = canvas.Canvas(output, pagesize=A4)
# dibujar_lineas_dinamicas(c, lineas)
# c.save()
# with open('CRT.pdf', 'wb') as f:
#     f.write(output.getvalue())
