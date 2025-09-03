# ========== backend/app/routes/mic_guardados.py ==========
"""
Rutas para gestionar MICs guardados en base de datos.
"""

from datetime import datetime, date, time, timedelta
from decimal import Decimal, InvalidOperation
import tempfile
import os

from flask import Blueprint, request, jsonify, send_file
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload

from app.models import db, MIC, CRT
from app.utils.layout_mic import generar_micdta_pdf_con_datos

mic_guardados_bp = Blueprint(
    "mic_guardados", __name__, url_prefix="/api/mic-guardados"
)

# ========= Helpers =========


def _safe_str(val):
    return "" if val is None else str(val)


def to_dict_mic_completo(mic: MIC):
    """
    Serializa un MIC completo + algunos datos del CRT si existe.
    Sirve para la vista de detalles, para la tabla y para generar el PDF.
    """
    base_dict = {
        "id": mic.id,
        "crt_id": mic.crt_id,
        "creado_en": mic.creado_en.strftime("%Y-%m-%d %H:%M:%S") if mic.creado_en else "",

        # Campos del MIC
        "campo_1_transporte": _safe_str(mic.campo_1_transporte),
        "campo_2_numero": _safe_str(mic.campo_2_numero),
        "campo_3_transporte": _safe_str(mic.campo_3_transporte),
        "campo_4_estado": _safe_str(mic.campo_4_estado),
        "campo_5_hoja": _safe_str(mic.campo_5_hoja),
        "campo_6_fecha": mic.campo_6_fecha.strftime("%Y-%m-%d") if mic.campo_6_fecha else "",
        "campo_7_pto_seguro": _safe_str(mic.campo_7_pto_seguro),
        "campo_8_destino": _safe_str(mic.campo_8_destino),
        "campo_9_datos_transporte": _safe_str(mic.campo_9_datos_transporte),
        "campo_10_numero": _safe_str(mic.campo_10_numero),
        "campo_11_placa": _safe_str(mic.campo_11_placa),
        "campo_12_modelo_chasis": _safe_str(mic.campo_12_modelo_chasis),
        "campo_13_siempre_45": _safe_str(mic.campo_13_siempre_45),
        "campo_14_anio": _safe_str(mic.campo_14_anio),
        "campo_15_placa_semi": _safe_str(mic.campo_15_placa_semi),
        "campo_16_asteriscos_1": _safe_str(mic.campo_16_asteriscos_1),
        "campo_17_asteriscos_2": _safe_str(mic.campo_17_asteriscos_2),
        "campo_18_asteriscos_3": _safe_str(mic.campo_18_asteriscos_3),
        "campo_19_asteriscos_4": _safe_str(mic.campo_19_asteriscos_4),
        "campo_20_asteriscos_5": _safe_str(mic.campo_20_asteriscos_5),
        "campo_21_asteriscos_6": _safe_str(mic.campo_21_asteriscos_6),
        "campo_22_asteriscos_7": _safe_str(mic.campo_22_asteriscos_7),
        "campo_23_numero_campo2_crt": _safe_str(mic.campo_23_numero_campo2_crt),
        "campo_24_aduana": _safe_str(mic.campo_24_aduana),
        "campo_25_moneda": _safe_str(mic.campo_25_moneda),
        "campo_26_pais": _safe_str(mic.campo_26_pais),
        "campo_27_valor_campo16": _safe_str(mic.campo_27_valor_campo16),
        "campo_28_total": _safe_str(mic.campo_28_total),
        "campo_29_seguro": _safe_str(mic.campo_29_seguro),
        "campo_30_tipo_bultos": _safe_str(mic.campo_30_tipo_bultos),
        "campo_31_cantidad": _safe_str(mic.campo_31_cantidad),
        "campo_32_peso_bruto": _safe_str(mic.campo_32_peso_bruto),
        "campo_33_datos_campo1_crt": _safe_str(mic.campo_33_datos_campo1_crt),
        "campo_34_datos_campo4_crt": _safe_str(mic.campo_34_datos_campo4_crt),
        "campo_35_datos_campo6_crt": _safe_str(mic.campo_35_datos_campo6_crt),
        "campo_36_factura_despacho": _safe_str(mic.campo_36_factura_despacho),
        "campo_37_valor_manual": _safe_str(mic.campo_37_valor_manual),
        "campo_38_datos_campo11_crt": _safe_str(mic.campo_38_datos_campo11_crt),
        "campo_40_tramo": _safe_str(mic.campo_40_tramo),
    }

    if mic.crt:
        base_dict.update({
            "crt_numero": mic.crt.numero_crt,
            "crt_fecha_emision": mic.crt.fecha_emision.strftime("%Y-%m-%d") if mic.crt.fecha_emision else "",
            "crt_estado": mic.crt.estado,
        })
    else:
        base_dict.update({
            "crt_numero": "",
            "crt_fecha_emision": "",
            "crt_estado": "",
        })

    return base_dict


