from odoo import api, fields, models


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
