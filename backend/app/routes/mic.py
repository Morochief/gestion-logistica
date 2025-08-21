# ========== IMPORTS COMPLETOS Y ORDENADOS ==========
from decimal import Decimal, InvalidOperation
from flask import Blueprint, request, jsonify, send_file
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from datetime import datetime, timedelta, date
from app.models import db, MIC, CRT, CRT_Gasto, Ciudad, Transportadora, Remitente
from app.utils.layout_mic import generar_micdta_pdf_con_datos

mic_bp = Blueprint('mic', __name__, url_prefix='/api/mic')

# ========== UTIL MULTILÍNEA ==========


def join_lines(*parts):
    """Une los campos con salto de línea solo si existen."""
    return "\n".join([str(p) for p in parts if p])

# ✅ FUNCIÓN: Formatear entidad COMPLETA con todos los datos del CRT


def formatear_entidad_completa_crt(entidad):
    """
    Formatea una entidad (transportadora, remitente, destinatario)
    con TODOS sus datos exactamente como están en el CRT
    """
    if not entidad:
        return ""

    lines = []

    # 1) Nombre
    if hasattr(entidad, 'nombre') and entidad.nombre:
        lines.append(entidad.nombre.strip())

    # 2) Dirección (respetando multilínea)
    if hasattr(entidad, 'direccion') and entidad.direccion:
        direccion = entidad.direccion.strip()
        if '\n' in direccion:
            for linea_dir in direccion.split('\n'):
                if linea_dir.strip():
                    lines.append(linea_dir.strip())
        else:
            lines.append(direccion)

    # 3) Ciudad - País
    ciudad_line = ""
    if hasattr(entidad, 'ciudad') and entidad.ciudad:
        if entidad.ciudad.nombre:
            ciudad_line = entidad.ciudad.nombre.strip()
        if entidad.ciudad.pais and entidad.ciudad.pais.nombre:
            pais = entidad.ciudad.pais.nombre.strip()
            if ciudad_line:
                ciudad_line += f" - {pais}"
            else:
                ciudad_line = pais
    if ciudad_line:
        lines.append(ciudad_line)

    # 4) Documento (tipo:número o DOC:número)
    documento_line = ""
    tipo_documento = getattr(entidad, 'tipo_documento', '') or ''
    numero_documento = getattr(entidad, 'numero_documento', '') or ''
    if tipo_documento and numero_documento:
        documento_line = f"{tipo_documento.strip()}:{numero_documento.strip()}"
    elif numero_documento:
        documento_line = f"DOC:{numero_documento.strip()}"
    if documento_line:
        lines.append(documento_line)

    # 5) Teléfono (si tuviera)
    telefono = getattr(entidad, 'telefono', '') or ''
    if telefono.strip():
        lines.append(f"Tel: {telefono.strip()}")

    resultado = "\n".join(lines)

    # Debug
    tipo_entidad = "Transportadora" if hasattr(
        entidad, 'codigo') else "Remitente/Destinatario"
    print(f"🎯 FORMATEO {tipo_entidad}:")
    print(f"   📝 Nombre: '{getattr(entidad, 'nombre', 'N/A')}'")
    print(f"   📍 Dirección: '{getattr(entidad, 'direccion', 'N/A')}'")
    print(
        f"   🏙️ Ciudad: '{getattr(entidad.ciudad, 'nombre', 'N/A') if hasattr(entidad, 'ciudad') and entidad.ciudad else 'N/A'}'")
    print(f"   🌍 País: '{getattr(entidad.ciudad.pais, 'nombre', 'N/A') if hasattr(entidad, 'ciudad') and entidad.ciudad and entidad.ciudad.pais else 'N/A'}'")
    print(f"   📄 Tipo Doc: '{getattr(entidad, 'tipo_documento', 'N/A')}'")
    print(f"   🔢 Núm Doc: '{getattr(entidad, 'numero_documento', 'N/A')}'")
    print(f"   📞 Teléfono: '{getattr(entidad, 'telefono', 'N/A')}'")
    print(f"   📋 RESULTADO ({len(lines)} líneas)")
    return resultado

# ========== PROCESAR GASTOS CRT -> MIC (28 flete / 29 seguro) ==========


def procesar_gastos_crt_para_mic(gastos_crt):
    """
    - Si el tramo contiene "seguro" -> Campo 29 (Seguro)
    - Los demás -> suman Campo 28 (Flete)
    """
    if not gastos_crt:
        return {"campo_28_total": "", "campo_29_seguro": ""}

    print(f"🧮 PROCESANDO {len(gastos_crt)} GASTOS DEL CRT:")

    valor_seguro = 0.0
    valor_flete_total = 0.0

    for i, gasto in enumerate(gastos_crt, 1):
        tramo = (gasto.tramo or "").strip().lower()

        # Determinar valor a usar (priorizar remitente, luego destinatario)
        valor_gasto = 0.0
        moneda_usada = ""

        if gasto.valor_remitente and gasto.valor_remitente not in [None, "None", ""]:
            try:
                valor_gasto = float(gasto.valor_remitente)
                moneda_usada = gasto.moneda_remitente.nombre if gasto.moneda_remitente else ""
            except (ValueError, TypeError):
                valor_gasto = 0.0
        elif gasto.valor_destinatario and gasto.valor_destinatario not in [None, "None", ""]:
            try:
                valor_gasto = float(gasto.valor_destinatario)
                moneda_usada = gasto.moneda_destinatario.nombre if gasto.moneda_destinatario else ""
            except (ValueError, TypeError):
                valor_gasto = 0.0

        es_seguro = "seguro" in tramo

        if es_seguro:
            valor_seguro += valor_gasto
            print(
                f"   🛡️ Gasto {i} - SEGURO: '{gasto.tramo}' = {valor_gasto} {moneda_usada}")
        else:
            valor_flete_total += valor_gasto
            print(
                f"   🚛 Gasto {i} - FLETE: '{gasto.tramo}' = {valor_gasto} {moneda_usada}")

    def format_number(num):
        if num == 0:
            return ""
        try:
            formatted = f"{num:,.2f}".replace(
                ",", "X").replace(".", ",").replace("X", ".")
            return formatted
        except Exception:
            return str(num) if num != 0 else ""

    resultado = {
        "campo_28_total": format_number(valor_flete_total),
        "campo_29_seguro": format_number(valor_seguro)
    }

    print("📊 RESULTADO DEL PROCESAMIENTO:")
    print(f"   🚛 Total Flete (28): '{resultado['campo_28_total']}'")
    print(f"   🛡️ Total Seguro (29): '{resultado['campo_29_seguro']}'\n")
    return resultado

