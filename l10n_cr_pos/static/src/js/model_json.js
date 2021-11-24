odoo.define('l10n_cr_pos.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var exports = {};
    var Session = require('web.session');
    var rpc = require('web.rpc');

    var OrderParent = models.Order.prototype;
    models.Order = models.Order.extend({
       initialize: function () {
             OrderParent.initialize.apply(this, arguments);
              this.number_electronic = null;
              this.sequence = null;
              this.tipo_documento = null;
       },
       init_from_JSON: function (json) {
            OrderParent.init_from_JSON.apply(this, arguments);
            this.number_electronic = json.number_electronic;
            this.sequence = json.sequence;
            this.tipo_documento = json.tipo_documento;
        },
        export_for_printing: function () {
            var order = OrderParent.export_for_printing.apply(this, arguments);
            var self =this;
            var json = this.get_json(self,order);
            return order;
        },
        export_as_JSON: function () {
            var order = OrderParent.export_as_JSON.apply(this, arguments);
            order.number_electronic = 1;
            order.sequence = 1;
            order.tipo_documento =  'h';
            return order;
        },

        get_json:function(self,order){
              return rpc.query({
                   model: 'pos.order',
                   method: 'search_order',
                   args: [self.uid],
                }, {
                    shadow: true,
                }).then(function (res) {
                    //localstorage.setItem('res',res)
                    //return res;
                    var j = JSON.parse(res);
                    self.tipo_documento = j.tipo_documento;
                    order.tipo_documento = j.tipo_documento;
                    order.sequence = j.sequence;
                    order.number_electronic = j.number_electronic;

                    return order;
                   //localstorage.setItem('tipo_documeto',j.tipo_documento)
                });


//            var self = this;
//            return rpc.query({
//               model: 'pos.order',
//               method: 'search_order',
//               args: [self.uid],
//            }, {
//                shadow: true,
//            }).then(function (res) {
//                return res;
//               //var j = JSON.parse(res);
//               //localstorage.setItem('tipo_documeto',j.tipo_documento)
//            });
        }


    });


    //models.load_fields('pos.order', ['number_electronic','sequence','tipo_documento']);


    models.load_fields('res.company', [
        'commercial_name',
        'state_name',
        'country_name',
        'district_name',
    ]);

    return exports;
});
