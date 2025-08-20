package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/mux"
	_ "github.com/lib/pq"
)

// ✅ Estructura CRT COMPLETA con toda la información necesaria para MIC
type CRT struct {
	ID        int    `json:"id"`
	NumeroCRT string `json:"numero_crt"`
	Estado    string `json:"estado"`

	// ✅ TRANSPORTADORA COMPLETA
	TransportadoraNombre        string `json:"transportadora_nombre"`
	TransportadoraDireccion     string `json:"transportadora_direccion"`
	TransportadoraDocumento     string `json:"transportadora_documento"`
	TransportadoraTipoDocumento string `json:"transportadora_tipo_documento"`
	TransportadoraTelefono      string `json:"transportadora_telefono"`
	TransportadoraCiudad        string `json:"transportadora_ciudad"`
	TransportadoraPais          string `json:"transportadora_pais"`

	// ✅ REMITENTE COMPLETO
	RemitenteNombre        string `json:"remitente_nombre"`
	RemitenteDireccion     string `json:"remitente_direccion"`
	RemitenteDocumento     string `json:"remitente_documento"`
	RemitenteTipoDocumento string `json:"remitente_tipo_documento"`
	RemitenteCiudad        string `json:"remitente_ciudad"`
	RemitentePais          string `json:"remitente_pais"`

	// ✅ DESTINATARIO COMPLETO
	DestinatarioNombre        string `json:"destinatario_nombre"`
	DestinatarioDireccion     string `json:"destinatario_direccion"`
	DestinatarioDocumento     string `json:"destinatario_documento"`
	DestinatarioTipoDocumento string `json:"destinatario_tipo_documento"`
	DestinatarioCiudad        string `json:"destinatario_ciudad"`
	DestinatarioPais          string `json:"destinatario_pais"`

	// ✅ CONSIGNATARIO COMPLETO
	ConsignatarioNombre        string `json:"consignatario_nombre"`
	ConsignatarioDireccion     string `json:"consignatario_direccion"`
	ConsignatarioDocumento     string `json:"consignatario_documento"`
	ConsignatarioTipoDocumento string `json:"consignatario_tipo_documento"`
	ConsignatarioCiudad        string `json:"consignatario_ciudad"`
	ConsignatarioPais          string `json:"consignatario_pais"`

	// ✅ OTROS DATOS DEL CRT
	LugarEntrega          string  `json:"lugar_entrega"`
	FacturaExportacion    string  `json:"factura_exportacion"`
	NroDespacho           string  `json:"nro_despacho"`
	DetallesMercaderia    string  `json:"detalles_mercaderia"`
	DeclaracionMercaderia string  `json:"declaracion_mercaderia"`
	PesoBruto             float64 `json:"peso_bruto"`
	MonedaNombre          string  `json:"moneda_nombre"`
	FechaEmision          string  `json:"fecha_emision"`
}

var db *sql.DB

func printBanner() {
	fmt.Println("\033[1;32m")
	fmt.Println("🚛 GO CRT API - DATOS COMPLETOS PARA MIC 🚀")
	fmt.Println("OIKOOOOO LPM!! 💪 (Ñandeko)")
	fmt.Println("\033[0m")
}

func main() {
	var err error
	connStr := "postgres://postgres:Mjjagkaz012.@localhost/logistica?sslmode=disable"
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal("❌ Error opening database:", err)
	}
	if err := db.Ping(); err != nil {
		log.Fatal("❌ Error connecting to PostgreSQL:", err)
	}
	log.Println("✅ Conectado a PostgreSQL correctamente.")

	printBanner()

	r := mux.NewRouter()

	// Middleware CORS
	r.Use(mux.CORSMethodMiddleware(r))
	r.Use(func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Access-Control-Allow-Origin", "*")
			w.Header().Set("Access-Control-Allow-Methods", "GET, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
			if r.Method == http.MethodOptions {
				w.WriteHeader(http.StatusNoContent)
				return
			}
			next.ServeHTTP(w, r)
		})
	})

	r.HandleFunc("/api/crts/simple", listarSimple).Methods("GET", "OPTIONS")
	r.HandleFunc("/api/crts/{id:[0-9]+}", obtenerCRTPorID).Methods("GET", "OPTIONS")
	r.HandleFunc("/api/crts/{numero}", obtenerCRTPorNumero).Methods("GET", "OPTIONS")

	log.Println("🚀 Servidor HTTP corriendo en :8080")
	log.Fatal(http.ListenAndServe(":8080", r))
}

