# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError , ValidationError
            

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    weightbridgeline_id = fields.Many2one('weight.bridge.line', string='WBL id')
    

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    period_month = fields.Boolean('Divide Transfers')
    no_of_transfers = fields.Integer('Transfers per month', default = fields.Date.today().day)
