odoo.define('l10n_cr_pos.pos', function (require) {
"use strict";

var models = require('point_of_sale.models');

models.PosModel = models.PosModel.extend({
    f_tipo_documento: function () {
        return true;
    },
});

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    export_for_printing: function () {
        var result = _super_order.export_for_printing.apply(this, arguments);
        result.tipo_documento = this.get_tipo_documento();
        result.numero_electronico = this.get_numero_electronico();
        result.secuencia = this.get_secuencia();
        return result;
    },
    set_tipo_documento: function (tipo_documento) {
        this.tipo_documento = tipo_documento;
    },
    get_tipo_documento: function () {
        return this.tipo_documento;
    },

    set_numero_electronico: function (numero_electronico) {
        this.numero_electronico = numero_electronico;
    },
    get_numero_electronico: function () {
        return this.numero_electronico;
    },

    set_secuencia: function (secuencia) {
        this.secuencia = secuencia;
    },
    get_secuencia: function () {
        return this.secuencia;
    },




    //MÉTODO PARA CONSULTAR
    wait_for_push_order: function () {
        var result = _super_order.wait_for_push_order.apply(this, arguments);
        result = Boolean(result || this.pos.f_tipo_documento());
        return result;
    }
});

});
