# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WarehouseRentalOrder(models.Model):
    _name = 'warehouse.rental.order'
    _rec_name = 'name'

    name = fields.Char(required=True)
    warehouse_stage_id = fields.Many2one(comodel_name="warehouse.stage", required=True)
    date = fields.Datetime(related='sale_id.date_order', store=True)
    state = fields.Selection(selection=[
        ('pending', 'Pending'),
        ('done', 'Done'),
    ], default='pending')

    # SO fields
    partner_id = fields.Many2one(related='sale_id.partner_id')
    sale_id = fields.Many2one(comodel_name="sale.order")
    order_line_ids = fields.One2many(related='sale_id.order_line', readonly=False)

    # accounting fields
    invoice_id = fields.Many2one(comodel_name="account.move", readonly=True)

    def create_invoice(self):
        move = self._create_invoice()
        self.invoice_id = move
        self.state = 'done'
        self.sale_id.state = 'sale'
        return True

    def _create_invoice(self):
        move = self.env['account.move']
        values = self.prepare_invoice()
        move = move.create(values)
        return move

    def prepare_invoice(self):
        lines = []
        for line in self.order_line_ids:
            lines.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'price_unit': line.price_unit,
                'product_uom_id': line.product_uom.id,
                'quantity': line.product_uom_qty,
            }))
        meta = {
            'move_type': 'out_invoice',
            'invoice_date': self.date.date(),
            'partner_id': self.partner_id.id,
            'invoice_line_ids': lines,
        }
        return meta

    def _auto_mark_stages_as_done(self):
        done_stage = self.env['warehouse.stage'].search([('done_stage', '=', True)], limit=1)
        if not done_stage:
            return
        rentals = self.env['warehouse.rental.order'].search([('warehouse_stage_id', '!=', done_stage.id)])
        for ro in rentals:
            done_lines = ro.order_line_ids.filtered(lambda line: line.rent_to and line.rent_to < fields.Datetime.now())
            if len(done_lines) == len(ro.order_line_ids):
                ro.warehouse_stage_id = done_stage
