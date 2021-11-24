odoo.define('l10n_cr_pos.PaymentScreen', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');

    const L10nCoPosPaymentScreen = PaymentScreen =>
        class extends PaymentScreen {
            async _postPushOrderResolve(order, order_server_ids) {
                try {
                    if (this.env.pos.f_tipo_documento()) {
                        const result = await this.rpc({
                            model: 'pos.order',
                            method: 'search_order',
                            args: [order.uid],
                        });
                        order.set_tipo_documento(JSON.parse(result).tipo_documento || false);
                        order.set_secuencia(JSON.parse(result).sequence || false);
                        order.set_numero_electronico(JSON.parse(result).number_electronic || false);
                    }
                } finally {
                    return super._postPushOrderResolve(...arguments);
                }
            }
        };

    Registries.Component.extend(PaymentScreen, L10nCoPosPaymentScreen);

    return PaymentScreen;
});
