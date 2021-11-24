odoo.define('l10n_cr_pos.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var exports = {};


    models.load_fields('pos.order', ['number_electronic','sequence','tipo_documento']);


    models.load_fields('res.company', [
        'commercial_name',
        'state_name',
        'country_name',
        'district_name',
    ]);

    return exports;
});
