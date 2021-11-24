odoo.define('l10n_cr_pos.aaa', function(require)
{
    "use strict";

    var rpc = require('web.rpc');
    var Dialog = require('web.Dialog');
    var param_partner_id = null
    var name_address = "";
    var firstName = "";
    var lastName = "";
    var location_first_time = 'yes';

    $("input[name='vat']").on("blur", function(){
        var _vat = $(this).val();
        rpc.query({
           model: 'res.partner',
           method: '_get_vat_pos',
           args: [_vat],
        }).then(function (res) {
            var j = res;
            $('input[name="name"]').val('ghi');
            $('input[name="phone"]').val('7777777777');
            $('input[name="street"]').val('SO2New Shipping Street, 5');
            $('input[name="city"]').val('SO2NewShipping');
            $('input[name="zip"]').val('1200');
        });


    });

});