# ========== SERIALIZADOR (para PDF desde MIC guardado) ==========


def to_dict_mic(mic):
    def safe_str(val):
        return "" if val is None else str(val)

    return {
        "id": mic.id,
        "crt_id": mic.crt_id,
        "campo_1_transporte": safe_str(mic.campo_1_transporte),
        "campo_2_numero": safe_str(mic.campo_2_numero),
        "campo_3_transporte": safe_str(mic.campo_3_transporte),
        "campo_4_estado": safe_str(mic.campo_4_estado),
        "campo_5_hoja": safe_str(mic.campo_5_hoja),
        "campo_6_fecha": mic.campo_6_fecha.strftime('%Y-%m-%d') if mic.campo_6_fecha else "",
        "campo_7_pto_seguro": safe_str(mic.campo_7_pto_seguro),
        "campo_8_destino": safe_str(mic.campo_8_destino),
        "campo_9_datos_transporte": safe_str(mic.campo_9_datos_transporte),
        "campo_10_numero": safe_str(mic.campo_10_numero),
        "campo_11_placa": safe_str(mic.campo_11_placa),
        "campo_12_modelo_chasis": safe_str(mic.campo_12_modelo_chasis),
        "campo_13_siempre_45": safe_str(mic.campo_13_siempre_45),
        "campo_14_anio": safe_str(mic.campo_14_anio),
        "campo_15_placa_semi": safe_str(mic.campo_15_placa_semi),
        "campo_16_asteriscos_1": safe_str(mic.campo_16_asteriscos_1),
        "campo_17_asteriscos_2": safe_str(mic.campo_17_asteriscos_2),
        "campo_18_asteriscos_3": safe_str(mic.campo_18_asteriscos_3),
        "campo_19_asteriscos_4": safe_str(mic.campo_19_asteriscos_4),
        "campo_20_asteriscos_5": safe_str(mic.campo_20_asteriscos_5),
        "campo_21_asteriscos_6": safe_str(mic.campo_21_asteriscos_6),
        "campo_22_asteriscos_7": safe_str(mic.campo_22_asteriscos_7),
        "campo_23_numero_campo2_crt": safe_str(mic.campo_23_numero_campo2_crt),
        "campo_24_aduana": safe_str(mic.campo_24_aduana),
        "campo_25_moneda": safe_str(mic.campo_25_moneda),
        "campo_26_pais": safe_str(mic.campo_26_pais),
        "campo_27_valor_campo16": safe_str(mic.campo_27_valor_campo16),
        "campo_28_total": safe_str(mic.campo_28_total),
        "campo_29_seguro": safe_str(mic.campo_29_seguro),
        "campo_30_tipo_bultos": safe_str(mic.campo_30_tipo_bultos),
        "campo_31_cantidad": safe_str(mic.campo_31_cantidad),
        "campo_32_peso_bruto": safe_str(mic.campo_32_peso_bruto),
        "campo_33_datos_campo1_crt": safe_str(mic.campo_33_datos_campo1_crt),
        "campo_34_datos_campo4_crt": safe_str(mic.campo_34_datos_campo4_crt),
        "campo_35_datos_campo6_crt": safe_str(mic.campo_35_datos_campo6_crt),
        "campo_36_factura_despacho": safe_str(mic.campo_36_factura_despacho),
        "campo_37_valor_manual": safe_str(mic.campo_37_valor_manual),
        "campo_38_datos_campo11_crt": safe_str(mic.campo_38_datos_campo11_crt),
        "campo_40_tramo": safe_str(mic.campo_40_tramo),
        "creado_en": mic.creado_en.strftime('%Y-%m-%d %H:%M:%S') if getattr(mic, "creado_en", None) else ""
    }

# ========== GENERAR PDF DESDE CRT (con opción de guardar) ==========


