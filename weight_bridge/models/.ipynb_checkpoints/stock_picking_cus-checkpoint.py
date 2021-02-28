# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError , ValidationError


            

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    weightbridgeline_id = fields.Many2one('weight.bridge.line', string='WBL id')
    
    
# class StockImmediateTransfer(models.TransientModel):
#     _inherit = 'stock.immediate.transfer'
    
    
#     def process(self):
#         pickings_to_do = self.env['stock.picking']
#         pickings_not_to_do = self.env['stock.picking']
#         for line in self.immediate_transfer_line_ids:
#             if line.to_immediate is True:
#                 pickings_to_do |= line.picking_id
#             else:
#                 pickings_not_to_do |= line.picking_id

#         for picking in pickings_to_do:
#             # If still in draft => confirm and assign
#             if picking.state == 'draft':
#                 picking.action_confirm()
#                 if picking.state != 'assigned':
#                     picking.action_assign()
#                     if picking.state != 'assigned':
#                         raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
#             raise ValidationError('%s'%picking.weightbridgeline_id)
#             if picking.weightbridgeline_id:
#                 for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
#                     for move_line in move.move_line_ids.filtered(lambda n: n.product_id == picking.weightbridgeline_id.product_id.id):
#                         move_line.qty_done = picking.weightbridgeline_id.weight_total
#             else:
#                 for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
#                     for move_line in move.move_line_ids:
#                         move_line.qty_done = move_line.product_uom_qty

#         pickings_to_validate = self.env.context.get('button_validate_picking_ids')
#         if pickings_to_validate:
#             pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate)
#             pickings_to_validate = pickings_to_validate - pickings_not_to_do
#             return pickings_to_validate.with_context(skip_immediate=True).button_validate()
#         return True


   