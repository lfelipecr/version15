odoo.define('l10n_cr_pos.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var exports = {};

    var OrderParent = models.Order.prototype;
    models.Order = models.Order.extend({
        export_for_printing: function () {
            var order = OrderParent.export_for_printing.apply(this, arguments);
            order.number_electronic = this.get('number_electronic');
            order.sequence = this.get('sequence');
            order.tipo_documento = this.get('tipo_documento');
            return order;
        },
        export_as_JSON: function () {
            var order = OrderParent.export_as_JSON.apply(this, arguments);
            order.number_electronic = this.get('number_electronic');
            order.sequence = this.get('sequence');
            order.tipo_documento = this.get('tipo_documento');
            return order;
        }
    });

    models.load_fields('res.company', [
        'commercial_name',
        'state_name',
        'country_name',
        'district_name',
    ]);

    return exports;
});