@mic_bp.route('/generate_pdf_from_crt/<int:crt_id>', methods=['POST'])
def generar_pdf_mic_desde_crt(crt_id):
    """
    Genera un PDF del MIC directamente desde un CRT.
    Opcional: guardar MIC si viene save=1 (query) o {"save": true} (JSON).
    """
    try:
        user_data = request.json if request.is_json else {}

        print(f"🔍 INICIANDO CLONACIÓN COMPLETA CRT -> MIC (ID: {crt_id})")
        print("="*80)

        # Cargar CRT con relaciones
        crt = CRT.query.options(
            joinedload(CRT.remitente).joinedload(
                Remitente.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.transportadora).joinedload(
                Transportadora.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.destinatario).joinedload(
                Remitente.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.consignatario).joinedload(
                Remitente.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.moneda),
            joinedload(CRT.gastos).joinedload(CRT_Gasto.moneda_remitente),
            joinedload(CRT.gastos).joinedload(CRT_Gasto.moneda_destinatario),
            joinedload(CRT.ciudad_emision).joinedload(Ciudad.pais)
        ).get_or_404(crt_id)

        print(f"✅ CRT CARGADO: {crt.numero_crt}")
        print(
            f"🚛 Transportadora: {crt.transportadora.nombre if crt.transportadora else 'N/A'}")
        print(
            f"📤 Remitente: {crt.remitente.nombre if crt.remitente else 'N/A'}")
        print(
            f"📥 Destinatario: {crt.destinatario.nombre if crt.destinatario else 'N/A'}")
        print(
            f"📦 Consignatario: {crt.consignatario.nombre if crt.consignatario else 'N/A'}")
        print(f"💰 Gastos: {len(crt.gastos) if crt.gastos else 0} items\n")

        # Formateos
        campo_1_transportadora = formatear_entidad_completa_crt(
            crt.transportadora)
        campo_33_remitente = formatear_entidad_completa_crt(crt.remitente)
        campo_34_destinatario = formatear_entidad_completa_crt(
            crt.destinatario)
        campo_35_consignatario = formatear_entidad_completa_crt(
            crt.consignatario) if crt.consignatario else campo_34_destinatario

        # Gastos
        gastos_procesados = procesar_gastos_crt_para_mic(crt.gastos)

        # Armar mic_data
        mic_data = {
            "campo_1_transporte": campo_1_transportadora,
            "campo_9_datos_transporte": campo_1_transportadora,
            "campo_33_datos_campo1_crt": campo_33_remitente,
            "campo_34_datos_campo4_crt": campo_34_destinatario,
            "campo_35_datos_campo6_crt": campo_35_consignatario,
            "campo_28_total": gastos_procesados["campo_28_total"],
            "campo_29_seguro": gastos_procesados["campo_29_seguro"],
            "campo_2_numero": "",
            "campo_3_transporte": "",
            "campo_4_estado": "PROVISORIO",
            "campo_5_hoja": "1 / 1",
            "campo_6_fecha": crt.fecha_emision.strftime('%Y-%m-%d') if crt.fecha_emision else "",
            "campo_7_pto_seguro": "",
            "campo_8_destino": crt.lugar_entrega or "",
            "campo_10_numero": "",
            "campo_11_placa": "",
            "campo_12_modelo_chasis": "",
            "campo_13_siempre_45": "45 TON",
            "campo_14_anio": "",
            "campo_15_placa_semi": "",
            "campo_16_asteriscos_1": "******",
            "campo_17_asteriscos_2": "******",
            "campo_18_asteriscos_3": "******",
            "campo_19_asteriscos_4": "******",
            "campo_20_asteriscos_5": "******",
            "campo_21_asteriscos_6": "******",
            "campo_22_asteriscos_7": "******",
            "campo_23_numero_campo2_crt": crt.numero_crt or "",
            "campo_24_aduana": "",
            "campo_25_moneda": crt.moneda.nombre if crt.moneda else "",
            "campo_26_pais": "520-PARAGUAY",
            "campo_27_valor_campo16": str(crt.declaracion_mercaderia or ""),
            "campo_30_tipo_bultos": "",
            "campo_31_cantidad": "",
            "campo_32_peso_bruto": str(crt.peso_bruto or ""),
            "campo_36_factura_despacho": (
                f"Factura: {crt.factura_exportacion or ''} | Despacho: {crt.nro_despacho or ''}"
                if crt.factura_exportacion or crt.nro_despacho else ""
            ),
            "campo_37_valor_manual": "",
            "campo_38_datos_campo11_crt": (crt.detalles_mercaderia or "")[:1500],
            "campo_40_tramo": "",
        }

        # Overrides del cliente
        if user_data:
            if 'campo_38' in user_data:
                user_data['campo_38_datos_campo11_crt'] = user_data.pop(
                    'campo_38')
            for k in ['campo_28_total', 'campo_29_seguro']:
                if k not in user_data or not user_data.get(k):
                    user_data.pop(k, None)  # no pisar gastos si no envían
            mic_data.update(user_data)

        # Resumen
        print("🎯 RESUMEN DE CLONACIÓN COMPLETA:")
        print(f"   📋 Campo 1 len: {len(mic_data['campo_1_transporte'])}")
        print(
            f"   📋 Campo 33 len: {len(mic_data['campo_33_datos_campo1_crt'])}")
        print(
            f"   📋 Campo 34 len: {len(mic_data['campo_34_datos_campo4_crt'])}")
        print(
            f"   📋 Campo 35 len: {len(mic_data['campo_35_datos_campo6_crt'])}")
        print(
            f"   📦 Campo 38 len: {len(mic_data['campo_38_datos_campo11_crt'])}")
        print(f"   🚛 Campo 28: '{mic_data['campo_28_total']}'")
        print(f"   🛡️ Campo 29: '{mic_data['campo_29_seguro']}'")
        print("="*80)

        # Guardar si corresponde
        should_save = False
        if isinstance(user_data, dict) and user_data.get('save') in [True, '1', 1, 'true', 'True']:
            should_save = True
        if request.args.get('save') in ['1', 'true', 'True']:
            should_save = True

        if should_save:
            print("💾 Guardando MIC en base de datos (pedido del cliente)...")
            saved_mic = _build_mic_model_from_dict(mic_data, crt_id=crt.id)
            db.session.add(saved_mic)
            db.session.commit()
            print(f"✅ MIC guardado con ID {saved_mic.id}")

            # Si no pidieron descargar binario, devolvemos JSON
            if request.args.get('download') not in ['1', 'true', 'True'] and not (isinstance(user_data, dict) and user_data.get('download')):
                return jsonify({
                    "message": "MIC generado y guardado",
                    "mic_id": saved_mic.id,
                    "pdf_url": f"/api/mic/{saved_mic.id}/pdf"
                }), 201

        # Generar PDF (temporal) y devolver binario
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            filename = tmp_file.name

        generar_micdta_pdf_con_datos(mic_data, filename)

        response = send_file(
            filename,
            as_attachment=True,
            download_name=f"MIC_CRT_{crt.numero_crt or crt.id}.pdf"
        )
        response.call_on_close(lambda: os.unlink(filename))

        print(f"✅ PDF MIC GENERADO EXITOSAMENTE para CRT {crt.numero_crt}")
        print(
            f"   💰 Incluye gastos: Flete={mic_data['campo_28_total']} | Seguro={mic_data['campo_29_seguro']}")
        return response

    except Exception as e:
        import traceback
        print("="*50)
        print("❌ ERROR EN CLONACIÓN CRT -> MIC:")
        print(traceback.format_exc())
        print("="*50)
        return jsonify({"error": str(e)}), 500

