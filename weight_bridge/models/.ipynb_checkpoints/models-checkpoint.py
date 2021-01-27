# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime


class WeightBridge(models.Model):
    _name = 'weight.bridge'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "WeightBridge"
    _order = 'date_weight desc, id desc'
    
    
    driver_name = fields.Many2one('res.partner', string='Driver')
    mobile_number = fields.Char('Mobile Number', compute='get_mobile_number')
    car_number = fields.Char('Car Number')
    permission_number = fields.Char('Permission Number')
    date_weight = fields.Datetime('Date')
    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    order_line = fields.One2many('weight.bridge.line', 'order_id', string='Weight Lines', states={ 'done': [('readonly', True)]}, copy=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)


    
    READONLY_STATES = {
        'done': [('readonly', True)],
    }
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date_weight' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_weight']))
            vals['name'] = self.env['ir.sequence'].next_by_code('weight.bridge', sequence_date=seq_date) or '/'
        return super(WeightBridge, self).create(vals)

    
    @api.onchange('driver_name')
    def get_mobile_number(self):
        for line in self:
            line['mobile_number'] = line.driver_name.mobile
            
            

class WeightBridgeLine(models.Model):
    _name = 'weight.bridge.line'
    _description = 'Weight Bridge Line'
    _order = 'order_id, id'
    
    
    name = fields.Text(string='Description', required=True , compute='get_product_name')
    product_id = fields.Many2one('product.product', string='Product', change_default=True)
    #domain=[('purchase_ok', '=', True)],
    weight_before = fields.Float('Weight Before')
    weight_after = fields.Float('Weight After')
    weight_total = fields.Float('Weight Total',compute='get_total_weight')
    order_id = fields.Many2one('weight.bridge', string='Weight Reference', index=True, required=True, ondelete='cascade')
    state = fields.Selection(related='order_id.state', store=True, readonly=False)
    date_weight_line = fields.Datetime('Date per Line')
    driver_id = fields.Many2one('res.partner', related='order_id.driver_name', string='Partner', readonly=True, store=True)

    
    @api.onchange('weight_before','weight_after')
    def get_total_weight(self):
        for line in self:
            if line.weight_after > line.weight_before:
                line['weight_total'] = line.weight_after - line.weight_before
            else if line.weight_after < line.weight_before:
                line['weight_total'] = line.weight_before - line.weight_after
                
                
    def _get_product_purchase_description(self, product_lang):
        self.ensure_one()
        name = product_lang.display_name

        return name
    
    
    @api.onchange('product_id')
    def get_product_name(self):
        if not self.product_id:
            return
        product_lang = self.product_id.with_context(
            lang=self.driver_id.lang,
            partner_id=self.driver_id.id,
            company_id=self.company_id.id,
        )
        self.name = self._get_product_purchase_description(product_lang)
    
    

    
    
        
    
    



    
    
        