def _parse_num_es(val):
    """
    Acepta: "2.500,00", "2500,00", "2500.00", 2500, None -> Decimal o None
    """
    if val is None or val == "":
        return None
    if isinstance(val, (int, float, Decimal)):
        return Decimal(str(val))
    s = str(val).strip().replace(".", "").replace(",", ".")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def _build_mic_model_from_dict(mic_data, crt_id=None):
    """
    Crea una instancia MIC (sin commit) a partir de un dict.
    Respeta los tipos declarados en models.py
    """
    f6 = mic_data.get("campo_6_fecha") or ""
    try:
        f6_date = datetime.strptime(
            f6, "%Y-%m-%d").date() if f6 else datetime.now().date()
    except Exception:
        f6_date = datetime.now().date()

    mic = MIC(
        crt_id=crt_id,
        campo_1_transporte=(mic_data.get(
            "campo_1_transporte", "") or "")[:150],
        campo_2_numero=(mic_data.get("campo_2_numero", "") or "")[:30],
        campo_3_transporte=(mic_data.get(
            "campo_3_transporte", "") or "")[:150],
        campo_4_estado=(mic_data.get(
            "campo_4_estado", "PROVISORIO") or "")[:30],
        campo_5_hoja=(mic_data.get("campo_5_hoja", "1 / 1") or "")[:20],
        campo_6_fecha=f6_date,
        campo_7_pto_seguro=(mic_data.get(
            "campo_7_pto_seguro", "") or "")[:100],
        campo_8_destino=(mic_data.get("campo_8_destino", "") or "")[:100],
        campo_9_datos_transporte=(mic_data.get(
            "campo_9_datos_transporte") or mic_data.get("campo_1_transporte", ""))[:200],
        campo_10_numero=(mic_data.get("campo_10_numero", "") or "")[:30],
        campo_11_placa=(mic_data.get("campo_11_placa", "") or "")[:20],
        campo_12_modelo_chasis=(mic_data.get(
            "campo_12_modelo_chasis", "") or "")[:80],
        campo_13_siempre_45=(
            (mic_data.get("campo_13_siempre_45", "45 TON") or ""))[:10],
        campo_14_anio=(mic_data.get("campo_14_anio", "") or "")[:10],
        campo_15_placa_semi=(mic_data.get(
            "campo_15_placa_semi", "") or "")[:20],
        campo_16_asteriscos_1=(mic_data.get(
            "campo_16_asteriscos_1", "******") or "")[:20],
        campo_17_asteriscos_2=(mic_data.get(
            "campo_17_asteriscos_2", "******") or "")[:20],
        campo_18_asteriscos_3=(mic_data.get(
            "campo_18_asteriscos_3", "******") or "")[:20],
        campo_19_asteriscos_4=(mic_data.get(
            "campo_19_asteriscos_4", "******") or "")[:20],
        campo_20_asteriscos_5=(mic_data.get(
            "campo_20_asteriscos_5", "******") or "")[:20],
        campo_21_asteriscos_6=(mic_data.get(
            "campo_21_asteriscos_6", "******") or "")[:20],
        campo_22_asteriscos_7=(mic_data.get(
            "campo_22_asteriscos_7", "******") or "")[:20],
        campo_23_numero_campo2_crt=(mic_data.get(
            "campo_23_numero_campo2_crt", "") or "")[:30],
        campo_24_aduana=(mic_data.get("campo_24_aduana", "") or "")[:100],
        campo_25_moneda=(mic_data.get("campo_25_moneda", "") or "")[:30],
        campo_26_pais=(mic_data.get("campo_26_pais", "") or "")[:30],
        campo_27_valor_campo16=_parse_num_es(
            mic_data.get("campo_27_valor_campo16")),
        campo_28_total=_parse_num_es(mic_data.get("campo_28_total")),
        campo_29_seguro=_parse_num_es(mic_data.get("campo_29_seguro")),
        campo_30_tipo_bultos=(mic_data.get(
            "campo_30_tipo_bultos", "") or "")[:30],
        campo_31_cantidad=_parse_num_es(mic_data.get("campo_31_cantidad")),
        campo_32_peso_bruto=_parse_num_es(mic_data.get("campo_32_peso_bruto")),
        campo_33_datos_campo1_crt=(mic_data.get(
            "campo_33_datos_campo1_crt", "") or "")[:200],
        campo_34_datos_campo4_crt=(mic_data.get(
            "campo_34_datos_campo4_crt", "") or "")[:200],
        campo_35_datos_campo6_crt=(mic_data.get(
            "campo_35_datos_campo6_crt", "") or "")[:200],
        campo_36_factura_despacho=(mic_data.get(
            "campo_36_factura_despacho", "") or "")[:100],
        campo_37_valor_manual=(mic_data.get(
            "campo_37_valor_manual", "") or "")[:100],
        campo_38_datos_campo11_crt=(mic_data.get(
            "campo_38_datos_campo11_crt", "") or ""),
        campo_40_tramo=(mic_data.get("campo_40_tramo", "") or "")[:200],
        creado_en=datetime.now()
    )
    return mic


