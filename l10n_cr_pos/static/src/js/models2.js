odoo.define('l10n_cr_pos.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var exports = {};
    var Session = require('web.session');
    var rpc = require('web.rpc');

//     var _sequence_next = function (seq) {
//        var idict = {
//            'year': moment().format('YYYY'),
//            'month': moment().format('MM'),
//            'day': moment().format('DD'),
//            'y': moment().format('YY'),
//            'h12': moment().format('hh')
//        };
//        var format = function (s, dict) {
//            var s_var = s || '';
//            $.each(dict, function (k, v) {
//                s_var = s_var.replace('%(' + k + ')s', v);
//            });
//            return s_var;
//        };
//        function pad(n, width, z) {
//            var z_var = z || '0';
//            var n_var = String(n);
//            if (n_var.length < width) {
//                n_var = new Array(width - n_var.length + 1).join(z_var) + n_var;
//            }
//            return n_var;
//        }
//        var num = seq.number_next_actual;
//        var prefix = format(seq.prefix, idict);
//        var suffix = format(seq.suffix, idict);
//        seq.number_next_actual += seq.number_increment;
//        return prefix + pad(num, seq.padding) + suffix;
//    };
//
//
//    var PosModelParent = models.PosModel.prototype;
//    models.PosModel = models.PosModel.extend({
//        load_server_data: function () {
//            var self = this;
//            self.models.push({
//                model: 'ir.sequence',
//                fields: [],
//                ids: function (s) { return [s.config.sequence_fe_id[0], s.config.sequence_te_id[0]]; },
//                loaded: function (s, sequence) {
//                    s.FE_sequence = sequence[0];
//                    s.TE_sequence = sequence[1];
//                },
//            });
//            return PosModelParent.load_server_data.apply(this, arguments);
//        },
//        push_and_invoice_order: function (order) {
//            if (order !== undefined) {
//                order.set({ 'sequence': this.FE_sequence.number_next_actual });
//                order.set({ 'number_electronic': _sequence_next(this.FE_sequence) });
//                order.set({ 'tipo_documento': 'FE' });
//            }
//            return PosModelParent.push_and_invoice_order.apply(this, arguments);
//        },
//        push_orders: function (order, opts) {
//            if (order !== undefined) {
//                // Revisar si es normal o devolucion . Pendiente !!!
//                if (order.client) {
//                    order.set({ 'sequence': this.FE_sequence.number_next_actual });
//                    order.set({ 'number_electronic': _sequence_next(this.FE_sequence) });
//                    order.set({ 'tipo_documento': 'FE' });
//                }
//                else {
//                    order.set({ 'sequence': this.TE_sequence.number_next_actual });
//                    order.set({ 'number_electronic': _sequence_next(this.TE_sequence) });
//                    order.set({ 'tipo_documento': 'TE' });
//                }
//            };
//            return PosModelParent.push_orders.apply(this, arguments);
//        }
//    });


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
            if (this.finalized){
//             const record = t.pos.rpc({
//                model: 'pos.order', method: 'search_order', args: [t.uid]
//            }).then(ar => ar[0]);
                    var self = this;
                    var i= rpc.query({
                       model: 'pos.order',
                       method: 'search_order',
                       args: [self.uid],
                    }, {
                        shadow: true,
                    }).then(function (res) {
                       var j = JSON.parse(res);
                       localstorage.setItem('tipo_documeto',j.tipo_documento)
                    });
//                  tableId = t.pos.rpc({
//                        model: 'pos.order',
//                        method: 'search_order',
//                        args: [t.uid],
//                    })
//                    .then(function (res) {
//                        var j = JSON.parse(res);
//                        j.clave
                        //localstorage.setItem('tp',i['tipo_documento'])
                    //});
                 //table.id = tableId;

//                    var j = t.pos.rpc({
//                        model: 'pos.order',
//                        method: 'search_order',
//                        args: [t.uid],
//                    })
//                    .then(function (res) {
//                        return res;
//                    });
            }


            var order = OrderParent.export_for_printing.apply(this, arguments);
            return order;
        },
        export_as_JSON: function () {
            var order = OrderParent.export_as_JSON.apply(this, arguments);
            order.number_electronic = 1;
            order.sequence = 1;
            order.tipo_documento =  'h';
            return order;
        },

        get_json: function(){

        }
    });


    function get_json(){

    }

    //models.load_fields('pos.order', ['number_electronic','sequence','tipo_documento']);


    models.load_fields('res.company', [
        'commercial_name',
        'state_name',
        'country_name',
        'district_name',
    ]);

    return exports;
});