// ✅ QUERY COMPLETA para obtener TODOS los datos necesarios para MIC
const queryCompleta = `
	SELECT
		c.id,
		c.numero_crt,
		c.estado,
		COALESCE(c.fecha_emision::text, '') as fecha_emision,
		COALESCE(c.lugar_entrega, '') as lugar_entrega,
		COALESCE(c.factura_exportacion, '') as factura_exportacion,
		COALESCE(c.nro_despacho, '') as nro_despacho,
		COALESCE(c.detalles_mercaderia, '') as detalles_mercaderia,
		COALESCE(c.declaracion_mercaderia::text, '') as declaracion_mercaderia,
		COALESCE(c.peso_bruto, 0) as peso_bruto,

		-- TRANSPORTADORA COMPLETA
		COALESCE(t.nombre, '') as transportadora_nombre,
		COALESCE(t.direccion, '') as transportadora_direccion,
		COALESCE(t.numero_documento, '') as transportadora_documento,
		COALESCE(t.tipo_documento, '') as transportadora_tipo_documento,
		COALESCE(t.telefono, '') as transportadora_telefono,
		COALESCE(tc.nombre, '') as transportadora_ciudad,
		COALESCE(tp.nombre, '') as transportadora_pais,

		-- REMITENTE COMPLETO
		COALESCE(rm.nombre, '') as remitente_nombre,
		COALESCE(rm.direccion, '') as remitente_direccion,
		COALESCE(rm.numero_documento, '') as remitente_documento,
		COALESCE(rm.tipo_documento, '') as remitente_tipo_documento,
		COALESCE(rmc.nombre, '') as remitente_ciudad,
		COALESCE(rmp.nombre, '') as remitente_pais,

		-- DESTINATARIO COMPLETO
		COALESCE(d.nombre, '') as destinatario_nombre,
		COALESCE(d.direccion, '') as destinatario_direccion,
		COALESCE(d.numero_documento, '') as destinatario_documento,
		COALESCE(d.tipo_documento, '') as destinatario_tipo_documento,
		COALESCE(dc.nombre, '') as destinatario_ciudad,
		COALESCE(dp.nombre, '') as destinatario_pais,

		-- CONSIGNATARIO COMPLETO
		COALESCE(cons.nombre, '') as consignatario_nombre,
		COALESCE(cons.direccion, '') as consignatario_direccion,
		COALESCE(cons.numero_documento, '') as consignatario_documento,
		COALESCE(cons.tipo_documento, '') as consignatario_tipo_documento,
		COALESCE(consc.nombre, '') as consignatario_ciudad,
		COALESCE(consp.nombre, '') as consignatario_pais,

		-- MONEDA
		COALESCE(m.nombre, '') as moneda_nombre

	FROM crts c
	-- TRANSPORTADORA con ciudad y país
	LEFT JOIN transportadoras t ON t.id = c.transportadora_id
	LEFT JOIN ciudades tc ON tc.id = t.ciudad_id
	LEFT JOIN paises tp ON tp.id = tc.pais_id

	-- REMITENTE con ciudad y país
	LEFT JOIN remitentes rm ON rm.id = c.remitente_id
	LEFT JOIN ciudades rmc ON rmc.id = rm.ciudad_id
	LEFT JOIN paises rmp ON rmp.id = rmc.pais_id

	-- DESTINATARIO con ciudad y país
	LEFT JOIN remitentes d ON d.id = c.destinatario_id
	LEFT JOIN ciudades dc ON dc.id = d.ciudad_id
	LEFT JOIN paises dp ON dp.id = dc.pais_id

	-- CONSIGNATARIO con ciudad y país
	LEFT JOIN remitentes cons ON cons.id = c.consignatario_id
	LEFT JOIN ciudades consc ON consc.id = cons.ciudad_id
	LEFT JOIN paises consp ON consp.id = consc.pais_id

	-- MONEDA
	LEFT JOIN monedas m ON m.id = c.moneda_id
`

