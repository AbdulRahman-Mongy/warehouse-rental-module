from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Product(models.Model):
    _inherit = 'product.template'

    warehouse_stage_id = fields.Many2one(comodel_name="warehouse.stage")

    @api.constrains('warehouse_stage_id')
    def _check_product_service(self):
        for product in self:
            if product.warehouse_stage_id and product.type != 'service':
                raise UserError(_("Warehouse Stages only available to a product of type Service"))
