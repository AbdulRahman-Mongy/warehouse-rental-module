from odoo import api, fields, models


class WarehouseStage(models.Model):
    _name = 'warehouse.stage'
    _rec_name = 'name'

    name = fields.Char()
