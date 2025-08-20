# ========== CREAR ARCHIVO: backend/app/routes/mic_guardados.py ==========
"""
Rutas para gestionar MICs guardados en base de datos
Complementa las rutas de mic.py para la funcionalidad de guardado
"""

from flask import Blueprint, request, jsonify, send_file
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from app.models import db, MIC, CRT
from app.utils.layout_mic import generar_micdta_pdf_con_datos
import tempfile
import os

mic_guardados_bp = Blueprint(
    'mic_guardados', __name__, url_prefix='/api/mic-guardados')


def to_dict_mic_completo(mic):
    """Serializar MIC completo con información del CRT"""
    def safe_str(val):
        return "" if val is None else str(val)

    base_dict = {
        "id": mic.id,
        "crt_id": mic.crt_id,
        "creado_en": mic.creado_en.strftime('%Y-%m-%d %H:%M:%S') if mic.creado_en else "",

        # Todos los campos del MIC
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
    }

    # Información del CRT si existe
    if mic.crt:
        base_dict.update({
            "crt_numero": mic.crt.numero_crt,
            "crt_fecha_emision": mic.crt.fecha_emision.strftime('%Y-%m-%d') if mic.crt.fecha_emision else "",
            "crt_estado": mic.crt.estado,
        })
    else:
        base_dict.update({
            "crt_numero": "",
            "crt_fecha_emision": "",
            "crt_estado": "",
        })

    return base_dict


@mic_guardados_bp.route('/', methods=['GET'])
def listar_mics_guardados():
    """Lista todos los MICs guardados con paginación"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        buscar = request.args.get('q', '', type=str).strip()

        # Query base con CRT joinedload
        query = MIC.query.options(joinedload(MIC.crt))

        # Filtro de búsqueda
        if buscar:
            like = f"%{buscar}%"
            query = query.filter(
                db.or_(
                    MIC.campo_23_numero_campo2_crt.ilike(like),
                    MIC.campo_1_transporte.ilike(like),
                    MIC.campo_38_datos_campo11_crt.ilike(like),
                    MIC.crt.has(CRT.numero_crt.ilike(like))
                )
            )

        # Ordenar por más recientes
        query = query.order_by(MIC.id.desc())

        # Paginar
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False)

        mics_data = []
        for mic in pagination.items:
            mic_dict = to_dict_mic_completo(mic)
            mic_dict.update({
                "acciones": {
                    "puede_editar": True,
                    "puede_eliminar": True,
                    "puede_generar_pdf": True,
                    "puede_duplicar": True
                },
                "urls": {
                    "detalle": f"/api/mic-guardados/{mic.id}",
                    "editar": f"/api/mic-guardados/{mic.id}",
                    "eliminar": f"/api/mic-guardados/{mic.id}",
                    "pdf": f"/api/mic-guardados/{mic.id}/pdf",
                    "duplicar": f"/api/mic-guardados/{mic.id}/duplicate"
                }
            })
            mics_data.append(mic_dict)

        return jsonify({
            "mics": mics_data,
            "pagination": {
                "page": pagination.page,
                "pages": pagination.pages,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "has_prev": pagination.has_prev,
                "has_next": pagination.has_next,
                "prev_num": pagination.prev_num,
                "next_num": pagination.next_num
            },
            "filtros": {
                "buscar": buscar
            }
        })

    except Exception as e:
        import traceback
        print(f"❌ Error listando MICs guardados: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@mic_guardados_bp.route('/<int:mic_id>/pdf', methods=['GET'])
def generar_pdf_mic_guardado(mic_id):
    """Genera PDF de un MIC guardado"""
    try:
        mic = MIC.query.get_or_404(mic_id)

        # Convertir MIC a formato compatible con el generador de PDF
        mic_data = to_dict_mic_completo(mic)

        # Asegurar que campo_9 = campo_1 (blindaje)
        mic_data["campo_9_datos_transporte"] = mic_data["campo_1_transporte"]

        # Generar archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            filename = tmp_file.name

        generar_micdta_pdf_con_datos(mic_data, filename)

        print(f"✅ PDF generado para MIC guardado {mic_id}")

        # Nombre del archivo para descarga
        download_name = f"MIC_{mic.campo_23_numero_campo2_crt or mic.id}_{datetime.now().strftime('%Y%m%d')}.pdf"

        response = send_file(
            filename,
            as_attachment=True,
            download_name=download_name,
            mimetype="application/pdf"
        )
        response.call_on_close(lambda: os.unlink(filename))

        return response

    except Exception as e:
        import traceback
        print(f"❌ Error generando PDF MIC {mic_id}: {e}")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@mic_guardados_bp.route('/crear-desde-crt/<int:crt_id>', methods=['POST'])
def crear_mic_desde_crt_guardado(crt_id):
    """Crea un MIC guardado usando datos del CRT + datos adicionales del usuario"""
    try:
        user_data = request.json or {}

        print(f"🔧 CREANDO MIC DESDE CRT {crt_id} CON DATOS ADICIONALES...")

        # Importar la función del módulo mic
        from app.routes.mic import obtener_datos_crt_para_mic

        # Obtener datos auto-completados del CRT
        response_data = obtener_datos_crt_para_mic(crt_id)
        if hasattr(response_data, 'status_code') and response_data.status_code != 200:
            return response_data

        # Extraer datos del response
        if hasattr(response_data, 'get_json'):
            datos_crt = response_data.get_json()["datos"]
        else:
            # Si es una respuesta directa de la función
            datos_crt = response_data.json["datos"]

        # Combinar datos del CRT con datos del usuario
        mic_data_final = {**datos_crt, **user_data}

        # Crear MIC en base de datos
        mic = MIC(
            crt_id=crt_id,
            campo_1_transporte=mic_data_final.get('campo_1_transporte', ''),
            campo_2_numero=mic_data_final.get('campo_2_numero', ''),
            campo_3_transporte=mic_data_final.get('campo_3_transporte', ''),
            campo_4_estado=mic_data_final.get('campo_4_estado', 'PROVISORIO'),
            campo_5_hoja=mic_data_final.get('campo_5_hoja', '1 / 1'),
            campo_6_fecha=datetime.strptime(mic_data_final.get('campo_6_fecha'), '%Y-%m-%d').date(
            ) if mic_data_final.get('campo_6_fecha') else datetime.now().date(),
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
            campo_38_datos_campo11_crt=mic_data_final.get('campo_38', ''),
            campo_40_tramo=mic_data_final.get('campo_40_tramo', ''),
            creado_en=datetime.now()
        )

        db.session.add(mic)
        db.session.commit()

        print(f"✅ MIC CREADO EXITOSAMENTE CON ID: {mic.id}")

        return jsonify({
            "success": True,
            "message": "MIC creado exitosamente desde CRT",
            "id": mic.id,
            "crt_id": crt_id,
            "numero_crt": datos_crt.get("numero_crt"),
            "campos_autocompletados": datos_crt.get("campos_autocompletados", []),
            "urls": {
                "pdf": f"/api/mic-guardados/{mic.id}/pdf",
                "detalle": f"/api/mic-guardados/{mic.id}"
            }
        }), 201

    except Exception as e:
        import traceback
        db.session.rollback()
        print(f"❌ ERROR CREANDO MIC DESDE CRT {crt_id}:")
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500
