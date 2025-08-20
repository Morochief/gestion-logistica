package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/signintech/gopdf"
)

const mmToPt = 2.8346
const a4HeightPt = 841.89

func mmToXY(xmm, ymm float64) (float64, float64) {
	xpt := xmm * mmToPt
	ypt := a4HeightPt - (ymm * mmToPt)
	return xpt, ypt
}

type CRT struct {
	NumeroCRT               string `json:"numero_crt"`
	FechaEmision            string `json:"fecha_emision"`
	Remitente               string `json:"remitente"`
	Transportadora          string `json:"transportadora"`
	Destinatario            string `json:"destinatario"`
	Consignatario           string `json:"consignatario"`
	NotificarA              string `json:"notificar_a"`
	LugarEmision            string `json:"lugar_emision"`
	LugarPaisFechaTrans     string `json:"lugar_pais_fecha_transportador"`
	LugarPaisPlazoEntrega   string `json:"lugar_pais_plazo_entrega"`
	TransporteSucesivos     string `json:"transporte_sucesivos"`
	DetallesMercaderia      string `json:"detalles_mercaderia"`
	PesoBruto               string `json:"peso_bruto"`
	PesoNeto                string `json:"peso_neto"`
	Volumen                 string `json:"volumen"`
	Valor                   string `json:"valor"`
	Moneda                  string `json:"moneda"`
	Incoterm                string `json:"incoterm"`
	DeclaracionValorMerc    string `json:"declaracion_valor_mercaderia"`
	FacturaExportacion      string `json:"factura_exportacion"`
	NroDespacho             string `json:"nro_despacho"`
	InstruccionesAduana     string `json:"instrucciones_aduana"`
	ValorFleteExterno       string `json:"valor_flete_externo"`
	ValorReembolso          string `json:"valor_reembolso"`
	FirmaRemitente          string `json:"firma_remitente"`
	FechaFirmaRemitente     string `json:"fecha_firma_remitente"`
	FirmaTransportador      string `json:"firma_transportador"`
	FechaFirmaTransportador string `json:"fecha_firma_transportador"`
	FirmaDestinatario       string `json:"firma_destinatario"`
	FechaFirmaDestinatario  string `json:"fecha_firma_destinatario"`
	Observaciones           string `json:"observaciones"`
}

func logToJSON(entry map[string]interface{}) {
	f, err := os.OpenFile("logs.json", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println("\033[31m[ERROR]\033[0m No se pudo abrir logs.json:", err)
		return
	}
	defer f.Close()
	jsonData, _ := json.Marshal(entry)
	f.Write(append(jsonData, '\n'))
}

