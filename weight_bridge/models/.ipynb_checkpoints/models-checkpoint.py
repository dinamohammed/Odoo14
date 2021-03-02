# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError , ValidationError



            

class WeightBridgeLine(models.Model):
    _name = 'weight.bridge.line'
    _description = 'Weight Bridge Line'
    _order = 'date_weight_line desc, id desc'
    
    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
    description = fields.Text(string='Description')
    # , compute='get_product_name'
    product_id = fields.Many2one('product.product', string='Product', change_default=True)
    quality_check_id = fields.Many2one('quality.check', string='Quality')
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
    driver_id = fields.Many2one('res.partner', string='Partner', store=True)
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
    
    
    def button_accept(self):
        for order in self:
            if order.state == 'pending':
                if order.sale_order_id:
                    picks = order.sale_order_id.picking_ids.filtered(lambda x: x.product_id.id == order.product_id.id)
                    for move in picks.move_lines:
                        for move_line in move.move_line_ids.filtered(lambda m: m.state not in ['done', 'cancel']):
                            move_line.qty_done = order.weight_total
#                     raise ValidationError('%s'%picks.button_validate())
                    picks.write({'state':'done'})
                    order.sale_order_id.picking_ids.weightbridgeline_id = order.id
                    order.write({'state': 'accepted'})
                elif order.purchase_order_id:
                    if order.quality_check_id:
                        order.quality_check_id.do_pass()
#                         picks = order.purchase_order_id.picking_ids.filtered(
#                             lambda x: x.product_id.id == order.product_id.id)
                        picks = order.quality_check_id.picking_id
                        for move in picks.move_lines:
                            for move_line in move.move_line_ids.filtered(lambda m: m.state not in ['done', 'cancel']):
                                move_line.qty_done = order.weight_total
                        picks.button_validate()
                        order.purchase_order_id.picking_ids.weightbridgeline_id = order.id
                        order.write({'state': 'accepted'})
                    else:
                        raise ValidationError('You need to Add value to the Quality check field..')
            else:
                raise ValidationError('Accept only Pending Orders...')
        return True
    
    @api.onchange('driver_id')
    def get_mobile_number(self):
        for line in self:
            line['mobile_number'] = line.driver_id.mobile
                
    
    def button_confirm(self):
        for order in self:
            order.write({'state': 'pending'})
        return True
    
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}
    
    def button_refuse(self):
        self.write({'state': 'refused'})
        return {}
    
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq_date = None
            vals['date_weight_line'] = fields.Datetime.now()
            if 'date_weight_line' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_weight_line']))
            vals['name'] = self.env['ir.sequence'].next_by_code('weight.bridge.line', sequence_date=seq_date) or '/'
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
        self.description = self._get_product_purchase_description(product_lang)
    
    
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


    def action_timer_stop(self):
        end_time = fields.Datetime.now()
        return self._action_create_weigth(end_time)
    

        
