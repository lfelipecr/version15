# TODOs

## Split

- [x] (Moy)Generate XML: Generar la estructura del XML desde los documentos de Odoo
- [x] (Moy) Send/Receive XML: Enviar el XML y Recibir la respuesta de Hacienda
- [ ] Update Document: Basado en las respuestas de hacienda, modificar los documentos de
      Odoo
- [ ] (Santana) Accounting: Todos los temas contables/legales para CR
- [ ] Exoneration Autorization: Autorizaciones de Exoneraciones
- [x] (Moy) CAByS: Descargar catalogo CAByS, Añadir campo en producto y en XML
- [x] (Moy) Lands: Cantones, Estados, Barrios, etc
- [x] (Moy) Currency (Exchange): Obtener el tipo de cambio desde Hacienda
- [x] (Moy) Validate RUT/Get name: Obtener el nombre desde Hacienda con el RUT y Validar
      el mismo
- [x] (Santana) Import: Importar XML y generar documentos desde ellos
- [x] (Santana) Mailling: Envío y Recepción de Correos con XML/PDF
- [ ] Refund: **No estamos seguros**
- [ ] ~~Phone Validation: Validación de teléfonos~~
- [ ] ~~Email Validation: Validación de correos~~

## Remove

- [ ] models/account_payment.py
- [ ] tools
- [ ] uom
- [ ] ~~XADES~~ Simplified

# Constraints

- [ ] invoice.tipo_documento accord to invoice.type
- [ ] identification
- [ ] inv.payment_term_id and not inv.payment_term_id.sale_conditions_id
- [ ] currency.name != self.company_id.currency_id.name and not currency.rate_ids