// ✅ FUNCIÓN para escanear todos los campos
func scanCRTCompleto(rows *sql.Rows) (CRT, error) {
	var c CRT
	err := rows.Scan(
		&c.ID,
		&c.NumeroCRT,
		&c.Estado,
		&c.FechaEmision,
		&c.LugarEntrega,
		&c.FacturaExportacion,
		&c.NroDespacho,
		&c.DetallesMercaderia,
		&c.DeclaracionMercaderia,
		&c.PesoBruto,

		// Transportadora
		&c.TransportadoraNombre,
		&c.TransportadoraDireccion,
		&c.TransportadoraDocumento,
		&c.TransportadoraTipoDocumento,
		&c.TransportadoraTelefono,
		&c.TransportadoraCiudad,
		&c.TransportadoraPais,

		// Remitente
		&c.RemitenteNombre,
		&c.RemitenteDireccion,
		&c.RemitenteDocumento,
		&c.RemitenteTipoDocumento,
		&c.RemitenteCiudad,
		&c.RemitentePais,

		// Destinatario
		&c.DestinatarioNombre,
		&c.DestinatarioDireccion,
		&c.DestinatarioDocumento,
		&c.DestinatarioTipoDocumento,
		&c.DestinatarioCiudad,
		&c.DestinatarioPais,

		// Consignatario
		&c.ConsignatarioNombre,
		&c.ConsignatarioDireccion,
		&c.ConsignatarioDocumento,
		&c.ConsignatarioTipoDocumento,
		&c.ConsignatarioCiudad,
		&c.ConsignatarioPais,

		// Moneda
		&c.MonedaNombre,
	)
	return c, err
}

// ✅ FUNCIÓN para escanear QueryRow
func scanCRTCompletoRow(row *sql.Row) (CRT, error) {
	var c CRT
	err := row.Scan(
		&c.ID,
		&c.NumeroCRT,
		&c.Estado,
		&c.FechaEmision,
		&c.LugarEntrega,
		&c.FacturaExportacion,
		&c.NroDespacho,
		&c.DetallesMercaderia,
		&c.DeclaracionMercaderia,
		&c.PesoBruto,

		// Transportadora
		&c.TransportadoraNombre,
		&c.TransportadoraDireccion,
		&c.TransportadoraDocumento,
		&c.TransportadoraTipoDocumento,
		&c.TransportadoraTelefono,
		&c.TransportadoraCiudad,
		&c.TransportadoraPais,

		// Remitente
		&c.RemitenteNombre,
		&c.RemitenteDireccion,
		&c.RemitenteDocumento,
		&c.RemitenteTipoDocumento,
		&c.RemitenteCiudad,
		&c.RemitentePais,

		// Destinatario
		&c.DestinatarioNombre,
		&c.DestinatarioDireccion,
		&c.DestinatarioDocumento,
		&c.DestinatarioTipoDocumento,
		&c.DestinatarioCiudad,
		&c.DestinatarioPais,

		// Consignatario
		&c.ConsignatarioNombre,
		&c.ConsignatarioDireccion,
		&c.ConsignatarioDocumento,
		&c.ConsignatarioTipoDocumento,
		&c.ConsignatarioCiudad,
		&c.ConsignatarioPais,

		// Moneda
		&c.MonedaNombre,
	)
	return c, err
}

