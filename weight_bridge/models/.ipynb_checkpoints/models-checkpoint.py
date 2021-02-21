# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT



# class WeightBridge(models.Model):
#     _name = 'weight.bridge'
#     _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
#     _description = "WeightBridge"
#     _order = 'date_weight desc, id desc'
    
    
# #     driver_name = fields.Many2one('res.partner', string='Driver')
# #     mobile_number = fields.Char('Mobile Number', compute='get_mobile_number')
# #     car_number = fields.Char('Car Number')
#     reference = fields.Char('PO/SO No.')
#     permission_number = fields.Char('Permission Number')
#     date_weight = fields.Datetime('Date',readonly = True)
# #     name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('done', 'Done'),
#     ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
#     order_line = fields.One2many('weight.bridge.line', 'order_id', string='Weight Lines', copy=True)
#     company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    

#     READONLY_STATES = {
#         'done': [('readonly', True)],
#     }
    
#     @api.model
#     def create(self, vals):
#         if vals.get('name', 'New') == 'New':
#             seq_date = None
#             vals['date_weight'] = fields.Datetime.now()
#             if 'date_weight' in vals:
#                 seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_weight']))
#             vals['name'] = self.env['ir.sequence'].next_by_code('weight.bridge', sequence_date=seq_date) or '/'
#         return super(WeightBridge, self).create(vals)

    
#     @api.onchange('driver_name')
#     def get_mobile_number(self):
#         for line in self:
#             line['mobile_number'] = line.driver_name.mobile
    
    
#     def button_confirm(self):
#         for order in self:
#             order.write({'state': 'done'})
#         return True
    
#     def button_draft(self):
#         self.write({'state': 'draft'})
#         return {}
    

            

class WeightBridgeLine(models.Model):
    _name = 'weight.bridge.line'
    _description = 'Weight Bridge Line'
    _order = 'date_weight desc, id desc'
    
    weight_name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
    name = fields.Text(string='Description')
    # , compute='get_product_name'
    product_id = fields.Many2one('product.product', string='Product', change_default=True)
    barcode = fields.Char(related='product_id.barcode',string = 'Product Barcode')
    #domain=[('purchase_ok', '=', True)],
    driver_name = fields.Char(string='Driver Name')
    mobile_number = fields.Char('Mobile Number', compute='get_mobile_number')
    phone_number = fields.Char('Phone Number',)
    car_number = fields.Char('Car Number')
    container_number = fields.Char('Container Number')
    license_number = fields.Char('License Number')
    weight_before = fields.Float('Weight Before')
    weight_after = fields.Float('Weight After')
    weight_total = fields.Float('Weight Total')
#     order_id = fields.Many2one('weight.bridge', string='Weight Reference')
    date_weight_line = fields.Datetime('Date per Line')
    driver_id = fields.Many2one('res.partner', string='Driver', readonly=True, store=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    time_spent = fields.Float('Time', precision_digits=2)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order Ref')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order Ref')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
        ('done', 'Done'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    remarks = fields.Text('Remarks')
    
    
    @api.onchange('driver_id')
    def get_mobile_number(self):
        for line in self:
            line['mobile_number'] = line.driver_id.mobile
    
    
    def button_confirm(self):
        for order in self:
            order.write({'state': 'done'})
        return True
    
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}
    
    
    @api.model
    def create(self, vals):
        if vals.get('weight_name', 'New') == 'New':
            seq_date = None
            vals['date_weight_line'] = fields.Datetime.now()
            if 'date_weight_line' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_weight_line']))
            vals['weight_name'] = self.env['ir.sequence'].next_by_code('weight.bridge.line', sequence_date=seq_date) or '/'
        return super(WeightBridgeLine, self).create(vals)
    
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
        start_time = fields.Datetime.now()
        if not self.weight_timer_first_start:
            self.write({'weight_timer_first_start': fields.Datetime.now()})
            
        self.write({'weight_timer_start': fields.Datetime.now()})
        return self._action_create_weigth2(start_time)

    def action_timer_pause(self):
        self.write({'weight_timer_pause': fields.Datetime.now()})
    
    def action_timer_resume(self):
        new_start = self.weight_timer_start + (fields.Datetime.now() - self.weight_timer_pause)
        self.write({
            'weight_timer_start': new_start,
            'weight_timer_pause': False
        })

    def action_timer_stop(self):
#         self.ensure_one()
#         start_time = self.weight_timer_start
        end_time = fields.Datetime.now()
#         if start_time:  # timer was either running or paused
#             pause_time = self.weight_timer_pause
#             if pause_time:
#                 start_time = start_time + (fields.Datetime.now() - pause_time)
#             minutes_spent = (fields.Datetime.now() - start_time).total_seconds() / 60
        return self._action_create_weigth(end_time)
    
    def _action_create_weigth(self, end_time):
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
                'default_end_time': end_time,
            },
        }
    
    
    def _action_create_weigth2(self,start_time):
        return {
            "name": _("Start Recording"),
            "type": 'ir.actions.act_window',
            "res_model": 'weight.bridge.create.line2',
            "views": [[False, "form"]],
            "target": 'new',
            "context": {
                **self.env.context,
                'active_id': self.id,
                'active_model': 'weight.bridge.line',
                'default_start_time': start_time,
            },
        }


    

    
    
        
    
    



    
    
        
