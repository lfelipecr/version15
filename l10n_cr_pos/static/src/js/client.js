odoo.define('l10n_cr_pos.pos_extended_partner', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');



    var QWeb = core.qweb;
    var _t = core._t;

    var _super_posmodel = models.PosModel.prototype;


    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var res_partner = _.find(this.models, function(model){ return model.model === 'res.partner'; });
            res_partner.fields.push('p2p_document_type');
            res_partner.fields.push('identification_id');
            return _super_posmodel.initialize.call(this, session, attributes);
        },

    });
});

