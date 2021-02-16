# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT



class WeightBridge(models.Model):
    _name = 'weight.bridge'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "WeightBridge"
    _order = 'date_weight desc, id desc'
    
    
    driver_name = fields.Many2one('res.partner', string='Driver')
    mobile_number = fields.Char('Mobile Number', compute='get_mobile_number')
    car_number = fields.Char('Car Number')
    reference = fields.Char('PO/SO No.')
    permission_number = fields.Char('Permission Number')
    date_weight = fields.Datetime('Date',readonly = True)
    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    order_line = fields.One2many('weight.bridge.line', 'order_id', string='Weight Lines', copy=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    

    READONLY_STATES = {
        'done': [('readonly', True)],
    }
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq_date = None
            vals['date_weight'] = fields.Datetime.now()
            if 'date_weight' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_weight']))
            vals['name'] = self.env['ir.sequence'].next_by_code('weight.bridge', sequence_date=seq_date) or '/'
        return super(WeightBridge, self).create(vals)

    
    @api.onchange('driver_name')
    def get_mobile_number(self):
        for line in self:
            line['mobile_number'] = line.driver_name.mobile
    
    
    def button_confirm(self):
        for order in self:
            order.write({'state': 'done'})
        return True
    
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}
    

            

class WeightBridgeLine(models.Model):
    _name = 'weight.bridge.line'
    _description = 'Weight Bridge Line'
    _order = 'order_id, id'
    
    
    name = fields.Text(string='Description')
    # , compute='get_product_name'
    product_id = fields.Many2one('product.product', string='Product', change_default=True)
    #domain=[('purchase_ok', '=', True)],
    weight_before = fields.Float('Weight Before')
    weight_after = fields.Float('Weight After')
    weight_total = fields.Float('Weight Total')
    order_id = fields.Many2one('weight.bridge', string='Weight Reference')
    state = fields.Selection(related='order_id.state', store=True, readonly=False)
    date_weight_line = fields.Datetime('Date per Line')
    driver_id = fields.Many2one('res.partner', related='order_id.driver_name', string='Partner', readonly=True, store=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    time_spent = fields.Float('Time', precision_digits=2)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order Ref')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order Ref')


    
    @api.onchange('weight_before','weight_after')
    def get_total_weight(self):
        for line in self:
            if line.weight_after or line.weight_before:
                if line.weight_after > line.weight_before:
                    line['weight_total'] = line.weight_after - line.weight_before
                elif line.weight_after < line.weight_before:
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
    
    
        # fields regarding timer 
    
    weight_timer_start = fields.Datetime("Weight Timer Start", default=None)
    weight_timer_pause = fields.Datetime("Weight Timer Last Pause")
    weight_timer_first_start = fields.Datetime("Weight Timer First Use", readonly=True)
    weight_timer_last_stop = fields.Datetime("Weight Timer Last Use", readonly=True)

    
    def action_timer_start(self):
        self.ensure_one()
        if not self.weight_timer_first_start:
            self.write({'weight_timer_first_start': fields.Datetime.now()})
            self.write({'weight_before': self.weight_before})
        return self.write({'weight_timer_start': fields.Datetime.now(),
                          'weight_before': self.weight_before})

    def action_timer_pause(self):
        self.write({'weight_timer_pause': fields.Datetime.now()})
    
    def action_timer_resume(self):
        new_start = self.weight_timer_start + (fields.Datetime.now() - self.weight_timer_pause)
        self.write({
            'weight_timer_start': new_start,
            'weight_timer_pause': False
        })

    def action_timer_stop(self):
        self.ensure_one()
        start_time = self.weight_timer_start
        if start_time:  # timer was either running or paused
            pause_time = self.weight_timer_pause
            if pause_time:
                start_time = start_time + (fields.Datetime.now() - pause_time)
            minutes_spent = (fields.Datetime.now() - start_time).total_seconds() / 60
#             minutes_spent = self._timer_rounding(minutes_spent)
            end_weight = 0.0
            difference = 0.0
            if self.weight_after :
                end_weight = self.weight_after
            if end_weight > self.weight_before:
                difference = end_weight - self.weight_before
            elif end_weight < self.weight_before:
                difference = self.weight_before - end_weight
            start_weight = self.weight_before
            sale_reference = 0
            purchase_reference = 0
            if self.sale_order_id :
                sale_reference = self.sale_order_id.id
            elif self.purchase_order_id: 
                purchase_reference = self.purchase_order_id.id
            else:
                sale_reference = False
                purchase_reference = False
                
            return self._action_create_weigth(minutes_spent * 60 / 3600 ,difference, start_weight, end_weight, sale_reference, 
                                              purchase_reference)
        return False
    
    def _action_create_weigth(self, time_spent, difference, start_weight, end_weight, sale_reference, purchase_reference):
        return {
            "name": _("Confirm Time and Weight"),
            "type": 'ir.actions.act_window',
            "res_model": 'weight.bridge.create.line',
            "views": [[False, "form"]],
            "target": 'new',
            "context": {
                **self.env.context,
                'active_id': self.id,
                'active_model': 'weight.bridge.line',
                'default_time_spent': time_spent,
                'default_difference': difference,
                'default_start_weight': start_weight,
                'default_end_weight': end_weight,
                'default_sale_reference': sale_reference,
                'default_purchase_reference': purchase_reference,
            },
        }


    

    
    
        
    
    



    
    
        
