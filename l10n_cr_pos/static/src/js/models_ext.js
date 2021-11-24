odoo.define('l10n_cr_pos.models', function (require) {
    "use strict";
    var models = require('point_of_sale.models');
      models.load_models({
        model: 'pos.order',
        fields: ['id','tipo_documento'],
        domain: [['state', '=', 'paid']],
        loaded: function (self, invoices) {
          var invoices_ids = _.pluck(invoices, 'id');
          self.prepare_invoices_data(invoices);
          self.invoices = invoices;
          self.db.add_invoices(invoices);
      }
    });

 });

