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
    difference = fields.Float('Weight Differences')
    product_id = fields.Many2one('product.product', string='Product', change_default=True)
    start_weight = fields.Float('Weight Before')
    end_weight = fields.Float('Weight After')
    sale_reference = fields.Many2one('sale.order', string='Sale Order Ref')
    purchase_reference = fields.Many2one('purchase.order', string='Purchase Order Ref')
    
    
    def save_weights(self):
        values = {
            'order_id': self.order_id.id,
            'date_weight_line': datetime.now(),
            'name': self.description,
            'driver_id': self.driver_id.id,
            'weight_total': self.difference,
            'product_id': self.product_id.id,
            'weight_before': self.start_weight,
            'weight_after': self.end_weight,
            'time_spent': self.time_spent,
            'sale_order_id': self.sale_reference.id,
            'purchase_order_id': self.purchase_reference.id,
        }
        self.order_id.write({
            'date_weight': fields.datetime.now(),
        })
        return self.env['weight.bridge.line'].create(values)


