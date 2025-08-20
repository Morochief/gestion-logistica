# ========== RUTAS PARA MICs GUARDADOS ==========
from flask import Blueprint, request, jsonify, send_file
from sqlalchemy.orm import joinedload
from datetime import datetime
from app.models import db, MIC, CRT
from app.utils.layout_mic import generar_micdta_pdf_con_datos
import tempfile
import os

# Blueprint para MICs guardados
mic_guardados_bp = Blueprint(
    'mic_guardados', __name__, url_prefix='/api/mic-guardados')

# ========== CREAR MIC Y GUARDARLO ==========


@mic_guardados_bp.route('/', methods=['POST'])
def crear_mic_guardado():
    """
    ✅ Crea un MIC completo desde datos del formulario y lo guarda en BD
    """
    try:
        data = request.json

        print(f"🔄 CREANDO MIC GUARDADO...")
        print(f"📊 Datos recibidos: {len(data)} campos")

        # Validar campos requeridos básicos
        campos_requeridos = ['campo_23_numero_campo2_crt']
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({"error": f"Campo requerido: {campo}"}), 400

        # Auto-completar campos 16-22 con ****** si están vacíos
        campos_asteriscos = [16, 17, 18, 19, 20, 21, 22]
        for num in campos_asteriscos:
            campo_key = f'campo_{num}_asteriscos_{num-15}'
            if not data.get(campo_key) or data.get(campo_key).strip() == "":
                data[campo_key] = "******"

        # Asegurar que campo 9 = campo 1 (datos transportadora)
        if data.get('campo_1_transporte') and not data.get('campo_9_datos_transporte'):
            data['campo_9_datos_transporte'] = data['campo_1_transporte']

        # Procesar fecha si viene como string
        fecha_emision = None
        if data.get('campo_6_fecha'):
            try:
                if isinstance(data['campo_6_fecha'], str):
                    fecha_emision = datetime.strptime(
                        data['campo_6_fecha'], '%Y-%m-%d').date()
                else:
                    fecha_emision = data['campo_6_fecha']
            except ValueError:
                fecha_emision = datetime.now().date()
        else:
            fecha_emision = datetime.now().date()

        # Crear el MIC en base de datos
        mic = MIC(
            crt_id=data.get('crt_id'),
            campo_1_transporte=data.get('campo_1_transporte', ''),
            campo_2_numero=data.get('campo_2_numero', ''),
            campo_3_transporte=data.get('campo_3_transporte', ''),
            campo_4_estado=data.get('campo_4_estado', 'PROVISORIO'),
            campo_5_hoja=data.get('campo_5_hoja', '1 / 1'),
            campo_6_fecha=fecha_emision,
            campo_7_pto_seguro=data.get('campo_7_pto_seguro', ''),
            campo_8_destino=data.get('campo_8_destino', ''),
            campo_9_datos_transporte=data.get('campo_9_datos_transporte', ''),
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
            campo_23_numero_campo2_crt=data.get(
                'campo_23_numero_campo2_crt', ''),
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

        print(f"✅ MIC guardado con ID: {mic.id}")

        return jsonify({
            "message": "MIC creado y guardado exitosamente",
            "id": mic.id,
            "numero_carta_porte": mic.campo_23_numero_campo2_crt,
            "estado": mic.campo_4_estado,
            "fecha_creacion": mic.creado_en.strftime('%Y-%m-%d %H:%M:%S'),
            "pdf_url": f"/api/mic-guardados/{mic.id}/pdf"
        }), 201

    except Exception as e:
        import traceback
        db.session.rollback()
        print(f"❌ Error creando MIC guardado: {e}")
        print(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

# ========== LISTAR MICs GUARDADOS ==========


@mic_guardados_bp.route('/', methods=['GET'])
def listar_mics_guardados():
    """
    ✅ Lista todos los MICs guardados con paginación y filtros
    """
    try:
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get(
            'per_page', 20, type=int), 100)  # Máximo 100
        estado = request.args.get('estado', '').strip()
        numero_carta = request.args.get('numero_carta', '').strip()
        fecha_desde = request.args.get('fecha_desde', '').strip()
        fecha_hasta = request.args.get('fecha_hasta', '').strip()

        print(f"📋 LISTANDO MICs GUARDADOS...")
        print(f"   📄 Página: {page}, Por página: {per_page}")
        print(
            f"   🔍 Filtros: estado='{estado}', numero_carta='{numero_carta}'")
        print(f"   📅 Fechas: desde='{fecha_desde}', hasta='{fecha_hasta}'")

        # Construir query base
        query = MIC.query.options(joinedload(MIC.crt))

        # Aplicar filtros
        if estado:
            query = query.filter(MIC.campo_4_estado.ilike(f'%{estado}%'))

        if numero_carta:
            query = query.filter(
                MIC.campo_23_numero_campo2_crt.ilike(f'%{numero_carta}%'))

        if fecha_desde:
            try:
                fecha_desde_dt = datetime.strptime(
                    fecha_desde, '%Y-%m-%d').date()
                query = query.filter(MIC.campo_6_fecha >= fecha_desde_dt)
            except ValueError:
                pass

        if fecha_hasta:
            try:
                fecha_hasta_dt = datetime.strptime(
                    fecha_hasta, '%Y-%m-%d').date()
                query = query.filter(MIC.campo_6_fecha <= fecha_hasta_dt)
            except ValueError:
                pass

        # Ordenar por fecha de creación (más recientes primero)
        query = query.order_by(MIC.id.desc())

        # Paginar
        mics_paginados = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # Formatear resultados
        mics_data = []
        for mic in mics_paginados.items:
            mic_data = {
                "id": mic.id,
                "crt_id": mic.crt_id,
                "numero_carta_porte": mic.campo_23_numero_campo2_crt,
                "estado": mic.campo_4_estado,
                "fecha_emision": mic.campo_6_fecha.strftime('%Y-%m-%d') if mic.campo_6_fecha else "",
                "transportadora": mic.campo_1_transporte[:100] + "..." if len(mic.campo_1_transporte or "") > 100 else (mic.campo_1_transporte or ""),
                "destino": mic.campo_8_destino or "",
                "placa_camion": mic.campo_11_placa or "",
                "peso_bruto": str(mic.campo_32_peso_bruto or ""),
                "moneda": mic.campo_25_moneda or "",
                "creado_en": mic.creado_en.strftime('%Y-%m-%d %H:%M:%S') if mic.creado_en else "",
                "crt_numero": mic.crt.numero_crt if mic.crt else "N/A"
            }
            mics_data.append(mic_data)

        resultado = {
            "mics": mics_data,
            "pagination": {
                "page": mics_paginados.page,
                "pages": mics_paginados.pages,
                "per_page": mics_paginados.per_page,
                "total": mics_paginados.total,
                "has_next": mics_paginados.has_next,
                "has_prev": mics_paginados.has_prev
            },
            "filtros_aplicados": {
                "estado": estado,
                "numero_carta": numero_carta,
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta
            }
        }

        print(
            f"✅ Enviados {len(mics_data)} MICs de {mics_paginados.total} totales")
        return jsonify(resultado)

    except Exception as e:
        print(f"❌ Error listando MICs: {e}")
        return jsonify({"error": str(e)}), 500

# ========== OBTENER MIC POR ID ==========


@mic_guardados_bp.route('/<int:mic_id>', methods=['GET'])
def obtener_mic_por_id(mic_id):
    """
    ✅ Obtiene un MIC específico por ID con todos sus datos
    """
    try:
        print(f"🔍 OBTENIENDO MIC ID: {mic_id}")

        mic = MIC.query.options(joinedload(MIC.crt)).get_or_404(mic_id)

        # Función helper para convertir a string seguro
        def safe_str(val):
            return "" if val is None else str(val)

        mic_data = {
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
            "creado_en": mic.creado_en.strftime('%Y-%m-%d %H:%M:%S') if mic.creado_en else "",
            "crt_numero": mic.crt.numero_crt if mic.crt else "N/A"
        }

        print(f"✅ MIC {mic_id} obtenido exitosamente")
        return jsonify(mic_data)

    except Exception as e:
        print(f"❌ Error obteniendo MIC {mic_id}: {e}")
        return jsonify({"error": str(e)}), 404

# ========== ACTUALIZAR MIC ==========


@mic_guardados_bp.route('/<int:mic_id>', methods=['PUT'])
def actualizar_mic(mic_id):
    """
    ✅ Actualiza un MIC existente
    """
    try:
        print(f"🔄 ACTUALIZANDO MIC ID: {mic_id}")

        mic = MIC.query.get_or_404(mic_id)
        data = request.json

        # Actualizar campos permitidos
        campos_actualizables = [
            'campo_1_transporte', 'campo_2_numero', 'campo_3_transporte', 'campo_4_estado',
            'campo_5_hoja', 'campo_6_fecha', 'campo_7_pto_seguro', 'campo_8_destino',
            'campo_9_datos_transporte', 'campo_10_numero', 'campo_11_placa', 'campo_12_modelo_chasis',
            'campo_13_siempre_45', 'campo_14_anio', 'campo_15_placa_semi', 'campo_16_asteriscos_1',
            'campo_17_asteriscos_2', 'campo_18_asteriscos_3', 'campo_19_asteriscos_4', 'campo_20_asteriscos_5',
            'campo_21_asteriscos_6', 'campo_22_asteriscos_7', 'campo_23_numero_campo2_crt', 'campo_24_aduana',
            'campo_25_moneda', 'campo_26_pais', 'campo_27_valor_campo16', 'campo_28_total',
            'campo_29_seguro', 'campo_30_tipo_bultos', 'campo_31_cantidad', 'campo_32_peso_bruto',
            'campo_33_datos_campo1_crt', 'campo_34_datos_campo4_crt', 'campo_35_datos_campo6_crt',
            'campo_36_factura_despacho', 'campo_37_valor_manual', 'campo_38_datos_campo11_crt', 'campo_40_tramo'
        ]

        campos_actualizados = []
        for campo in campos_actualizables:
            if campo in data:
                if campo == 'campo_6_fecha' and data[campo]:
                    # Procesar fecha especialmente
                    try:
                        if isinstance(data[campo], str):
                            setattr(mic, campo, datetime.strptime(
                                data[campo], '%Y-%m-%d').date())
                        else:
                            setattr(mic, campo, data[campo])
                    except ValueError:
                        continue
                else:
                    setattr(mic, campo, data[campo])
                campos_actualizados.append(campo)

        # Asegurar que campo 9 = campo 1 si se actualiza campo 1
        if 'campo_1_transporte' in data and not data.get('campo_9_datos_transporte'):
            mic.campo_9_datos_transporte = data['campo_1_transporte']
            if 'campo_9_datos_transporte' not in campos_actualizados:
                campos_actualizados.append('campo_9_datos_transporte')

        db.session.commit()

        print(f"✅ MIC {mic_id} actualizado. Campos: {len(campos_actualizados)}")
        return jsonify({
            "message": "MIC actualizado exitosamente",
            "id": mic.id,
            "campos_actualizados": campos_actualizados,
            "numero_carta_porte": mic.campo_23_numero_campo2_crt,
            "estado": mic.campo_4_estado
        })

    except Exception as e:
        import traceback
        db.session.rollback()
        print(f"❌ Error actualizando MIC {mic_id}: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# ========== ELIMINAR MIC ==========


@mic_guardados_bp.route('/<int:mic_id>', methods=['DELETE'])
def eliminar_mic(mic_id):
    """
    ✅ Elimina un MIC (soft delete cambiando estado a ANULADO)
    """
    try:
        print(f"🗑️ ELIMINANDO MIC ID: {mic_id}")

        mic = MIC.query.get_or_404(mic_id)
        numero_carta = mic.campo_23_numero_campo2_crt

        # Soft delete: cambiar estado a ANULADO en lugar de eliminar físicamente
        mic.campo_4_estado = "ANULADO"
        db.session.commit()

        print(f"✅ MIC {mic_id} marcado como ANULADO")
        return jsonify({
            "message": "MIC anulado exitosamente",
            "id": mic.id,
            "numero_carta_porte": numero_carta,
            "estado": "ANULADO"
        })

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error eliminando MIC {mic_id}: {e}")
        return jsonify({"error": str(e)}), 500

# ========== GENERAR PDF DESDE MIC GUARDADO ==========


@mic_guardados_bp.route('/<int:mic_id>/pdf', methods=['GET'])
def generar_pdf_mic_guardado(mic_id):
    """
    ✅ Genera PDF de un MIC guardado
    """
    try:
        print(f"📄 GENERANDO PDF MIC GUARDADO ID: {mic_id}")

        mic = MIC.query.get_or_404(mic_id)

        # Convertir MIC a dict para el generador de PDF
        def safe_str(val):
            return "" if val is None else str(val)

        mic_data = {
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
            "campo_40_tramo": safe_str(mic.campo_40_tramo)
        }

        # Generar archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            filename = tmp_file.name

        generar_micdta_pdf_con_datos(mic_data, filename)

        # Nombre del archivo de descarga
        download_name = f"MIC_{mic.campo_23_numero_campo2_crt or mic.id}_{datetime.now().strftime('%Y%m%d')}.pdf"

        response = send_file(
            filename,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/pdf'
        )

        # Limpiar archivo temporal después de enviarlo
        response.call_on_close(lambda: os.unlink(filename))

        print(f"✅ PDF generado para MIC {mic_id}: {download_name}")
        return response

    except Exception as e:
        import traceback
        print(f"❌ Error generando PDF para MIC {mic_id}: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# ========== ESTADÍSTICAS ==========


@mic_guardados_bp.route('/stats', methods=['GET'])
def obtener_estadisticas():
    """
    ✅ Obtiene estadísticas generales de MICs guardados
    """
    try:
        print("📊 OBTENIENDO ESTADÍSTICAS DE MICs")

        # Contar por estado
        stats_estado = db.session.query(
            MIC.campo_4_estado,
            db.func.count(MIC.id).label('cantidad')
        ).group_by(MIC.campo_4_estado).all()

        # Contar por mes (últimos 6 meses)
        stats_mes = db.session.query(
            db.func.date_trunc('month', MIC.creado_en).label('mes'),
            db.func.count(MIC.id).label('cantidad')
        ).filter(
            MIC.creado_en >= datetime.now() - db.text("INTERVAL '6 months'")
        ).group_by(
            db.func.date_trunc('month', MIC.creado_en)
        ).order_by('mes').all()

        # Total general
        total_mics = MIC.query.count()

        # MICs creados hoy
        hoy = datetime.now().date()
        mics_hoy = MIC.query.filter(
            db.func.date(MIC.creado_en) == hoy
        ).count()

        # MICs creados esta semana
        desde_semana = datetime.now() - db.text("INTERVAL '7 days'")
        mics_semana = MIC.query.filter(MIC.creado_en >= desde_semana).count()

        resultado = {
            "total_mics": total_mics,
            "mics_hoy": mics_hoy,
            "mics_semana": mics_semana,
            "por_estado": [
                {"estado": estado, "cantidad": cantidad}
                for estado, cantidad in stats_estado
            ],
            "por_mes": [
                {
                    "mes": mes.strftime('%Y-%m') if mes else "",
                    "cantidad": cantidad
                }
                for mes, cantidad in stats_mes
            ]
        }

        print(f"✅ Estadísticas obtenidas: {total_mics} MICs totales")
        return jsonify(resultado)

    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return jsonify({"error": str(e)}), 500

# ========== BÚSQUEDA AVANZADA ==========


@mic_guardados_bp.route('/search', methods=['POST'])
def busqueda_avanzada():
    """
    ✅ Búsqueda avanzada de MICs con múltiples criterios
    """
    try:
        data = request.json
        print(f"🔍 BÚSQUEDA AVANZADA DE MICs")
        print(f"📊 Criterios: {data}")

        query = MIC.query.options(joinedload(MIC.crt))

        # Aplicar filtros dinámicos
        if data.get('numero_carta'):
            query = query.filter(MIC.campo_23_numero_campo2_crt.ilike(
                f"%{data['numero_carta']}%"))

        if data.get('transportadora'):
            query = query.filter(MIC.campo_1_transporte.ilike(
                f"%{data['transportadora']}%"))

        if data.get('placa'):
            query = query.filter(
                MIC.campo_11_placa.ilike(f"%{data['placa']}%"))

        if data.get('estado'):
            query = query.filter(MIC.campo_4_estado == data['estado'])

        if data.get('destino'):
            query = query.filter(
                MIC.campo_8_destino.ilike(f"%{data['destino']}%"))

        if data.get('fecha_desde'):
            try:
                fecha_desde = datetime.strptime(
                    data['fecha_desde'], '%Y-%m-%d').date()
                query = query.filter(MIC.campo_6_fecha >= fecha_desde)
            except ValueError:
                pass

        if data.get('fecha_hasta'):
            try:
                fecha_hasta = datetime.strptime(
                    data['fecha_hasta'], '%Y-%m-%d').date()
                query = query.filter(MIC.campo_6_fecha <= fecha_hasta)
            except ValueError:
                pass

        if data.get('peso_min'):
            try:
                peso_min = float(data['peso_min'])
                query = query.filter(MIC.campo_32_peso_bruto >= peso_min)
            except (ValueError, TypeError):
                pass

        if data.get('peso_max'):
            try:
                peso_max = float(data['peso_max'])
                query = query.filter(MIC.campo_32_peso_bruto <= peso_max)
            except (ValueError, TypeError):
                pass

        # Ordenamiento
        orden = data.get('orden', 'fecha_desc')
        if orden == 'fecha_asc':
            query = query.order_by(MIC.campo_6_fecha.asc())
        elif orden == 'fecha_desc':
            query = query.order_by(MIC.campo_6_fecha.desc())
        elif orden == 'numero_asc':
            query = query.order_by(MIC.campo_23_numero_campo2_crt.asc())
        elif orden == 'numero_desc':
            query = query.order_by(MIC.campo_23_numero_campo2_crt.desc())
        else:
            query = query.order_by(MIC.id.desc())

        # Paginación
        page = data.get('page', 1)
        per_page = min(data.get('per_page', 20), 100)

        mics_paginados = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # Formatear resultados
        mics_data = []
        for mic in mics_paginados.items:
            mic_data = {
                "id": mic.id,
                "numero_carta_porte": mic.campo_23_numero_campo2_crt,
                "estado": mic.campo_4_estado,
                "fecha_emision": mic.campo_6_fecha.strftime('%Y-%m-%d') if mic.campo_6_fecha else "",
                "transportadora": (mic.campo_1_transporte or "")[:100],
                "destino": mic.campo_8_destino or "",
                "placa_camion": mic.campo_11_placa or "",
                "peso_bruto": str(mic.campo_32_peso_bruto or ""),
                "moneda": mic.campo_25_moneda or "",
                "creado_en": mic.creado_en.strftime('%Y-%m-%d %H:%M:%S') if mic.creado_en else ""
            }
            mics_data.append(mic_data)

        resultado = {
            "mics": mics_data,
            "pagination": {
                "page": mics_paginados.page,
                "pages": mics_paginados.pages,
                "per_page": mics_paginados.per_page,
                "total": mics_paginados.total,
                "has_next": mics_paginados.has_next,
                "has_prev": mics_paginados.has_prev
            },
            "criterios_busqueda": data
        }

        print(
            f"✅ Búsqueda completada: {len(mics_data)} resultados de {mics_paginados.total} totales")
        return jsonify(resultado)

    except Exception as e:
        print(f"❌ Error en búsqueda avanzada: {e}")
        return jsonify({"error": str(e)}), 500

# ========== CREAR DESDE CRT Y GUARDAR ==========


@mic_guardados_bp.route('/crear-desde-crt/<int:crt_id>', methods=['POST'])
def crear_mic_desde_crt_y_guardar(crt_id):
    """
    ✅ Crea un MIC desde un CRT, permite edición y lo guarda en BD
    """
    try:
        user_data = request.json if request.is_json else {}

        print(f"🔄 CREANDO MIC DESDE CRT {crt_id} Y GUARDANDO...")

        # Reutilizar la lógica existente del módulo MIC
        from app.routes.mic import formatear_entidad_completa_crt, procesar_gastos_crt_para_mic
        from sqlalchemy.orm import joinedload

        # Cargar CRT con todas las relaciones
        crt = CRT.query.options(
            joinedload(CRT.remitente).joinedload(Ciudad.pais),
            joinedload(CRT.transportadora).joinedload(Ciudad.pais),
            joinedload(CRT.destinatario).joinedload(Ciudad.pais),
            joinedload(CRT.consignatario).joinedload(Ciudad.pais),
            joinedload(CRT.moneda),
            joinedload(CRT.gastos),
            joinedload(CRT.ciudad_emision).joinedload(Ciudad.pais)
        ).get_or_404(crt_id)

        # Formatear entidades completas
        campo_1_transportadora = formatear_entidad_completa_crt(
            crt.transportadora)
        campo_33_remitente = formatear_entidad_completa_crt(crt.remitente)
        campo_34_destinatario = formatear_entidad_completa_crt(
            crt.destinatario)
        campo_35_consignatario = formatear_entidad_completa_crt(
            crt.consignatario) if crt.consignatario else campo_34_destinatario

        # Procesar gastos
        gastos_procesados = procesar_gastos_crt_para_mic(crt.gastos)

        # Construir datos base del MIC
        mic_data_base = {
            "crt_id": crt.id,
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
            "campo_6_fecha": crt.fecha_emision.strftime('%Y-%m-%d') if crt.fecha_emision else datetime.now().strftime('%Y-%m-%d'),
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

        # Aplicar datos del usuario (sobrescribir campos base si se proporcionan)
        mic_data_final = {**mic_data_base, **user_data}

        # Procesar fecha
        fecha_emision = None
        if mic_data_final.get('campo_6_fecha'):
            try:
                if isinstance(mic_data_final['campo_6_fecha'], str):
                    fecha_emision = datetime.strptime(
                        mic_data_final['campo_6_fecha'], '%Y-%m-%d').date()
                else:
                    fecha_emision = mic_data_final['campo_6_fecha']
            except ValueError:
                fecha_emision = datetime.now().date()
        else:
            fecha_emision = datetime.now().date()

        # Crear MIC en base de datos
        mic = MIC(
            crt_id=crt.id,
            campo_1_transporte=mic_data_final.get('campo_1_transporte', ''),
            campo_2_numero=mic_data_final.get('campo_2_numero', ''),
            campo_3_transporte=mic_data_final.get('campo_3_transporte', ''),
            campo_4_estado=mic_data_final.get('campo_4_estado', 'PROVISORIO'),
            campo_5_hoja=mic_data_final.get('campo_5_hoja', '1 / 1'),
            campo_6_fecha=fecha_emision,
            campo_7_pto_seguro=mic_data_final.get('campo_7_pto_seguro', ''),
            campo_8_destino=mic_data_final.get('campo_8_destino', ''),
            campo_9_datos_transporte=mic_data_final.get(
                'campo_9_datos_transporte', ''),
            campo_10_numero=mic_data_final.get('campo_10_numero', ''),
            campo_11_placa=mic_data_final.get('campo_11_placa', ''),
            campo_12_modelo_chasis=mic_data_final.get(
                'campo_12_modelo_chasis', ''),
            campo_13_siempre_45=mic_data_final.get(
                'campo_13_siempre_45', '45 TON'),
            campo_14_anio=mic_data_final.get('campo_14_anio', ''),
            campo_15_placa_semi=mic_data_final.get('campo_15_placa_semi', ''),
            campo_16_asteriscos_1=mic_data_final.get(
                'campo_16_asteriscos_1', '******'),
            campo_17_asteriscos_2=mic_data_final.get(
                'campo_17_asteriscos_2', '******'),
            campo_18_asteriscos_3=mic_data_final.get(
                'campo_18_asteriscos_3', '******'),
            campo_19_asteriscos_4=mic_data_final.get(
                'campo_19_asteriscos_4', '******'),
            campo_20_asteriscos_5=mic_data_final.get(
                'campo_20_asteriscos_5', '******'),
            campo_21_asteriscos_6=mic_data_final.get(
                'campo_21_asteriscos_6', '******'),
            campo_22_asteriscos_7=mic_data_final.get(
                'campo_22_asteriscos_7', '******'),
            campo_23_numero_campo2_crt=mic_data_final.get(
                'campo_23_numero_campo2_crt', ''),
            campo_24_aduana=mic_data_final.get('campo_24_aduana', ''),
            campo_25_moneda=mic_data_final.get('campo_25_moneda', ''),
            campo_26_pais=mic_data_final.get('campo_26_pais', '520-PARAGUAY'),
            campo_27_valor_campo16=mic_data_final.get(
                'campo_27_valor_campo16', ''),
            campo_28_total=mic_data_final.get('campo_28_total', ''),
            campo_29_seguro=mic_data_final.get('campo_29_seguro', ''),
            campo_30_tipo_bultos=mic_data_final.get(
                'campo_30_tipo_bultos', ''),
            campo_31_cantidad=mic_data_final.get('campo_31_cantidad', ''),
            campo_32_peso_bruto=mic_data_final.get('campo_32_peso_bruto', ''),
            campo_33_datos_campo1_crt=mic_data_final.get(
                'campo_33_datos_campo1_crt', ''),
            campo_34_datos_campo4_crt=mic_data_final.get(
                'campo_34_datos_campo4_crt', ''),
            campo_35_datos_campo6_crt=mic_data_final.get(
                'campo_35_datos_campo6_crt', ''),
            campo_36_factura_despacho=mic_data_final.get(
                'campo_36_factura_despacho', ''),
            campo_37_valor_manual=mic_data_final.get(
                'campo_37_valor_manual', ''),
            campo_38_datos_campo11_crt=mic_data_final.get(
                'campo_38_datos_campo11_crt', ''),
            campo_40_tramo=mic_data_final.get('campo_40_tramo', ''),
            creado_en=datetime.now()
        )

        db.session.add(mic)
        db.session.commit()

        print(f"✅ MIC creado desde CRT {crt_id} y guardado con ID: {mic.id}")

        return jsonify({
            "message": "MIC creado desde CRT y guardado exitosamente",
            "id": mic.id,
            "crt_id": crt.id,
            "crt_numero": crt.numero_crt,
            "numero_carta_porte": mic.campo_23_numero_campo2_crt,
            "estado": mic.campo_4_estado,
            "fecha_creacion": mic.creado_en.strftime('%Y-%m-%d %H:%M:%S'),
            "gastos_procesados": {
                "flete": mic_data_final.get('campo_28_total', ''),
                "seguro": mic_data_final.get('campo_29_seguro', '')
            },
            "pdf_url": f"/api/mic-guardados/{mic.id}/pdf"
        }), 201

    except Exception as e:
        import traceback
        db.session.rollback()
        print(f"❌ Error creando MIC desde CRT {crt_id}: {e}")
        print(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500
