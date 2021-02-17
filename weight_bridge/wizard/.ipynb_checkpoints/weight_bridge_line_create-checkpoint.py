# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class WeightBridgeCreateLine(models.TransientModel):
    _name = 'weight.bridge.create.line'
    _description = "Create Weights from timer"

    _sql_constraints = [('time_positive', 'CHECK(time_spent > 0)', 'The time must be positive' )]
    
    time_spent = fields.Float('Time', precision_digits=2)
    description = fields.Char('Description')
    order_id = fields.Many2one('weight.bridge', string='Weight Reference', index=True, required=True, ondelete='cascade')
    driver_id = fields.Many2one('res.partner', related='order_id.driver_name', string='Partner')
    difference = fields.Float('Weight Differences',compute = "")
    product_id = fields.Many2one('product.product', string='Product', change_default=True)
    end_weight = fields.Float('Weight After')
    sale_reference = fields.Many2one('sale.order', string='Sale Order Ref')
    purchase_reference = fields.Many2one('purchase.order', string='Purchase Order Ref')
    
    
    def save_weights(self):
        line_id = self.env['weight.bridge.line'].search([('order_id', '=', self.order_id.id)], limit=1)
        start_weight = line_id.weight_before
        end_weight = 0.0
        difference = 0.0
        if self.end_weight :
            end_weight = self.end_weight
        if end_weight > start_weight:
            difference = end_weight - start_weight
        elif end_weight < start_weight:
            difference = start_weight - end_weight
        
        return line_id.write({
            'date_weight_line': datetime.now(),
            'name': self.description,
            'weight_total': difference,
            'weight_after': self.end_weight,
            'time_spent': self.time_spent,
        })
    
    
class WeightBridgeCreateLine2(models.TransientModel):
    _name = 'weight.bridge.create.line2'
    _description = "Create Weights from timer"

    order_id = fields.Many2one('weight.bridge', string='Weight Reference', index=True, required=True, ondelete='cascade')
    driver_id = fields.Many2one('res.partner', string='Partner')
    product_id = fields.Many2one('product.product', string='Product', change_default=True)
    start_weight = fields.Float('Weight Before')
    sale_reference = fields.Many2one('sale.order', string='Sale Order Ref')
    purchase_reference = fields.Many2one('purchase.order', string='Purchase Order Ref')
    
    
    
    def save_weights2(self):
        values = {
            'order_id': self.order_id.id,
            'date_weight_line': datetime.now(),
            'driver_id': self.driver_id.id,
            'product_id': self.product_id.id,
            'weight_before': self.start_weight,
            'sale_order_id': self.sale_reference.id,
            'purchase_order_id': self.purchase_reference.id,
        }
        self.order_id.write({
            'date_weight': fields.datetime.now(),
        })
        return self.env['weight.bridge.line'].create(values)

