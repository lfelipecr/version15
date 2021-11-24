from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _get_new_values(self, record, on_change_result):
        vals = on_change_result.get("value", {})
        new_values = {}
        for fieldname, value in vals.items():
            if fieldname not in record:
                column = self._fields[fieldname]
                if value and column.type == "many2one":
                    value = value[0]
                new_values[fieldname] = value
        return new_values

    def play_onchanges(self, values, onchange_fields):
        onchange_specs = self._onchange_spec()
        all_values = values.copy()

        if self:
            self.ensure_one()
            record_values = self._convert_to_write(self.read()[0])
        else:
            record_values = {}
        for field in self._fields:
            if field not in all_values:
                all_values[field] = record_values.get(field, False)

        new_values = {}
        for field in onchange_fields:
            onchange_values = self.onchange(all_values, field, onchange_specs)
            new_values.update(self._get_new_values(values, onchange_values))
            all_values.update(new_values)

        return {
            f: v
            for f, v in all_values.items()
            if not self._fields[f].compute and (f in values or f in new_values)
        }
