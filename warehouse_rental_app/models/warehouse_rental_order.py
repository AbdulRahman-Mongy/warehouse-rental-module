# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WarehouseRentalOrder(models.Model):
    _name = 'warehouse.rental.order'
    _rec_name = 'name'

    name = fields.Char(required=True)
    warehouse_stage_id = fields.Many2one(comodel_name="warehouse.stage", required=True)
    date = fields.Date()
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
        self._create_invoice()
        self.state = 'done'
        return True

    def _create_invoice(self):
        return
        invoice = self.env['account.move']
        values = self.prepare_invoice_vals()
        invoice.create(values)

    def prepare_invoice_vals(self):
        return {}