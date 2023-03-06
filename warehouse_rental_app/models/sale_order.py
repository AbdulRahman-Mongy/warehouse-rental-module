from odoo import _, api, fields, models
from odoo.exceptions import *


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[
        ('waiting_wro', 'Waiting Another Operation')
    ], tracking=True)

    def action_confirm(self):
        if not self.create_rental_order():
            return super(SaleOrder, self).action_confirm()
        return True

    def create_rental_order(self):
        for sale in self:
            if not sale.should_create_wro():
                return False
            sale.validate_available_shelves()
            wro = self.env['warehouse.rental.order']
            values = sale.prepare_wro_vals()
            wro.create(values)
            sale.state = 'waiting_wro'
        return True

    def should_create_wro(self):
        for sale in self:
            lines = sale.order_line.filtered(lambda line: not line.product_id.warehouse_stage_id)
            if lines:
                return False
            warehouse_stages = set()
            for line in sale.order_line:
                warehouse_stages.add(line.product_id.warehouse_stage_id.id)
            if len(warehouse_stages) != 1:
                return False
        return True

    def prepare_wro_vals(self):
        for sale in self:
            return {
                'name': f"Warehouse RO {sale.name}",
                'sale_id': sale.id,
                'warehouse_stage_id': sale.order_line.mapped('product_id')[-1].warehouse_stage_id.id,
            }

    def validate_available_shelves(self):
        for line in self.order_line:
            so_lines = self.env['sale.order.line'].search([
                ('id', '!=', line.id),
                ('product_id', '=', line.product_id.id),
                ('rent_to', '>', line.rent_from),
                ('rent_from', '<=', line.rent_to),
            ], limit=1)
            if so_lines:
                raise ValidationError(_(f"{line.product_id.display_name} is Already Rented From "
                                        f"{so_lines.rent_from} To {so_lines.rent_to}."))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rent_from = fields.Datetime()
    rent_to = fields.Datetime()

    @api.onchange('rent_from', 'rent_to')
    def onchange_rental_dates(self):
        for sale in self:
            if sale.product_id and sale.product_id.type == 'service' and sale.rent_from and sale.rent_to and sale.rent_to >= sale.rent_from:
                sale.product_uom_qty = (sale.rent_to - sale.rent_from).days