# ========== PDF DESDE MIC GUARDADO ==========


@mic_bp.route('/<int:mic_id>/pdf', methods=['GET'])
def mic_pdf(mic_id):
    mic = MIC.query.get_or_404(mic_id)
    mic_data = to_dict_mic(mic)

    # Blindaje: campo 9 = campo 1
    mic_data["campo_9_datos_transporte"] = mic_data["campo_1_transporte"]

    filename = f"mic_{mic.id}.pdf"
    print("🎯 GENERANDO PDF DESDE MIC GUARDADO:")
    print(f"   📋 Campo 1 len: {len(mic_data['campo_1_transporte'])}")
    print(f"   📋 Campo 9 len: {len(mic_data['campo_9_datos_transporte'])}")
    print(f"   📦 Campo 38 len: {len(mic_data['campo_38_datos_campo11_crt'])}")

    generar_micdta_pdf_con_datos(mic_data, filename)
    return send_file(filename, as_attachment=True)

# ✅ RUTA: Verificar clonación de datos específicos


@mic_bp.route('/verify_clone/<int:crt_id>', methods=['GET'])
def verificar_clonacion(crt_id):
    try:
        crt = CRT.query.options(
            joinedload(CRT.remitente).joinedload(
                Remitente.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.transportadora).joinedload(
                Transportadora.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.destinatario).joinedload(
                Remitente.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.consignatario).joinedload(
                Remitente.ciudad).joinedload(Ciudad.pais),
        ).get_or_404(crt_id)

        campo_1 = formatear_entidad_completa_crt(crt.transportadora)
        campo_33 = formatear_entidad_completa_crt(crt.remitente)
        campo_34 = formatear_entidad_completa_crt(crt.destinatario)
        campo_35 = formatear_entidad_completa_crt(
            crt.consignatario) if crt.consignatario else campo_34

        return jsonify({
            "crt_numero": crt.numero_crt,
            "clonacion": {
                "campo_1_transportadora": {"texto": campo_1, "lineas": campo_1.split('\n'), "longitud": len(campo_1)},
                "campo_33_remitente": {"texto": campo_33, "lineas": campo_33.split('\n'), "longitud": len(campo_33)},
                "campo_34_destinatario": {"texto": campo_34, "lineas": campo_34.split('\n'), "longitud": len(campo_34)},
                "campo_35_consignatario": {"texto": campo_35, "lineas": campo_35.split('\n'), "longitud": len(campo_35)}
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ RUTA: Verificar procesamiento de gastos específicos


@mic_bp.route('/verify_gastos/<int:crt_id>', methods=['GET'])
def verificar_gastos(crt_id):
    try:
        crt = CRT.query.options(
            joinedload(CRT.gastos).joinedload(CRT_Gasto.moneda_remitente),
            joinedload(CRT.gastos).joinedload(CRT_Gasto.moneda_destinatario)
        ).get_or_404(crt_id)

        resultado_gastos = procesar_gastos_crt_para_mic(crt.gastos)

        gastos_detalle = []
        for gasto in crt.gastos:
            tramo = (gasto.tramo or "").strip()
            es_seguro = "seguro" in tramo.lower()

            valor_usado = None
            moneda_usada = ""

            if gasto.valor_remitente and gasto.valor_remitente not in [None, "None", ""]:
                valor_usado = float(gasto.valor_remitente)
                moneda_usada = gasto.moneda_remitente.nombre if gasto.moneda_remitente else ""
            elif gasto.valor_destinatario and gasto.valor_destinatario not in [None, "None", ""]:
                valor_usado = float(gasto.valor_destinatario)
                moneda_usada = gasto.moneda_destinatario.nombre if gasto.moneda_destinatario else ""

            gastos_detalle.append({
                "tramo": tramo,
                "es_seguro": es_seguro,
                "valor_usado": valor_usado,
                "moneda": moneda_usada,
                "valor_remitente": str(gasto.valor_remitente or ""),
                "valor_destinatario": str(gasto.valor_destinatario or "")
            })

        return jsonify({
            "crt_numero": crt.numero_crt,
            "gastos_detalle": gastos_detalle,
            "resultado_mic": resultado_gastos,
            "explicacion": {
                "campo_28": "Suma de todos los gastos que NO contengan 'seguro'",
                "campo_29": "Suma de los gastos que contengan 'seguro' en el tramo"
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ RUTA: Crear CRT de prueba con gastos


@mic_bp.route('/create_test_crt', methods=['POST'])
def crear_crt_prueba():
    try:
        from app.models import Moneda, Pais, Ciudad

        moneda = Moneda.query.filter_by(codigo='USD').first()
        if not moneda:
            moneda = Moneda(codigo='USD', nombre='Dólar Americano', simbolo='')
            db.session.add(moneda)
            db.session.flush()

        pais = Pais.query.filter_by(codigo='PY').first()
        if not pais:
            pais = Pais(codigo='PY', nombre='PARAGUAY')
            db.session.add(pais)
            db.session.flush()

        ciudad = Ciudad.query.filter_by(nombre='ASUNCIÓN').first()
        if not ciudad:
            ciudad = Ciudad(nombre='ASUNCIÓN', pais_id=pais.id)
            db.session.add(ciudad)
            db.session.flush()

        transportadora = Transportadora.query.first()
        remitente = Remitente.query.first()

        if not transportadora:
            transportadora = Transportadora(
                codigo='TEST001',
                nombre='TRANSPORTADORA TEST',
                direccion='DIRECCIÓN TEST',
                ciudad_id=ciudad.id,
                tipo_documento='RUC',
                numero_documento='12345678-9'
            )
            db.session.add(transportadora)
            db.session.flush()

        if not remitente:
            remitente = Remitente(
                nombre='REMITENTE TEST',
                direccion='DIRECCIÓN REMITENTE',
                ciudad_id=ciudad.id,
                tipo_documento='RUC',
                numero_documento='98765432-1'
            )
            db.session.add(remitente)
            db.session.flush()

        crt_test = CRT(
            numero_crt=f'TEST{datetime.now().strftime("%Y%m%d%H%M%S")}',
            estado='PRUEBA',
            remitente_id=remitente.id,
            destinatario_id=remitente.id,
            transportadora_id=transportadora.id,
            ciudad_emision_id=ciudad.id,
            pais_emision_id=pais.id,
            moneda_id=moneda.id,
            detalles_mercaderia='Mercadería de prueba para testing gastos MIC',
            peso_bruto=1000.0,
            declaracion_mercaderia=15000.00
        )
        db.session.add(crt_test)
        db.session.flush()

        gastos_ejemplo = [
            {'tramo': 'Flete terrestre principal', 'valor_remitente': 2500.00},
            {'tramo': 'Seguro de mercadería', 'valor_remitente': 300.00},
            {'tramo': 'Gastos portuarios', 'valor_remitente': 150.00},
            {'tramo': 'SEGURO TOTAL DE TRANSPORTE', 'valor_remitente': 200.00},
            {'tramo': 'Manipuleo y estiba', 'valor_remitente': 350.00},
            {'tramo': 'Prima de seguro internacional', 'valor_destinatario': 100.00},
            {'tramo': 'Otros gastos operativos', 'valor_destinatario': 75.00}
        ]

        for gasto_data in gastos_ejemplo:
            gasto = CRT_Gasto(
                crt_id=crt_test.id,
                tramo=gasto_data['tramo'],
                valor_remitente=gasto_data.get('valor_remitente'),
                moneda_remitente_id=moneda.id,
                valor_destinatario=gasto_data.get('valor_destinatario'),
                moneda_destinatario_id=moneda.id
            )
            db.session.add(gasto)

        db.session.commit()

        total_seguro = 300 + 200 + 100
        total_flete = 2500 + 150 + 350 + 75

        return jsonify({
            "message": "CRT de prueba creado exitosamente",
            "crt_id": crt_test.id,
            "numero_crt": crt_test.numero_crt,
            "gastos_creados": len(gastos_ejemplo),
            "totales_esperados": {"flete": total_flete, "seguro": total_seguro},
            "verificar_url": f"/api/mic/verify_gastos/{crt_test.id}",
            "generar_pdf_url": f"/api/mic/generate_pdf_from_crt/{crt_test.id}"
        }), 201

    except Exception as e:
        import traceback
        db.session.rollback()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

# ✅ LISTAR MICs (básico)


@mic_bp.route('/', methods=['GET'])
def listar_mics():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        mics = MIC.query.options(joinedload(MIC.crt)).order_by(MIC.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            "total": mics.total,
            "page": mics.page,
            "pages": mics.pages,
            "mics": [
                {
                    "id": mic.id,
                    "crt_id": mic.crt_id,
                    "crt_numero": mic.crt.numero_crt if mic.crt else "N/A",
                    "estado": mic.campo_4_estado,
                    "fecha": mic.campo_6_fecha.strftime('%Y-%m-%d') if mic.campo_6_fecha else "",
                    "creado_en": mic.creado_en.strftime('%Y-%m-%d %H:%M:%S') if getattr(mic, "creado_en", None) else ""
                }
                for mic in mics.items
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ CREAR MIC manual


@mic_bp.route('/', methods=['POST'])
def crear_mic():
    try:
        data = request.json

        campos_requeridos = ['campo_1_transporte',
                             'campo_23_numero_campo2_crt']
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({"error": f"Campo requerido: {campo}"}), 400

        mic = MIC(
            crt_id=data.get('crt_id'),
            campo_1_transporte=data.get('campo_1_transporte'),
            campo_2_numero=data.get('campo_2_numero', ''),
            campo_3_transporte=data.get('campo_3_transporte', ''),
            campo_4_estado=data.get('campo_4_estado', 'PROVISORIO'),
            campo_5_hoja=data.get('campo_5_hoja', '1 / 1'),
            campo_6_fecha=datetime.strptime(data.get(
                'campo_6_fecha'), '%Y-%m-%d') if data.get('campo_6_fecha') else datetime.now().date(),
            campo_7_pto_seguro=data.get('campo_7_pto_seguro', ''),
            campo_8_destino=data.get('campo_8_destino', ''),
            campo_9_datos_transporte=data.get(
                'campo_9_datos_transporte') or data.get('campo_1_transporte'),
            campo_10_numero=data.get('campo_10_numero', ''),
            campo_11_placa=data.get('campo_11_placa', ''),
            campo_12_modelo_chasis=data.get('campo_12_modelo_chasis', ''),
            campo_13_siempre_45=data.get('campo_13_siempre_45', '45 TON'),
            campo_14_anio=data.get('campo_14_anio', ''),
            campo_15_placa_semi=data.get('campo_15_placa_semi', ''),
            campo_16_asteriscos_1=data.get('campo_16_asteriscos_1', '******'),
            campo_17_asteriscos_2=data.get('campo_17_asteriscos_2', '******'),
            campo_18_asteriscos_3=data.get('campo_18_asteriscos_3', '******'),
            campo_19_asteriscos_4=data.get('campo_19_asteriscos_4', '******'),
            campo_20_asteriscos_5=data.get('campo_20_asteriscos_5', '******'),
            campo_21_asteriscos_6=data.get('campo_21_asteriscos_6', '******'),
            campo_22_asteriscos_7=data.get('campo_22_asteriscos_7', '******'),
            campo_23_numero_campo2_crt=data.get('campo_23_numero_campo2_crt'),
            campo_24_aduana=data.get('campo_24_aduana', ''),
            campo_25_moneda=data.get('campo_25_moneda', ''),
            campo_26_pais=data.get('campo_26_pais', '520-PARAGUAY'),
            campo_27_valor_campo16=data.get('campo_27_valor_campo16', ''),
            campo_28_total=data.get('campo_28_total', ''),
            campo_29_seguro=data.get('campo_29_seguro', ''),
            campo_30_tipo_bultos=data.get('campo_30_tipo_bultos', ''),
            campo_31_cantidad=data.get('campo_31_cantidad', ''),
            campo_32_peso_bruto=data.get('campo_32_peso_bruto', ''),
            campo_33_datos_campo1_crt=data.get(
                'campo_33_datos_campo1_crt', ''),
            campo_34_datos_campo4_crt=data.get(
                'campo_34_datos_campo4_crt', ''),
            campo_35_datos_campo6_crt=data.get(
                'campo_35_datos_campo6_crt', ''),
            campo_36_factura_despacho=data.get(
                'campo_36_factura_despacho', ''),
            campo_37_valor_manual=data.get('campo_37_valor_manual', ''),
            campo_38_datos_campo11_crt=data.get(
                'campo_38_datos_campo11_crt', ''),
            campo_40_tramo=data.get('campo_40_tramo', ''),
            creado_en=datetime.now()
        )

        db.session.add(mic)
        db.session.commit()

        return jsonify({
            "message": "MIC creado exitosamente",
            "id": mic.id,
            "pdf_url": f"/api/mic/{mic.id}/pdf"
        }), 201

    except Exception as e:
        import traceback
        db.session.rollback()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

# ========== OBTENER DATOS DEL CRT PARA AUTOCOMPLETAR MIC ==========


@mic_bp.route('/get_crt_data/<int:crt_id>', methods=['GET'])
def obtener_datos_crt_para_mic(crt_id):
    try:
        print(
            f"🔍 OBTENIENDO DATOS DEL CRT {crt_id} PARA AUTO-COMPLETAR MIC...")

        crt = CRT.query.options(
            joinedload(CRT.remitente).joinedload(
                Remitente.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.transportadora).joinedload(
                Transportadora.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.destinatario).joinedload(
                Remitente.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.consignatario).joinedload(
                Remitente.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.moneda),
            joinedload(CRT.gastos).joinedload(CRT_Gasto.moneda_remitente),
            joinedload(CRT.gastos).joinedload(CRT_Gasto.moneda_destinatario),
            joinedload(CRT.ciudad_emision).joinedload(Ciudad.pais),
            joinedload(CRT.pais_emision)
        ).get_or_404(crt_id)

        print(f"✅ CRT CARGADO: {crt.numero_crt}")

        transportadora_formateada = formatear_entidad_completa_crt(
            crt.transportadora) if crt.transportadora else ""
        remitente_formateado = formatear_entidad_completa_crt(
            crt.remitente) if crt.remitente else ""
        destinatario_formateado = formatear_entidad_completa_crt(
            crt.destinatario) if crt.destinatario else ""
        consignatario_formateado = formatear_entidad_completa_crt(
            crt.consignatario) if crt.consignatario else destinatario_formateado

        gastos_procesados = procesar_gastos_crt_para_mic(crt.gastos) if crt.gastos else {
            "campo_28_total": "", "campo_29_seguro": ""}

        datos_mic = {
            "numero_crt": crt.numero_crt or "",
            "fecha_emision": crt.fecha_emision.strftime('%Y-%m-%d') if crt.fecha_emision else "",

            "campo_1_transporte": transportadora_formateada,
            "campo_6_fecha": crt.fecha_emision.strftime('%Y-%m-%d') if crt.fecha_emision else "",
            "campo_8_destino": crt.lugar_entrega or "",
            "campo_9_datos_transporte": transportadora_formateada,
            "campo_23_numero_campo2_crt": crt.numero_crt or "",
            "campo_25_moneda": crt.moneda.nombre if crt.moneda else "DOLAR AMERICANO",
            "campo_26_pais": "520-PARAGUAY",
            "campo_27_valor_campo16": str(crt.declaracion_mercaderia or ""),
            "campo_32_peso_bruto": str(crt.peso_bruto or ""),
            "campo_38": crt.detalles_mercaderia or "",

            "campo_33_datos_campo1_crt": remitente_formateado,
            "campo_34_datos_campo4_crt": destinatario_formateado,
            "campo_35_datos_campo6_crt": consignatario_formateado,

            "campo_28_total": gastos_procesados["campo_28_total"],
            "campo_29_seguro": gastos_procesados["campo_29_seguro"],

            "campo_36_factura_despacho": (
                f"Factura: {crt.factura_exportacion} | Despacho: {crt.nro_despacho}"
                if crt.factura_exportacion and crt.nro_despacho
                else (f"Factura: {crt.factura_exportacion}" if crt.factura_exportacion
                      else f"Despacho: {crt.nro_despacho}" if crt.nro_despacho else "")
            ),

            "campos_autocompletados": [
                "campo_1_transporte", "campo_6_fecha", "campo_8_destino",
                "campo_9_datos_transporte", "campo_23_numero_campo2_crt",
                "campo_25_moneda", "campo_26_pais", "campo_27_valor_campo16",
                "campo_32_peso_bruto", "campo_38", "campo_33_datos_campo1_crt",
                "campo_34_datos_campo4_crt", "campo_35_datos_campo6_crt",
                "campo_28_total", "campo_29_seguro", "campo_36_factura_despacho"
            ]
        }

        return jsonify({
            "success": True,
            "crt_id": crt_id,
            "numero_crt": crt.numero_crt,
            "datos": datos_mic,
            "mensaje": f"Datos del CRT {crt.numero_crt} cargados exitosamente"
        })

    except Exception as e:
        import traceback
        print(f"❌ ERROR OBTENIENDO DATOS CRT {crt_id}:")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e), "mensaje": f"Error cargando datos del CRT {crt_id}"}), 500

# ==== UTIL NÚMEROS (formato "2.500,00" -> Decimal) ====


def _parse_num_es(val):
    """
    Acepta: "2.500,00", "2500,00", "2500.00", 2500, None -> Decimal o None
    """
    if val is None or val == "":
        return None
    if isinstance(val, (int, float, Decimal)):
        return Decimal(str(val))
    s = str(val).strip()
    s = s.replace('.', '').replace(',', '.')
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def _build_mic_model_from_dict(mic_data, crt_id=None):
    """
    Crea una instancia MIC (sin commit) a partir de mic_data ya armado.
    Respeta tus tipos declarados en models.py
    """
    # fechas
    f6 = mic_data.get('campo_6_fecha') or ""
    try:
        f6_date = datetime.strptime(
            f6, '%Y-%m-%d').date() if f6 else datetime.now().date()
    except Exception:
        f6_date = datetime.now().date()

    mic = MIC(
        crt_id=crt_id,
        campo_1_transporte=mic_data.get('campo_1_transporte', '')[:150],
        campo_2_numero=mic_data.get('campo_2_numero', '')[:30],
        campo_3_transporte=mic_data.get('campo_3_transporte', '')[:150],
        campo_4_estado=mic_data.get('campo_4_estado', 'PROVISORIO')[:30],
        campo_5_hoja=mic_data.get('campo_5_hoja', '1 / 1')[:20],
        campo_6_fecha=f6_date,
        campo_7_pto_seguro=mic_data.get('campo_7_pto_seguro', '')[:100],
        campo_8_destino=mic_data.get('campo_8_destino', '')[:100],
        campo_9_datos_transporte=(mic_data.get(
            'campo_9_datos_transporte') or mic_data.get('campo_1_transporte', ''))[:200],
        campo_10_numero=mic_data.get('campo_10_numero', '')[:30],
        campo_11_placa=mic_data.get('campo_11_placa', '')[:20],
        campo_12_modelo_chasis=mic_data.get('campo_12_modelo_chasis', '')[:80],
        campo_13_siempre_45=(mic_data.get(
            'campo_13_siempre_45', '45 TON') or '')[:10],
        campo_14_anio=mic_data.get('campo_14_anio', '')[:10],
        campo_15_placa_semi=mic_data.get('campo_15_placa_semi', '')[:20],
        campo_16_asteriscos_1=mic_data.get(
            'campo_16_asteriscos_1', '******')[:20],
        campo_17_asteriscos_2=mic_data.get(
            'campo_17_asteriscos_2', '******')[:20],
        campo_18_asteriscos_3=mic_data.get(
            'campo_18_asteriscos_3', '******')[:20],
        campo_19_asteriscos_4=mic_data.get(
            'campo_19_asteriscos_4', '******')[:20],
        campo_20_asteriscos_5=mic_data.get(
            'campo_20_asteriscos_5', '******')[:20],
        campo_21_asteriscos_6=mic_data.get(
            'campo_21_asteriscos_6', '******')[:20],
        campo_22_asteriscos_7=mic_data.get(
            'campo_22_asteriscos_7', '******')[:20],
        campo_23_numero_campo2_crt=mic_data.get(
            'campo_23_numero_campo2_crt', '')[:30],
        campo_24_aduana=mic_data.get('campo_24_aduana', '')[:100],
        campo_25_moneda=mic_data.get('campo_25_moneda', '')[:30],
        campo_26_pais=mic_data.get('campo_26_pais', '')[:30],
        campo_27_valor_campo16=_parse_num_es(
            mic_data.get('campo_27_valor_campo16')),
        campo_28_total=_parse_num_es(mic_data.get('campo_28_total')),
        campo_29_seguro=_parse_num_es(mic_data.get('campo_29_seguro')),
        campo_30_tipo_bultos=mic_data.get('campo_30_tipo_bultos', '')[:30],
        campo_31_cantidad=_parse_num_es(mic_data.get('campo_31_cantidad')),
        campo_32_peso_bruto=_parse_num_es(mic_data.get('campo_32_peso_bruto')),
        campo_33_datos_campo1_crt=mic_data.get(
            'campo_33_datos_campo1_crt', '')[:200],
        campo_34_datos_campo4_crt=mic_data.get(
            'campo_34_datos_campo4_crt', '')[:200],
        campo_35_datos_campo6_crt=mic_data.get(
            'campo_35_datos_campo6_crt', '')[:200],
        campo_36_factura_despacho=mic_data.get(
            'campo_36_factura_despacho', '')[:100],
        campo_37_valor_manual=mic_data.get('campo_37_valor_manual', '')[:100],
        campo_38_datos_campo11_crt=mic_data.get(
            'campo_38_datos_campo11_crt', ''),
        campo_40_tramo=mic_data.get('campo_40_tramo', '')[:200],
        creado_en=datetime.now()
    )
    return mic

# ========== GUARDAR MIC DESDE CRT (JSON; opcional PDF) ==========


@mic_bp.route('/save_from_crt/<int:crt_id>', methods=['POST'])
def guardar_mic_desde_crt(crt_id):
    """
    Crea y guarda un MIC a partir de un CRT y devuelve JSON con el ID.
    Opcional: ?pdf=1 para devolver el PDF binario inmediato.
    """
    try:
        user_data = request.json if request.is_json else {}

        crt = CRT.query.options(
            joinedload(CRT.remitente).joinedload(
                Remitente.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.transportadora).joinedload(
                Transportadora.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.destinatario).joinedload(
                Remitente.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.consignatario).joinedload(
                Remitente.ciudad).joinedload(Ciudad.pais),
            joinedload(CRT.moneda),
            joinedload(CRT.gastos).joinedload(CRT_Gasto.moneda_remitente),
            joinedload(CRT.gastos).joinedload(CRT_Gasto.moneda_destinatario),
            joinedload(CRT.ciudad_emision).joinedload(Ciudad.pais)
        ).get_or_404(crt_id)

        campo_1_transportadora = formatear_entidad_completa_crt(
            crt.transportadora)
        campo_33_remitente = formatear_entidad_completa_crt(crt.remitente)
        campo_34_destinatario = formatear_entidad_completa_crt(
            crt.destinatario)
        campo_35_consignatario = formatear_entidad_completa_crt(
            crt.consignatario) if crt.consignatario else campo_34_destinatario

        gastos_procesados = procesar_gastos_crt_para_mic(crt.gastos)

        mic_data = {
            "campo_1_transporte": campo_1_transportadora,
            "campo_9_datos_transporte": campo_1_transportadora,
            "campo_33_datos_campo1_crt": campo_33_remitente,
            "campo_34_datos_campo4_crt": campo_34_destinatario,
            "campo_35_datos_campo6_crt": campo_35_consignatario,
            "campo_28_total": gastos_procesados["campo_28_total"],
            "campo_29_seguro": gastos_procesados["campo_29_seguro"],
            "campo_2_numero": "",
            "campo_3_transporte": "",
            "campo_4_estado": "PROVISORIO",
            "campo_5_hoja": "1 / 1",
            "campo_6_fecha": crt.fecha_emision.strftime('%Y-%m-%d') if crt.fecha_emision else "",
            "campo_7_pto_seguro": "",
            "campo_8_destino": crt.lugar_entrega or "",
            "campo_10_numero": "",
            "campo_11_placa": "",
            "campo_12_modelo_chasis": "",
            "campo_13_siempre_45": "45 TON",
            "campo_14_anio": "",
            "campo_15_placa_semi": "",
            "campo_16_asteriscos_1": "******",
            "campo_17_asteriscos_2": "******",
            "campo_18_asteriscos_3": "******",
            "campo_19_asteriscos_4": "******",
            "campo_20_asteriscos_5": "******",
            "campo_21_asteriscos_6": "******",
            "campo_22_asteriscos_7": "******",
            "campo_23_numero_campo2_crt": crt.numero_crt or "",
            "campo_24_aduana": "",
            "campo_25_moneda": crt.moneda.nombre if crt.moneda else "",
            "campo_26_pais": "520-PARAGUAY",
            "campo_27_valor_campo16": str(crt.declaracion_mercaderia or ""),
            "campo_30_tipo_bultos": "",
            "campo_31_cantidad": "",
            "campo_32_peso_bruto": str(crt.peso_bruto or ""),
            "campo_36_factura_despacho": (
                f"Factura: {crt.factura_exportacion or ''} | Despacho: {crt.nro_despacho or ''}"
                if crt.factura_exportacion or crt.nro_despacho else ""
            ),
            "campo_37_valor_manual": "",
            "campo_38_datos_campo11_crt": (crt.detalles_mercaderia or "")[:1500],
            "campo_40_tramo": "",
        }

        if user_data:
            for k in ['campo_28_total', 'campo_29_seguro']:
                if k not in user_data or not user_data.get(k):
                    user_data.pop(k, None)
            if 'campo_38' in user_data:
                user_data['campo_38_datos_campo11_crt'] = user_data.pop(
                    'campo_38')
            mic_data.update(user_data)

        mic = _build_mic_model_from_dict(mic_data, crt_id=crt.id)
        db.session.add(mic)
        db.session.commit()

        resp = {"message": "MIC guardado correctamente",
                "id": mic.id, "pdf_url": f"/api/mic/{mic.id}/pdf"}

        want_pdf = request.args.get('pdf') in ['1', 'true', 'True'] or (
            isinstance(user_data, dict) and user_data.get('pdf'))
        if not want_pdf:
            return jsonify(resp), 201

        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            filename = tmp_file.name
        generar_micdta_pdf_con_datos(mic_data, filename)
        response = send_file(filename, as_attachment=True,
                             download_name=f"MIC_CRT_{crt.numero_crt or crt.id}.pdf")
        response.call_on_close(lambda: os.unlink(filename))
        return response

    except Exception as e:
        import traceback
        db.session.rollback()
        print("❌ ERROR guardando MIC desde CRT:")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Recuerda registrar el blueprint en tu app principal:
# from app.routes.mic import mic_bp
# app.register_blueprint(mic_bp)
