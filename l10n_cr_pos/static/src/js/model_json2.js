odoo.define('l10n_cr_pos.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var exports = {};
    var Session = require('web.session');
    var rpc = require('web.rpc');

    var OrderParent = models.Order.prototype;
    models.Order = models.Order.extend({

        set_tipo_documento: function (tipo_documento) {
        this.tipo_documento = tipo_documento;
        },
        get_tipo_documento: function () {
            return this.tipo_documento;
        },

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
//        getOrderReceiptEnv: function(){
//            var order = this;
////            var datalines : this.get_all_json(),
////            var receipt: this.export_for_printing(),
////            var orderlines: this.get_orderlines(),
////            var paymentlines: this.get_paymentlines(),
//
//            var self = this;
//            $.ajax({
//                type: "POST",
//                url: "/shop/confirm_quotation",
//                dataType: 'json',
//                data: {id: self.uid},
//                success: function (response) {
//                    //alert(response.number_electronic);
//                    //var j = JSON.parse(response);
//                    self.tipo_documento = response.tipo_documento;
//                    self.sequence = response.sequence;
//                    self.number_electronic = response.number_electronic;
//                },
//                error: function (e) {
//
//                }
//            });
//
//
//            return OrderParent.getOrderReceiptEnv.apply(this, arguments);
//
//
////            return {
////                order: order,
////                datalines : datalines,
////                receipt: receipt,
////                orderlines: orderlines,
////                paymentlines: paymentlines,
////            };
//
//        },
        willStart: function (self) {
            var _this = self;
            var getPolicy = _this.pos.rpc({
                model: 'pos.order',
                method: 'search_order',
                args: [_this.uid],
            }).then(function (response) {
                  var j = JSON.parse(response);
                  self.tipo_documento = j.tipo_documento;
            });
            //return Promise.all([getPolicy]);
        },
        export_for_printing: function () {
            //var data = [];
            //var data2 = [];
            var self = this;
            this.willStart(self);



//            function e_invoice(self){
//                $.ajax({
//                    type: "POST",
//                    url: "/shop/confirm_quotation",
//                    dataType: 'json',
//                    data: {id: self.uid},
//                    success: function (response) {
//                        alert(response.number_electronic);
//                        //var j = JSON.parse(response);
//                        self.tipo_documento = response.tipo_documento;
//                        self.sequence = response.sequence;
//                        self.number_electronic = response.number_electronic;
//                    },
//                    error: function (e) {
//
//                    }
//                });
//            }
//            function e_invoice(self){
//                 $.ajax({
//                        type: "POST",
//                        url: "/shop/confirm_quotation",
//                        dataType: 'json',
//                        data: {id: self.uid},
//                        success: function (response) {
//                            //var j = JSON.parse(response);
//                            self.tipo_documento = response.tipo_documento;
//                            self.sequence = response.sequence;
//                            self.number_electronic = response.number_electronic;
//                        },
//                        error: function (e) {
//
//                        }
//                    });
//            }

//
//            function electronic(self){
//                return rpc.query({
//                model: 'pos.order',
//                method: 'search_order',
//                args: [self.uid],
//                }).then(function (res) {
//                       return res;
//                });
//            }
//
//            var def1 = rpc.query({
//                model: 'pos.order',
//                method: 'search_order',
//                args: [self.uid]
//                });


            //var def2 = e_invoice(self);

            //var m = electronic(self);
            //var m = e_invoice(self);
            var json = OrderParent.export_for_printing.apply(this, arguments);

            //json.tipo_documento = self.tipo_documento;
            //json.sequence = self.sequence;
            //json.number_electronic = self.number_electronic;

            return json;

        },
        export_as_JSON: function () {
            var order = OrderParent.export_as_JSON.apply(this, arguments);
            order.tipo_documento = this.get_tipo_documento()
            //var self =this;
            //var json = this.get_json(self,order);
            return order;
        },

        get_json:function(self,order){
              return rpc.query({
                   model: 'pos.order',
                   method: 'search_order',
                   args: [self.uid],
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
