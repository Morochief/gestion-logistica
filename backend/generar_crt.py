import io
from sqlalchemy.orm import joinedload
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfReader, PdfWriter
from app import create_app
from app.models import db, CRT

app = create_app()
app.app_context().push()

def dividir_texto(texto, max_len=40):
    if not texto:
        return ["", ""]
    if len(texto) <= max_len:
        return [texto, ""]
    corte = texto.rfind(" ", 0, max_len)
    if corte == -1:
        corte = max_len
    return [texto[:corte], texto[corte:].strip()]

def generar_pdf_crt(crt_id):
    crt = db.session.query(CRT)\
        .options(
            joinedload(CRT.remitente),
            joinedload(CRT.destinatario),
            joinedload(CRT.consignatario),
            joinedload(CRT.notificar_a),
            joinedload(CRT.transportadora),
            joinedload(CRT.ciudad_emision),
            joinedload(CRT.pais_emision),
            joinedload(CRT.moneda),
            joinedload(CRT.gastos)
        ).filter_by(id=crt_id).first()

    if not crt:
        print(f"❌ CRT con id {crt_id} no encontrado")
        return

    print(f"✅ Generando PDF para CRT: {crt.numero_crt}")

    plantilla = "app/static/Plantilla_CRT_Vacio.pdf"
    reader = PdfReader(plantilla)
    page = reader.pages[0]

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    c.setFont("Helvetica", 8)

    # Coordenadas aproximadas (x, y)
    remitente1, remitente2 = dividir_texto(f"{crt.remitente.nombre} - {crt.remitente.direccion}")
    destinatario1, destinatario2 = dividir_texto(f"{crt.destinatario.nombre} - {crt.destinatario.direccion}")
    consignatario1, consignatario2 = dividir_texto(f"{crt.consignatario.nombre} - {crt.consignatario.direccion}" if crt.consignatario else "")
    transportadora = crt.transportadora.nombre
    notificar = crt.notificar_a.nombre if crt.notificar_a else ""

    # Datos generales
    c.drawString(209.98, 135.63, crt.numero_crt)
    c.drawString(80, 740, remitente1)
    c.drawString(80, 730, remitente2)
    c.drawString(80, 710, destinatario1)
    c.drawString(80, 700, destinatario2)
    c.drawString(80, 680, consignatario1)
    c.drawString(80, 670, consignatario2)
    c.drawString(80, 650, transportadora)
    c.drawString(80, 630, notificar)
    c.drawString(450, 630, crt.lugar_entrega or "")
    c.drawString(450, 610, crt.incoterm or "")
    c.drawString(450, 590, crt.moneda.nombre if crt.moneda else "")
    c.drawString(450, 570, str(crt.valor_mercaderia or ""))
    c.drawString(450, 550, crt.factura_exportacion or "")
    c.drawString(450, 530, crt.nro_despacho or "")
    c.drawString(450, 510, crt.formalidades_aduana or "")
    c.drawString(450, 490, str(crt.valor_flete_externo or ""))
    c.drawString(450, 470, str(crt.valor_reembolso or ""))
    c.drawString(450, 450, crt.transporte_sucesivos or "")
    c.drawString(80, 430, crt.detalles_mercaderia or "")
    c.drawString(80, 410, f"Peso bruto: {crt.peso_bruto or ''} kg / Peso neto: {crt.peso_neto or ''} kg / Vol: {crt.volumen or ''} m3")

    # Observaciones largas
    obs1, obs2 = dividir_texto(crt.observaciones or "", max_len=80)
    c.drawString(80, 390, obs1)
    c.drawString(80, 380, obs2)

    # Tabla de gastos
    y = 360
    for gasto in crt.gastos:
        linea = f"{gasto.tramo or ''} | {gasto.valor_remitente or ''} {gasto.moneda_remitente.nombre if gasto.moneda_remitente else ''} / {gasto.valor_destinatario or ''} {gasto.moneda_destinatario.nombre if gasto.moneda_destinatario else ''}"
        c.drawString(80, y, linea)
        y -= 12

    c.save()
    packet.seek(0)
    overlay = PdfReader(packet)

    output = PdfWriter()
    page.merge_page(overlay.pages[0])
    output.add_page(page)

    output_filename = f"CRT_{crt.numero_crt}.pdf"
    with open(output_filename, "wb") as f:
        output.write(f)

    print(f"✅ PDF generado: {output_filename}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("⚠️ Uso: python generar_crt.py <id_crt>")
    else:
        generar_pdf_crt(int(sys.argv[1]))
