from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError


class PlanLine(models.Model):
    _name = "mrp.plan.line"
    _description = "Plan Line"
    _order = 'id'
    _rec_name = "product_id"


     
    
    product_id = fields.Many2one('product.product', 'Component', required=True, check_company=True)
    
    name = fields.Char('Name')
    
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_uom_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',      
        required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control", domain="[('category_id', '=', product_uom_category_id)]")
    
    production_order_id = fields.Many2one(
        'mrp.production', 'Ordre de Fabrication',
        index=True, ondelete='cascade')
    production_plan_line_id = fields.Many2one(
        'mrp.plan', 'Parent BoM',
        index=True, ondelete='cascade')
  
    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('mrp.plan.line') or _('New')
        return super(PlanLine,self).create(vals)


    @api.onchange('product_id')
    def onchange_bom(self):
        if self.product_id:
            print(self.product_id)
            product_id = self.env['product.template'].search([('name','=',self.product_id.name)],limit=1)
            print(product_id)
            bom = self.env['mrp.bom'].search([('product_tmpl_id','=',product_id.id)],limit=1)
            self.bom_id = bom
            self.uom_id = self.product_id.uom_id.id
            self.plan_qty = 1

    @api.onchange('production_date')
    def onchange_date(self):
        if self.production_date and self.plan_date:
            if self.production_date < self.plan_date:
                raise ValidationError('Production Date should be greater than Plan Date...!!')


    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        if not self.product_id and self.bom_id:
            self.product_id = self.bom_id.product_id or self.bom_id.product_tmpl_id.product_variant_ids[:1]
        self.plan_qty = self.bom_id.product_qty or 1.0
        self.uom_id = self.bom_id and self.bom_id.product_uom_id.id or self.product_id.uom_id.id
        print ('Cool')
        self.move_raw_plan_ids = [(2, move.id) for move in self.move_raw_plan_ids.filtered(lambda m: m.bom_line_id)]
        
    @api.onchange('bom_id', 'product_id', 'product_qty', 'product_uom_id')
    def _onchange_move_raw(self):
        if not self.bom_id:
            return
        # Clear move raws if we are changing the product. In case of creation (self._origin is empty),
        # we need to avoid keeping incorrect lines, so clearing is necessary too.

        if self.bom_id and self.product_id and self.plan_qty > 0:
            # keep manual entries
            list_move_raw = [(4, move.id) for move in self.move_raw_plan_ids.filtered(lambda m: not m.bom_line_id)]
            moves_raw_values = self._get_moves_raw_values()
            print (moves_raw_values)
            move_raw_dict = {move.bom_line_id.id: move for move in self.move_raw_plan_ids.filtered(lambda m: m.bom_line_id)}
            for move_raw_values in moves_raw_values:
                if move_raw_values['bom_line_id'] in move_raw_dict:
                    # update existing entries
                    list_move_raw += [(1, move_raw_dict[move_raw_values['bom_line_id']].id, move_raw_values)]
                else:
                    # add new entries
                    list_move_raw += [(0, 0, move_raw_values)]
            self.move_raw_plan_ids = list_move_raw
        else:
            self.move_raw_plan_ids = [(2, move.id) for move in self.move_raw_plan_ids.filtered(lambda m: m.bom_line_id)]
    def _get_moves_raw_values(self):
        moves = []
        for production in self:
            if not production.bom_id:
                continue
            factor = production.uom_id._compute_quantity(production.plan_qty, production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(production.product_id, factor, picking_type=production.bom_id.picking_type_id)
            for bom_line, line_data in lines:
                if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom' or\
                        bom_line.product_id.type not in ['product', 'consu']:
                    continue
                operation = bom_line.operation_id.id or line_data['parent_line'] and line_data['parent_line'].operation_id.id
                moves.append(production._get_move_raw_values(
                    bom_line.product_id,
                    line_data['qty'],
                    bom_line.product_uom_id,
                    operation,
                    bom_line
                ))
        return moves

    def _get_move_raw_values(self, product_id, product_uom_qty, product_uom, operation_id=False, bom_line=False):
        #source_location = self.location_src_id
        origin = self.name
        """ if self.orderpoint_id and self.origin:
            origin = self.origin.replace(
                '%s - ' % (self.orderpoint_id.display_name), '')
            origin = '%s,%s' % (origin, self.name) """
        data = {
            'sequence': bom_line.sequence if bom_line else 10,
            'name': self.name,
            'date': self.production_date_debut,
            'date_deadline': self.production_date_fin,
            'bom_line_id': bom_line.id if bom_line else False,
            'product_id': product_id.id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom.id,
            #'location_id': source_location.id,
            #'location_dest_id': self.product_id.with_company(self.company_id).property_stock_production.id,
            'raw_material_production_plan_line_id': self.id,
            'company_id': self.company_id.id,
            #'operation_id': operation_id,
            #'price_unit': product_id.standard_price,
            #'procure_method': 'make_to_stock',
            #'origin': origin,
            #'state': 'draft',
            #'warehouse_id': source_location.warehouse_id.id,
            #'group_id': self.procurement_group_id.id,
            #'propagate_cancel': self.propagate_cancel,
        }
        
        return data
    
    def _update_raw_moves(self, factor):
        self.ensure_one()
        update_info = []
        move_to_unlink = self.env['stock.move.plan']
        for move in self.move_raw_plan_ids.filtered(lambda m: m.state not in ('done', 'cancel')):
            old_qty = move.product_uom_qty
            new_qty = old_qty * factor
            if new_qty > 0:
                move.write({'product_uom_qty': new_qty})
                move._action_assign()
                update_info.append((move, old_qty, new_qty))
            else:
                if move.quantity_done > 0:
                    raise UserError(_('Lines need to be deleted, but can not as you still have some quantities to consume in them. '))
                move._action_cancel()
                move_to_unlink |= move
        move_to_unlink.unlink()
        print (update_info)
        return update_info

    @api.onchange('bom_id', 'product_qty', 'product_uom_id')
    def _onchange_move_finished(self):
        if self.product_id and self.product_qty > 0:
            self._create_update_move_finished()
        else:
            self.move_finished_ids = [(2, move.id) for move in self.move_finished_ids.filtered(lambda m: m.bom_line_id)]

    