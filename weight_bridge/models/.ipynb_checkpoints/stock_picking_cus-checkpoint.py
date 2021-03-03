# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError , ValidationError
from calendar import monthrange
from datetime import timedelta 

            

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    weightbridgeline_id = fields.Many2one('weight.bridge.line', string='WBL id')
    

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    period_month = fields.Boolean('Divide Transfers')
    no_of_transfers = fields.Integer('Transfers per month', 
                                     default = monthrange(fields.Date.today().year,fields.Date.today().month)[1])
    
    
    def multi_transfers(self):
        product_quantity = self.order_line[0].product_uom_qty
        quantity_divide = int(product_quantity / self.no_of_transfers)
        for _ in range(self.no_of_transfers-1):
            self.picking_ids[0].copy()
        next_date = self.date_order
        for pick in self.picking_ids:
            pick.write({'state':'waiting',
                       'scheduled_date': next_date,
                       'date_deadline': next_date})
            next_date = next_date + timedelta(days=1)
            for move in pick.move_ids_without_package:
                move.write({'product_uom_qty':quantity_divide,
                           'state':'waiting'})
                

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    
    period_month = fields.Boolean('Divide Transfers')
    no_of_transfers = fields.Integer('Transfers per month',
                                     default = monthrange(fields.Date.today().year,fields.Date.today().month)[1])
    
    
    
    def multi_transfers(self):
        product_quantity = self.order_line[0].product_qty
        quantity_divide = int(product_quantity / self.no_of_transfers)
        for _ in range(self.no_of_transfers-1):
            self.picking_ids[0].copy()
        for pick in self.picking_ids:
            pick.write({'state':'waiting'})
            for move in pick.move_ids_without_package:
                move.write({'product_uom_qty':quantity_divide,
                           'state':'waiting'})