# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError , ValidationError


            

class QualityCheck(models.Model):
    _inherit = 'quality.check'

    weightbridgeline_id = fields.Many2one('weight.bridge.line', string='WeightBridge Order',
                                         domain = "[('purchase_order_id', '!=', False)]")
    
    pass_location_id = fields.Many2one(
        'stock.location', 'Pass Location',
        check_company=True,
        help="Location where the system will stock the products if pass")
    
    fail_location_id = fields.Many2one(
        'stock.location', 'Fail Location',
        check_company=True,
        help="Location where the system will stock the products if fail")
    
    @api.onchange('weightbridgeline_id')
    def onchange_weightbridgeline_id(self):
        self.product_id = self.weightbridgeline_id.product_id.id
        self.picking_id = self.weightbridgeline_id.purchase_order_id.picking_ids.id
        
    
    def do_fail(self):
        if self.picking_id.picking_type_id.code == 'incoming':
            if self.fail_location_id:
                self.picking_id.write({'location_dest_id':self.fail_location_id.id})
            else:
                raise ValidationError('You need add value to Fail location..')
        self.write({
            'quality_state': 'fail',
            'user_id': self.env.user.id,
            'control_date': datetime.now()})
        if self.env.context.get('no_redirect'):
            return True
        return self.redirect_after_pass_fail()

    def do_pass(self):
        if self.pass_location_id:
            if self.picking_id.picking_type_id.code == 'incoming':
                self.picking_id.write({'location_dest_id':self.pass_location_id.id})
            else:
                raise ValidationError('You need add value to Pass location..')
        self.write({'quality_state': 'pass',
                    'user_id': self.env.user.id,
                    'control_date': datetime.now()})
        if self.env.context.get('no_redirect'):
            return True
        return self.redirect_after_pass_fail()
        