// ✅ ACTUALIZADO: GET /api/crts/simple con datos completos
func listarSimple(w http.ResponseWriter, r *http.Request) {
	log.Println("📋 GET /api/crts/simple - DATOS COMPLETOS PARA MIC")

	query := queryCompleta + " ORDER BY c.id DESC LIMIT 20"

	rows, err := db.Query(query)
	if err != nil {
		log.Println("❌ Error ejecutando query:", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var crts []CRT
	for rows.Next() {
		c, err := scanCRTCompleto(rows)
		if err != nil {
			log.Println("❌ Error en rows.Scan:", err)
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		crts = append(crts, c)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(crts)
	log.Printf("✅ Enviados %d CRTs con datos completos para MIC\n", len(crts))
}

// ✅ ACTUALIZADO: GET /api/crts/{id} con datos completos
func obtenerCRTPorID(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	log.Printf("🔍 GET /api/crts/%s (por ID) - DATOS COMPLETOS PARA MIC\n", id)

	query := queryCompleta + " WHERE c.id = $1"

	c, err := scanCRTCompletoRow(db.QueryRow(query, id))
	if err != nil {
		log.Printf("❌ Error buscando CRT por ID %s: %v\n", id, err)
		http.Error(w, "CRT no encontrado: "+err.Error(), http.StatusNotFound)
		return
	}

	// ✅ DEBUG: Mostrar datos completos obtenidos
	log.Printf("🏢 Transportadora completa:")
	log.Printf("   Nombre: %s", c.TransportadoraNombre)
	log.Printf("   Dirección: %s", c.TransportadoraDireccion)
	log.Printf("   Documento: %s %s", c.TransportadoraTipoDocumento, c.TransportadoraDocumento)
	log.Printf("   Ciudad-País: %s - %s", c.TransportadoraCiudad, c.TransportadoraPais)
	log.Printf("   Teléfono: %s", c.TransportadoraTelefono)

	log.Printf("📤 Remitente completo:")
	log.Printf("   Nombre: %s", c.RemitenteNombre)
	log.Printf("   Dirección: %s", c.RemitenteDireccion)
	log.Printf("   Documento: %s %s", c.RemitenteTipoDocumento, c.RemitenteDocumento)
	log.Printf("   Ciudad-País: %s - %s", c.RemitenteCiudad, c.RemitentePais)

	log.Printf("📥 Destinatario completo:")
	log.Printf("   Nombre: %s", c.DestinatarioNombre)
	log.Printf("   Dirección: %s", c.DestinatarioDireccion)
	log.Printf("   Documento: %s %s", c.DestinatarioTipoDocumento, c.DestinatarioDocumento)
	log.Printf("   Ciudad-País: %s - %s", c.DestinatarioCiudad, c.DestinatarioPais)

	if c.ConsignatarioNombre != "" {
		log.Printf("📦 Consignatario completo:")
		log.Printf("   Nombre: %s", c.ConsignatarioNombre)
		log.Printf("   Dirección: %s", c.ConsignatarioDireccion)
		log.Printf("   Documento: %s %s", c.ConsignatarioTipoDocumento, c.ConsignatarioDocumento)
		log.Printf("   Ciudad-País: %s - %s", c.ConsignatarioCiudad, c.ConsignatarioPais)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(c)
	log.Printf("✅ Enviado CRT por ID %s con datos completos para MIC\n", id)
}

// ✅ ACTUALIZADO: GET /api/crts/{numero} con datos completos
func obtenerCRTPorNumero(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	numero := vars["numero"]

	log.Printf("🔍 GET /api/crts/%s (por número) - DATOS COMPLETOS PARA MIC\n", numero)

	query := queryCompleta + " WHERE c.numero_crt = $1"

	c, err := scanCRTCompletoRow(db.QueryRow(query, numero))
	if err != nil {
		log.Printf("❌ Error buscando CRT por número %s: %v\n", numero, err)
		http.Error(w, "CRT no encontrado: "+err.Error(), http.StatusNotFound)
		return
	}

	// ✅ DEBUG: Mostrar datos obtenidos
	log.Printf("✅ CRT %s encontrado con datos completos para clonación MIC", numero)
	log.Printf("🏢 Transportadora: %s (%s %s)", c.TransportadoraNombre, c.TransportadoraTipoDocumento, c.TransportadoraDocumento)
	log.Printf("📤 Remitente: %s (%s %s)", c.RemitenteNombre, c.RemitenteTipoDocumento, c.RemitenteDocumento)
	log.Printf("📥 Destinatario: %s (%s %s)", c.DestinatarioNombre, c.DestinatarioTipoDocumento, c.DestinatarioDocumento)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(c)
	log.Printf("✅ Enviado CRT por número %s con datos completos para MIC\n", numero)
}