# ✅ CONFIGURACIÓN PROFESIONAL DE ESTADOS
ESTADOS_MIC_CONFIG = {
    'PROVISORIO': {
        'label': 'Provisorio',
        'can_transition_to': ['DEFINITIVO', 'ANULADO'],
        'requires_confirmation': False,
        'allow_direct_edit': True,
        'is_final': False
    },
    'DEFINITIVO': {
        'label': 'Definitivo',
        'can_transition_to': ['CONFIRMADO', 'EN_PROCESO', 'ANULADO'],
        'requires_confirmation': True,
        'allow_direct_edit': True,
        'is_final': False
    },
    'CONFIRMADO': {
        'label': 'Confirmado',
        'can_transition_to': ['EN_PROCESO', 'FINALIZADO', 'ANULADO'],
        'requires_confirmation': True,
        'allow_direct_edit': False,
        'is_final': False
    },
    'EN_PROCESO': {
        'label': 'En Proceso',
        'can_transition_to': ['FINALIZADO', 'ANULADO'],
        'requires_confirmation': True,
        'allow_direct_edit': False,
        'is_final': False
    },
    'FINALIZADO': {
        'label': 'Finalizado',
        'can_transition_to': [],
        'requires_confirmation': False,
        'allow_direct_edit': False,
        'is_final': True
    },
    'ANULADO': {
        'label': 'Anulado',
        'can_transition_to': [],
        'requires_confirmation': False,
        'allow_direct_edit': False,
        'is_final': True
    }
}


def validar_transicion_estado(estado_actual, estado_nuevo):
    """
    Validar que la transición de estado sea válida según las reglas de negocio
    """
    if not estado_actual or not estado_nuevo:
        return False, "Estados no pueden estar vacíos"

    if estado_actual == estado_nuevo:
        return True, "Sin cambios"

    config_actual = ESTADOS_MIC_CONFIG.get(estado_actual)
    if not config_actual:
        return False, f"Estado actual '{estado_actual}' no es válido"

    if estado_nuevo not in ESTADOS_MIC_CONFIG:
        return False, f"Estado nuevo '{estado_nuevo}' no es válido"

    if estado_nuevo not in config_actual['can_transition_to']:
        return False, f"No se puede cambiar de '{estado_actual}' a '{estado_nuevo}'"

    return True, "Transición válida"


def puede_editar_mic(estado_actual):
    """
    Verificar si un MIC en cierto estado puede ser editado
    """
    config = ESTADOS_MIC_CONFIG.get(estado_actual, {})
    return config.get('allow_direct_edit', False)


