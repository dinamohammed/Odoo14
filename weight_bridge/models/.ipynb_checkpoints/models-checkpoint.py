# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


            

class WeightBridgeLine(models.Model):
    _name = 'weight.bridge.line'
    _description = 'Weight Bridge Line'
    _order = 'date_weight_line desc, id desc'
    
    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
    description = fields.Text(string='Description')
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
    driver_id = fields.Many2one('res.partner', string='Driver', store=True)
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
    
    ################# For Transfers #######################
    
    picking_ids = fields.One2many('stock.picking', 'weightbridge_id', string='Transfers')
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')
    
    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for order in self:
            order.delivery_count = len(order.picking_ids)
            
    def action_view_delivery(self):
        '''
        This function returns an action that display existing delivery orders
        of given weightbridge ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        # Prepare the context.
        picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]
        action['context'] = dict(self._context, default_picking_id=picking_id.id,
                                 default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.weight_name,
                                 default_group_id=picking_id.group_id.id)
        return action

    
    
    
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
    




    
    
        