func main() {
	app := fiber.New()

	fmt.Println("\033[35m🚀 Iniciando microservicio PDF en :3002 con logs color + JSON\033[0m")

	app.Get("/", func(c *fiber.Ctx) error {
		return c.SendString("✅ Microservicio PDF corriendo.")
	})

	app.Post("/generate-pdf", func(c *fiber.Ctx) error {
		var crt CRT
		if err := c.BodyParser(&crt); err != nil {
			fmt.Println("\033[31m[ERROR]\033[0m JSON inválido recibido.")
			logToJSON(map[string]interface{}{
				"time":  time.Now().Format(time.RFC3339),
				"level": "error",
				"msg":   "JSON inválido en BodyParser",
				"err":   err.Error(),
			})
			return c.Status(400).JSON(fiber.Map{"error": "JSON inválido"})
		}

		body, _ := json.MarshalIndent(crt, "", "  ")
		fmt.Println("\033[36m[REQUEST BODY]\033[0m", string(body))

		logToJSON(map[string]interface{}{
			"time":  time.Now().Format(time.RFC3339),
			"level": "info",
			"msg":   "Recibido nuevo CRT",
			"crt":   crt,
		})

		pdf := gopdf.GoPdf{}
		pdf.Start(gopdf.Config{PageSize: *gopdf.PageSizeA4})
		fontErr := pdf.AddTTFFont("Arial", "./arial.ttf")
		if fontErr != nil {
			fmt.Println("\033[33m[WARN]\033[0m No se encontró arial.ttf, usando fuente estándar.")
		}
		if err := pdf.SetFont("Arial", "", 9); err != nil {
			pdf.SetFont("Helvetica", "", 9)
		}
		pdf.AddPage()

		// --- CAMPOS ALINEADOS ---
		// Ajustá los valores en mm según tu plantilla real. Estos son ejemplos razonables.

		// NumeroCRT
		x, y := mmToXY(200, 287)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.NumeroCRT)

		// Fecha Emisión
		x, y = mmToXY(20, 275)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.FechaEmision)

		// Remitente
		x, y = mmToXY(30, 260)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.Remitente)

		// Transportadora
		x, y = mmToXY(30, 250)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.Transportadora)

		// Destinatario
		x, y = mmToXY(30, 240)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.Destinatario)

		// Consignatario
		x, y = mmToXY(30, 230)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.Consignatario)

		// Notificar A
		x, y = mmToXY(30, 220)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.NotificarA)

		// Lugar Emisión
		x, y = mmToXY(30, 210)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.LugarEmision)

		// Lugar País Fecha Transportador
		x, y = mmToXY(30, 200)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.LugarPaisFechaTrans)

		// Lugar País Plazo Entrega
		x, y = mmToXY(30, 190)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.LugarPaisPlazoEntrega)

		// Transporte Sucesivos
		x, y = mmToXY(30, 180)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.TransporteSucesivos)

		// Detalles Mercadería
		x, y = mmToXY(30, 170)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.DetallesMercaderia)

		// Peso Bruto, Peso Neto, Volumen
		x, y = mmToXY(30, 160)
		pdf.SetXY(x, y)
		pdf.Cell(nil, "PB: "+crt.PesoBruto+" PN: "+crt.PesoNeto+" V: "+crt.Volumen)

		// Valor, Moneda, Incoterm
		x, y = mmToXY(30, 150)
		pdf.SetXY(x, y)
		pdf.Cell(nil, "Valor: "+crt.Valor+" "+crt.Moneda+" "+crt.Incoterm)

		// Declaración Valor Mercadería
		x, y = mmToXY(30, 140)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.DeclaracionValorMerc)

		// Factura Exportación, Nro Despacho
		x, y = mmToXY(30, 130)
		pdf.SetXY(x, y)
		pdf.Cell(nil, "Factura: "+crt.FacturaExportacion+" | Despacho: "+crt.NroDespacho)

		// Instrucciones Aduana
		x, y = mmToXY(30, 120)
		pdf.SetXY(x, y)
		pdf.Cell(nil, crt.InstruccionesAduana)

		// Valor Flete Externo, Valor Reembolso
		x, y = mmToXY(30, 110)
		pdf.SetXY(x, y)
		pdf.Cell(nil, "Flete ext: "+crt.ValorFleteExterno+" | Reemb: "+crt.ValorReembolso)

		// Observaciones
		x, y = mmToXY(30, 100)
		pdf.SetXY(x, y)
		pdf.Cell(nil, "Obs: "+crt.Observaciones)

		// Firmas
		x, y = mmToXY(30, 90)
		pdf.SetXY(x, y)
		pdf.Cell(nil, "Firma R: "+crt.FirmaRemitente+" "+crt.FechaFirmaRemitente)
		x, y = mmToXY(30, 80)
		pdf.SetXY(x, y)
		pdf.Cell(nil, "Firma T: "+crt.FirmaTransportador+" "+crt.FechaFirmaTransportador)
		x, y = mmToXY(30, 70)
		pdf.SetXY(x, y)
		pdf.Cell(nil, "Firma D: "+crt.FirmaDestinatario+" "+crt.FechaFirmaDestinatario)

		var buf bytes.Buffer
		pdf.Write(&buf)

		fmt.Println("\033[34m[PDF]\033[0m Generado para CRT", crt.NumeroCRT)
		logToJSON(map[string]interface{}{
			"time":       time.Now().Format(time.RFC3339),
			"level":      "success",
			"msg":        "PDF generado exitosamente",
			"crt_numero": crt.NumeroCRT,
		})

		c.Set("Content-Type", "application/pdf")
		c.Set("Content-Disposition", "inline; filename=CRT.pdf")
		return c.Send(buf.Bytes())
	})

	app.Listen(":3002")
}
