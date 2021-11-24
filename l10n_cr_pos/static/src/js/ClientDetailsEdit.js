odoo.define('l10n_cr_pos.ClientDetailsEdit', function(require) {

    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');

    const LoyaltyClientDetailsEdit = ClientDetailsEdit => class extends ClientDetailsEdit {
        constructor() {
            super(...arguments);
            this.intFields = ['country_id', 'state_id', 'property_product_pricelist'];
            this.changes = {};
         }
        captureChange(event) {
            this.changes[event.target.name] = event.target.value;

            if(event.target.name=='vat'){
                var vat = $('input[name="vat"]').val();
                $.ajax({
                    url: 'https://api.hacienda.go.cr/fe/ae?identificacion='+vat,
                    success: function(respuesta) {
                        console.log(respuesta);
                        alert("Búsqueda exitosa!");
                        $('input[name="name"]').val(respuesta.nombre);
                        //this.changes["name"] = respuesta.nombre;
                    },
                    error: function() {
                        $('input[name="name"]').val("")
                        alert("No se ha podido obtener la información");
                        console.log("No se ha podido obtener la información");
                    }
                });
            }


        }
         saveChanges() {
            //El campo "NAME" al ser automático, necesita que se asigne nuevamente para ser guardado
            this.changes['name'] = $('input[name="name"]').val();

            let processedChanges = {};
            for (let [key, value] of Object.entries(this.changes)) {
                if (this.intFields.includes(key)) {
                    processedChanges[key] = parseInt(value) || false;
                } else {
                    processedChanges[key] = value;
                }
            }
             if ((!this.props.partner.name && !processedChanges.name) ||
                processedChanges.name === '' ){
                return this.showPopup('ErrorPopup', {
                  title: _('El nombre del cliente es requerido!.'),
                });
            }
            processedChanges.id = this.props.partner.id || false;
            this.trigger('save-changes', { processedChanges });
        }

    };

    Registries.Component.extend(ClientDetailsEdit, LoyaltyClientDetailsEdit);

    return ClientDetailsEdit;
});