def registrar_cambio_estado(mic_id, estado_anterior, estado_nuevo, usuario=None, motivo=None):
    """
    Registrar el cambio de estado para auditoría (opcional - implementar tabla de auditoría)
    """
    try:
        print(
            f"📊 AUDITORIA: MIC {mic_id} cambió de {estado_anterior} a {estado_nuevo}")
        if usuario:
            print(f"👤 Usuario: {usuario}")
        if motivo:
            print(f"📝 Motivo: {motivo}")
    except Exception as e:
        print(f"⚠️ Error registrando auditoría: {e}")


# ========= Endpoints =========

@mic_guardados_bp.route("/", methods=["GET"])
def listar_mics_guardados():
    """
    Lista MICs guardados con paginación + filtros.
    Devuelve cada item con TODOS los campos 'campo_*' (to_dict_mic_completo).
    """
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        estado = (request.args.get("estado", "") or "").strip().upper()
        numero_carta = (request.args.get("numero_carta", "") or "").strip()
        transportadora = (request.args.get("transportadora", "") or "").strip()
        placa = (request.args.get("placa", "") or "").strip()
        destino = (request.args.get("destino", "") or "").strip()
        fecha_desde = (request.args.get("fecha_desde", "") or "").strip()
        fecha_hasta = (request.args.get("fecha_hasta", "") or "").strip()

        query = MIC.query.options(joinedload(MIC.crt))

        if estado:
            query = query.filter(MIC.campo_4_estado == estado)

        if numero_carta:
            like = f"%{numero_carta}%"
            query = query.filter(MIC.campo_23_numero_campo2_crt.ilike(like))

        if transportadora:
            query = query.filter(
                MIC.campo_1_transporte.ilike(f"%{transportadora}%"))

        if placa:
            like_placa = f"%{placa}%"
            query = query.filter(
                or_(MIC.campo_11_placa.ilike(like_placa),
                    MIC.campo_15_placa_semi.ilike(like_placa))
            )

        if destino:
            query = query.filter(MIC.campo_8_destino.ilike(f"%{destino}%"))

        # Fechas en campo_6_fecha (Date)
        if fecha_desde:
            try:
                fd = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
                query = query.filter(MIC.campo_6_fecha >= fd)
            except Exception:
                pass

        if fecha_hasta:
            try:
                fh = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
                query = query.filter(MIC.campo_6_fecha <= fh)
            except Exception:
                pass

        query = query.order_by(MIC.id.desc())
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False)

        items = [to_dict_mic_completo(m) for m in pagination.items]

        return jsonify({
            "mics": items,
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
                "estado": estado,
                "numero_carta": numero_carta,
                "transportadora": transportadora,
                "placa": placa,
                "destino": destino,
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta
            }
        })

    except Exception as e:
        import traceback
        print(f"❌ Error listando MICs guardados: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@mic_guardados_bp.route("/<int:mic_id>", methods=["GET"])
def obtener_mic_guardado(mic_id):
    """Detalle de un MIC guardado (para modal en el front)."""
    mic = MIC.query.options(joinedload(MIC.crt)).get_or_404(mic_id)
    return jsonify(to_dict_mic_completo(mic))


@mic_guardados_bp.route("/<int:mic_id>/pdf", methods=["GET"])
def generar_pdf_mic_guardado(mic_id):
    """Genera PDF de un MIC guardado."""
    try:
        mic = MIC.query.get_or_404(mic_id)
        mic_data = to_dict_mic_completo(mic)

        # Blindaje: campo 9 = campo 1
        mic_data["campo_9_datos_transporte"] = mic_data["campo_1_transporte"]

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            filename = tmp_file.name

        generar_micdta_pdf_con_datos(mic_data, filename)

        download_name = f"MIC_{mic.campo_23_numero_campo2_crt or mic.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        response = send_file(filename, as_attachment=True,
                             download_name=download_name, mimetype="application/pdf")
        response.call_on_close(lambda: os.unlink(filename))
        return response

    except Exception as e:
        import traceback
        print(f"❌ Error generando PDF MIC {mic_id}: {e}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500


@mic_guardados_bp.route("/<int:mic_id>", methods=["DELETE"])
def anular_mic_guardado(mic_id):
    """Soft delete: cambia el estado del MIC a ANULADO."""
    try:
        mic = MIC.query.get_or_404(mic_id)
        mic.campo_4_estado = "ANULADO"
        db.session.commit()
        return jsonify({"message": "MIC anulado exitosamente"})
    except Exception as e:
        import traceback
        db.session.rollback()
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@mic_guardados_bp.route("/stats", methods=["GET"])
def stats_mics_guardados():
    """Estadísticas para el panel (total, hoy, semana, por estado)."""
    try:
        hoy = date.today()
        semana_ini = hoy - timedelta(days=hoy.weekday())

        total_mics = db.session.query(func.count(MIC.id)).scalar() or 0

        mics_hoy = MIC.query.filter(
            MIC.creado_en >= datetime.combine(hoy, time.min)
        ).count()

        mics_semana = MIC.query.filter(
            MIC.creado_en >= datetime.combine(semana_ini, time.min)
        ).count()

        por_estado_raw = db.session.query(
            MIC.campo_4_estado, func.count(MIC.id)
        ).group_by(MIC.campo_4_estado).all()

        por_estado = [{"estado": (e or "SIN_ESTADO"), "cantidad": c}
                      for e, c in por_estado_raw]

        return jsonify({
            "total_mics": total_mics,
            "mics_hoy": mics_hoy,
            "mics_semana": mics_semana,
            "por_estado": por_estado
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@mic_guardados_bp.route("/crear-desde-crt/<int:crt_id>", methods=["POST"])
def crear_mic_desde_crt_guardado(crt_id):
    """
    Crea y guarda un MIC usando datos del CRT + overrides del usuario.
    Usa el formateo/auto-completado del endpoint de mic.get_crt_data.
    """
    try:
        user_data = request.json or {}
        print(f"🔧 CREANDO MIC DESDE CRT {crt_id} CON DATOS ADICIONALES...")

        # Import diferido para evitar ciclos
        from app.routes.mic import obtener_datos_crt_para_mic

        response_data = obtener_datos_crt_para_mic(crt_id)
        if hasattr(response_data, "status_code") and response_data.status_code != 200:
            return response_data

        datos_crt = response_data.get_json()["datos"] if hasattr(
            response_data, "get_json") else response_data.json["datos"]

        # Combinar CRT + usuario (sin pisar gastos si el usuario no envía)
        mic_data_final = dict(datos_crt)
        if not user_data.get("campo_28_total"):
            user_data.pop("campo_28_total", None)
        if not user_data.get("campo_29_seguro"):
            user_data.pop("campo_29_seguro", None)

        # Mapear "campo_38" a "campo_38_datos_campo11_crt" si viene del front
        if "campo_38" in user_data:
            user_data["campo_38_datos_campo11_crt"] = user_data.pop("campo_38")

        mic_data_final.update(user_data)

        mic = _build_mic_model_from_dict(mic_data_final, crt_id=crt_id)
        db.session.add(mic)
        db.session.commit()

        print(f"✅ MIC CREADO EXITOSAMENTE CON ID: {mic.id}")

        return jsonify({
            "success": True,
            "message": "MIC creado exitosamente desde CRT",
            "id": mic.id,
            "crt_id": crt_id,
            "numero_crt": datos_crt.get("numero_crt"),
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
        return jsonify({"success": False, "error": str(e), "trace": traceback.format_exc()}), 500


# ========== PUT con VALIDACIONES PROFESIONALES ==========
@mic_guardados_bp.route('/<int:mic_id>', methods=['PUT'])
def actualizar_mic_guardado(mic_id):
    """
    Actualizar un MIC existente en la base de datos CON VALIDACIONES PROFESIONALES
    """
    try:
        print(f"🔄 ACTUALIZANDO MIC {mic_id}...")

        # Obtener datos del request
        data = request.json or {}
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # Buscar el MIC existente
        mic_existente = MIC.query.get(mic_id)
        if not mic_existente:
            return jsonify({"error": "MIC no encontrado"}), 404

        estado_actual = mic_existente.campo_4_estado or 'PROVISORIO'

        # ✅ VALIDAR CAMBIO DE ESTADO SI ESTÁ PRESENTE
        if 'campo_4_estado' in data:
            estado_nuevo = (data['campo_4_estado'] or '').upper()

            # Validar transición
            es_valida, mensaje = validar_transicion_estado(
                estado_actual, estado_nuevo)
            if not es_valida:
                return jsonify({
                    "error": f"Transición de estado no válida: {mensaje}",
                    "estado_actual": estado_actual,
                    "estado_solicitado": estado_nuevo,
                    "transiciones_permitidas": ESTADOS_MIC_CONFIG.get(estado_actual, {}).get('can_transition_to', [])
                }), 400

            # Registrar cambio para auditoría
            if estado_actual != estado_nuevo:
                usuario_actualizacion = data.get(
                    'usuario_actualizacion', 'Sistema')
                motivo = data.get('cambio_estado_motivo',
                                  f'Cambio de {estado_actual} a {estado_nuevo}')
                registrar_cambio_estado(
                    mic_id, estado_actual, estado_nuevo, usuario_actualizacion, motivo)

        # ✅ VALIDAR SI PUEDE EDITAR OTROS CAMPOS
        campos_editables = [
            'campo_1_transporte', 'campo_2_numero', 'campo_3_transporte',
            'campo_5_hoja', 'campo_6_fecha', 'campo_7_pto_seguro',
            'campo_8_destino', 'campo_9_datos_transporte', 'campo_10_numero',
            'campo_11_placa', 'campo_12_modelo_chasis', 'campo_13_siempre_45',
            'campo_14_anio', 'campo_15_placa_semi', 'campo_24_aduana',
            'campo_25_moneda', 'campo_26_pais', 'campo_27_valor_campo16',
            'campo_28_total', 'campo_29_seguro', 'campo_30_tipo_bultos',
            'campo_31_cantidad', 'campo_32_peso_bruto', 'campo_33_datos_campo1_crt',
            'campo_34_datos_campo4_crt', 'campo_35_datos_campo6_crt',
            'campo_36_factura_despacho', 'campo_37_valor_manual',
            'campo_38_datos_campo11_crt', 'campo_40_tramo'
        ]

        campos_a_editar = [
            campo for campo in campos_editables if campo in data]

        if campos_a_editar and not puede_editar_mic(estado_actual):
            return jsonify({
                "error": f"No se pueden editar campos en estado '{estado_actual}'. Solo se permite cambio de estado.",
                "estado_actual": estado_actual,
                "campos_intentados": campos_a_editar,
                "accion_permitida": "Solo cambio de estado"
            }), 403

        print(f"📊 Datos recibidos para actualización: {list(data.keys())}")

        # Mapear "campo_38" a "campo_38_datos_campo11_crt" si viene del front
        if "campo_38" in data:
            data["campo_38_datos_campo11_crt"] = data.pop("campo_38")

        # Actualizar campos usando la lógica existente
        campos_actualizables = [
            'campo_1_transporte', 'campo_2_numero', 'campo_3_transporte',
            'campo_4_estado', 'campo_5_hoja', 'campo_6_fecha',
            'campo_7_pto_seguro', 'campo_8_destino', 'campo_9_datos_transporte',
            'campo_10_numero', 'campo_11_placa', 'campo_12_modelo_chasis',
            'campo_13_siempre_45', 'campo_14_anio', 'campo_15_placa_semi',
            'campo_24_aduana', 'campo_25_moneda', 'campo_26_pais',
            'campo_27_valor_campo16', 'campo_28_total', 'campo_29_seguro',
            'campo_30_tipo_bultos', 'campo_31_cantidad', 'campo_32_peso_bruto',
            'campo_33_datos_campo1_crt', 'campo_34_datos_campo4_crt', 'campo_35_datos_campo6_crt',
            'campo_36_factura_despacho', 'campo_37_valor_manual', 'campo_38_datos_campo11_crt',
            'campo_40_tramo'
        ]

        # Actualizar cada campo usando la lógica de creación
        for campo in campos_actualizables:
            if campo in data:
                if campo in ['campo_27_valor_campo16', 'campo_28_total', 'campo_29_seguro',
                             'campo_31_cantidad', 'campo_32_peso_bruto']:
                    setattr(mic_existente, campo, _parse_num_es(data[campo]))
                elif campo == 'campo_6_fecha':
                    f6 = data[campo] or ""
                    try:
                        f6_date = datetime.strptime(
                            f6, "%Y-%m-%d").date() if f6 else datetime.now().date()
                    except Exception:
                        f6_date = datetime.now().date()
                    setattr(mic_existente, campo, f6_date)
                else:
                    valor = data[campo] or ""
                    if campo in ['campo_1_transporte', 'campo_3_transporte']:
                        valor = valor[:150]
                    elif campo in ['campo_2_numero', 'campo_10_numero', 'campo_23_numero_campo2_crt']:
                        valor = valor[:30]
                    elif campo == 'campo_4_estado':
                        valor = valor[:30]
                    elif campo == 'campo_5_hoja':
                        valor = valor[:20]
                    elif campo in ['campo_7_pto_seguro', 'campo_8_destino', 'campo_24_aduana', 'campo_36_factura_despacho']:
                        valor = valor[:100]
                    elif campo in ['campo_11_placa', 'campo_15_placa_semi']:
                        valor = valor[:20]
                    elif campo == 'campo_12_modelo_chasis':
                        valor = valor[:80]
                    elif campo == 'campo_13_siempre_45':
                        valor = valor[:10]
                    elif campo == 'campo_14_anio':
                        valor = valor[:10]
                    elif campo in ['campo_25_moneda', 'campo_26_pais', 'campo_30_tipo_bultos']:
                        valor = valor[:30]
                    elif campo == 'campo_37_valor_manual':
                        valor = valor[:100]
                    elif campo in ['campo_9_datos_transporte', 'campo_33_datos_campo1_crt',
                                   'campo_34_datos_campo4_crt', 'campo_35_datos_campo6_crt',
                                   'campo_40_tramo']:
                        valor = valor[:200]

                    setattr(mic_existente, campo, valor)

        db.session.commit()

        print(f"✅ MIC {mic_id} actualizado exitosamente")

        return jsonify({
            "success": True,
            "message": "MIC actualizado exitosamente",
            "id": mic_existente.id,
            "numero_crt": mic_existente.campo_23_numero_campo2_crt,
            "estado_anterior": estado_actual,
            "estado_actual": mic_existente.campo_4_estado,
            "transiciones_disponibles": ESTADOS_MIC_CONFIG.get(mic_existente.campo_4_estado, {}).get('can_transition_to', [])
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"❌ ERROR ACTUALIZANDO MIC {mic_id}:")
        print(traceback.format_exc())
        return jsonify({"error": f"Error actualizando MIC: {str(e)}"}), 500


@mic_guardados_bp.route('/<int:mic_id>/duplicate', methods=['POST'])
def duplicar_mic_guardado(mic_id):
    """
    Crear una copia de un MIC existente
    """
    try:
        print(f"📋 DUPLICANDO MIC {mic_id}...")

        # Buscar el MIC original
        mic_original = MIC.query.get(mic_id)
        if not mic_original:
            return jsonify({"error": "MIC original no encontrado"}), 404

        # Crear nuevo MIC copiando datos del original usando tu función
        mic_data_original = to_dict_mic_completo(mic_original)

        # Modificar algunos campos para la copia
        mic_data_original[
            "campo_23_numero_campo2_crt"] = f"{mic_data_original.get('campo_23_numero_campo2_crt', '')}_COPIA"
        mic_data_original["campo_4_estado"] = "PROVISORIO"
        mic_data_original["campo_6_fecha"] = datetime.now().strftime(
            '%Y-%m-%d')

        # Crear nuevo MIC
        nuevo_mic = _build_mic_model_from_dict(
            mic_data_original, crt_id=mic_original.crt_id)

        # Guardar el nuevo MIC
        db.session.add(nuevo_mic)
        db.session.commit()

        print(f"✅ MIC duplicado exitosamente: {mic_id} -> {nuevo_mic.id}")

        return jsonify({
            "success": True,
            "message": "MIC duplicado exitosamente",
            "id": nuevo_mic.id,
            "id_original": mic_id,
            "numero_crt": nuevo_mic.campo_23_numero_campo2_crt,
            "estado": nuevo_mic.campo_4_estado
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"❌ ERROR DUPLICANDO MIC {mic_id}:")
        print(traceback.format_exc())
        return jsonify({"error": f"Error duplicando MIC: {str(e)}"}), 500


# ========== NUEVO ENDPOINT: CONFIG ESTADOS ==========
@mic_guardados_bp.route('/estados-config', methods=['GET'])
def obtener_configuracion_estados():
    """
    Obtener la configuración de estados y transiciones válidas
    """
    try:
        return jsonify({
            "estados": ESTADOS_MIC_CONFIG,
            "message": "Configuración de estados obtenida exitosamente"
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error obteniendo configuración: {str(e)}"}), 500
