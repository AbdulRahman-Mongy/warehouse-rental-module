from odoo import _, api, fields, models
from odoo.exceptions import *


class WarehouseStage(models.Model):
    _name = 'warehouse.stage'
    _rec_name = 'name'

    name = fields.Char()
    done_stage = fields.Boolean(default=False)

    @api.constrains('done_stage')
    def _check_unique_done_stage(self):
        res = self.env['warehouse.stage'].search([('done_stage', '=', True)])
        if len(res) > 1:
            raise UserError(_("There is Already One Done Stage. You Can't Create Another One"))
