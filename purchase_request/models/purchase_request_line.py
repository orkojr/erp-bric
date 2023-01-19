# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_STATES = [
    ("draft", "Draft"),
    ("to_approve", "To be approved"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("done", "Done"),
]


class PurchaseRequestLine(models.Model):

    _name = "purchase.request.line"
    _description = "Purchase Request Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Description", tracking=True)
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unite de Mesure",
        tracking=True,
    )
    product_qty = fields.Float(
        string="Quantity", tracking=True, digits="Product Unit of Measure"
    )
    request_id = fields.Many2one(
        comodel_name="purchase.request",
        string="Purchase Request",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="request_id.company_id",
        string="Company",
        store=True,
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        tracking=True,
    )
    analytic_tag_ids = fields.Many2many(
        "account.analytic.tag", string="Analytic Tags", tracking=True
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        related="request_id.requested_by",
        string="Requested by",
        store=True,
    )
    vehicule = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Vehicule",
        required=False,
        tracking=True,
    )
    chauffeur = fields.Many2one(
        comodel_name="hr.employee",
        string="Chauffeur",
        required=False,
        tracking=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        related="request_id.assigned_to",
        string="Assigned to",
        store=True,
    )
    date_start = fields.Date(related="request_id.date_start", store=True)
    description = fields.Text(
        related="request_id.description",
        string="PR Description",
        store=True,
        readonly=False,
    )
    origin = fields.Char(
        related="request_id.origin", string="Source Document", store=True
    )
    date_required = fields.Date(
        string="Request Date",
        required=True,
        tracking=True,
        default=fields.Date.context_today,
    )
    is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
    is_recu = fields.Boolean(string="Ne necessite pas un fournisseur")
    specifications = fields.Text()
    request_state = fields.Selection(
        string="Request state",
        related="request_id.state",
        store=True,
    )
    """ supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Preferred supplier",
        compute="_compute_supplier_id",
        compute_sudo=True,
        store=True,
    ) """
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Preferred supplier",
        compute_sudo=True,
        store=True,
    )
    cancelled = fields.Boolean(readonly=True, default=False, copy=False)

    purchased_qty = fields.Float(
        string="RFQ/PO Qty",
        digits="Product Unit of Measure",
        compute="_compute_purchased_qty",
    )
    """ invoice_lines = fields.Many2many(
        comodel_name="account.move.line",
        relation="purchase_request_account_move_line_rel",
        column1="purchase_request_line_id",
        column2="account_move_line_id",
        string="Account Move Lines",
        readonly=True,
        copy=False,
    ) """
    purchase_lines = fields.Many2many(
        comodel_name="purchase.order.line",
        relation="purchase_request_purchase_order_line_rel",
        column1="purchase_request_line_id",
        column2="purchase_order_line_id",
        string="Purchase Order Lines",
        readonly=True,
        copy=False,
    )
    purchase_state = fields.Selection(
        compute="_compute_purchase_state",
        string="Purchase Status",
        selection=lambda self: self.env["purchase.order"]._fields["state"].selection,
        store=True,
    )
    move_dest_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="created_purchase_request_line_id",
        string="Downstream Moves",
    )

    line_cout_ids = fields.One2many(
        comodel_name="purchase.request.line.cout",
        inverse_name="request_cout_id",
        string="Autres couts",
        readonly=False,
        copy=True,
        tracking=True,
    )

    orderpoint_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint", string="Orderpoint"
    )
    purchase_request_allocation_ids = fields.One2many(
        comodel_name="purchase.request.allocation",
        inverse_name="purchase_request_line_id",
        string="Purchase Request Allocation",
    )

    qty_in_progress = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity in progress.",
    )
    qty_done = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity completed",
    )
    qty_cancelled = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty_cancelled",
        store=True,
        help="Quantity cancelled",
    )
    qty_to_buy = fields.Boolean(
        compute="_compute_qty_to_buy",
        string="There is some pending qty to buy",
        store=True,
    )
    pending_qty_to_receive = fields.Float(
        compute="_compute_qty_to_buy",
        digits="Product Unit of Measure",
        copy=False,
        string="Pending Qty to Receive",
        store=True,
    )
    price_unit = fields.Float(string='Prix Unitaire', required=False, digits='Product Price')
    cout_total = fields.Float(
        string='Cout d\'achat',
        compute='_compute_cout_total',
        store=True,
        default=0.0
    )
    cout_lies = fields.Monetary(
        string='Couts lies',
        compute='_compute_cout_lies',
        store=True,
        default=0.0
    )
    estimated_cost = fields.Monetary(
        compute="_compute_amount",
        default=0.0,
        help="Estimated cost of Purchase Request Line, not propagated to PO.",
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain=[("purchase_ok", "=", True)],
        tracking=True,
    )
    repair_line_ids = fields.One2many('maintenance.request.line', 'invoice_line_id', readonly=True, copy=False)
    vehicule = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Moyen de transport",
        required=False,
        tracking=True,
    )
    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id",
        "purchase_request_allocation_ids.purchase_line_id.state",
        "request_id.state",
        "product_qty",
    )
    def _compute_qty_to_buy(self):
        for pr in self:
            qty_to_buy = sum(pr.mapped("product_qty")) - sum(pr.mapped("qty_done"))
            pr.qty_to_buy = qty_to_buy > 0.0
            pr.pending_qty_to_receive = qty_to_buy

    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id.state",
        "purchase_request_allocation_ids.purchase_line_id",
    )
    def _compute_qty(self):
        for request in self:
            done_qty = sum(
                request.purchase_request_allocation_ids.mapped("allocated_product_qty")
            )
            open_qty = sum(
                request.purchase_request_allocation_ids.mapped("open_product_qty")
            )
            request.qty_done = done_qty
            request.qty_in_progress = open_qty

    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id.order_id.state",
        "purchase_request_allocation_ids.purchase_line_id",
    )
    def _compute_qty_cancelled(self):
        for request in self:
            if request.product_id.type != "service":
                qty_cancelled = sum(
                    request.mapped("purchase_request_allocation_ids.stock_move_id")
                    .filtered(lambda sm: sm.state == "cancel")
                    .mapped("product_qty")
                )
            else:
                qty_cancelled = sum(
                    request.mapped("purchase_request_allocation_ids.purchase_line_id")
                    .filtered(lambda sm: sm.state == "cancel")
                    .mapped("product_qty")
                )
                # done this way as i cannot track what was received before
                # cancelled the purchase order
                qty_cancelled -= request.qty_done
            if request.product_uom_id:
                request.qty_cancelled = (
                    max(
                        0,
                        request.product_id.uom_id._compute_quantity(
                            qty_cancelled, request.product_uom_id
                        ),
                    )
                    if request.purchase_request_allocation_ids
                    else 0
                )
            else:
                request.qty_cancelled = qty_cancelled

    @api.depends(
        "product_id",
        "name",
        "product_uom_id",
        "product_qty",
        "analytic_account_id",
        "date_required",
        "specifications",
        "purchase_lines",
    )
    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ("approved", "rejected", "done","stock", "po_ro", "paye"):
                rec.is_editable = False
            else:
                rec.is_editable = True
        for rec in self.filtered(lambda p: p.purchase_lines):
            rec.is_editable = False
    
    @api.depends('product_id')
    def _compute_prix_unitaire(self):
        for line in self:
            line.price_unit = line.product_id.standard_price

    @api.depends("product_id", "product_id.seller_ids")
    def _compute_supplier_id(self):
        for rec in self:
            sellers = rec.product_id.seller_ids.filtered(
                lambda si: not si.company_id or si.company_id == rec.company_id
            )
            rec.supplier_id = sellers[0].name if sellers else False

    """ @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = "[{}] {}".format(self.product_id.code, name)
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name """
    
    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = "[{}] {}".format(self.product_id.code, name)
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name
            sellers = self.product_id.seller_ids
            self.supplier_id = sellers[0].name if sellers else False
            self.price_unit = sellers[0].price if sellers else False
    @api.onchange("supplier_id", "product_id")
    def onchange_supplier_id(self):
        if self.supplier_id:
            
            sellers = self.product_id.seller_ids 
            if sellers:
                for seller in sellers:
                    if self.supplier_id == seller.name:

                        self.price_unit = seller.price
    @api.depends('product_qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.update({
                'estimated_cost' : line.product_qty * line.price_unit
            })
    @api.depends("line_cout_ids")
    def _compute_cout_lies(self):
        for rec in self:
            cout_t = 0.0
            for line in rec.line_cout_ids:
                cout_t += line.cout
            self.cout_lies = cout_t
    
    @api.depends('estimated_cost', 'line_cout_ids')
    def _compute_cout_total(self):
        for main in self:
            print ("DEMANDE:",main.estimated_cost)
            cout_t = 0.0
            for line in main.line_cout_ids:
                cout_t += line.cout
            self.cout_total = cout_t + main.estimated_cost
           
    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({"cancelled": True})

    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({"cancelled": False})

    def write(self, vals):
        res = super(PurchaseRequestLine, self).write(vals)
        if vals.get("cancelled"):
            requests = self.mapped("request_id")
            requests.check_auto_reject()
        return res

    def _compute_purchased_qty(self):
        for rec in self:
            rec.purchased_qty = 0.0
            for line in rec.purchase_lines.filtered(lambda x: x.state != "cancel"):
                if rec.product_uom_id and line.product_uom != rec.product_uom_id:
                    rec.purchased_qty += line.product_uom._compute_quantity(
                        line.product_qty, rec.product_uom_id
                    )
                else:
                    rec.purchased_qty += line.product_qty

    @api.depends("purchase_lines.state", "purchase_lines.order_id.state")
    def _compute_purchase_state(self):
        for rec in self:
            temp_purchase_state = False
            if rec.purchase_lines:
                if any(po_line.state == "done" for po_line in rec.purchase_lines):
                    temp_purchase_state = "done"
                elif all(po_line.state == "cancel" for po_line in rec.purchase_lines):
                    temp_purchase_state = "cancel"
                elif any(po_line.state == "purchase" for po_line in rec.purchase_lines):
                    temp_purchase_state = "purchase"
                elif any(
                    po_line.state == "to approve" for po_line in rec.purchase_lines
                ):
                    temp_purchase_state = "to approve"
                elif any(po_line.state == "sent" for po_line in rec.purchase_lines):
                    temp_purchase_state = "sent"
                elif all(
                    po_line.state in ("draft", "cancel")
                    for po_line in rec.purchase_lines
                ):
                    temp_purchase_state = "draft"
            rec.purchase_state = temp_purchase_state

    @api.model
    def _get_supplier_min_qty(self, product, partner_id=False):
        seller_min_qty = 0.0
        if partner_id:
            seller = product.seller_ids.filtered(lambda r: r.name == partner_id).sorted(
                key=lambda r: r.min_qty
            )
        else:
            seller = product.seller_ids.sorted(key=lambda r: r.min_qty)
        if seller:
            seller_min_qty = seller[0].min_qty
        return seller_min_qty

    @api.model
    def _calc_new_qty(self, request_line, po_line=None, new_pr_line=False):
        purchase_uom = po_line.product_uom or request_line.product_id.uom_po_id
        # TODO: Not implemented yet.
        #  Make sure we use the minimum quantity of the partner corresponding
        #  to the PO. This does not apply in case of dropshipping
        supplierinfo_min_qty = 0.0
        if not po_line.order_id.dest_address_id:
            supplierinfo_min_qty = self._get_supplier_min_qty(
                po_line.product_id, po_line.order_id.partner_id
            )

        rl_qty = 0.0
        # Recompute quantity by adding existing running procurements.
        if new_pr_line:
            rl_qty = po_line.product_uom_qty
        else:
            for prl in po_line.purchase_request_lines:
                for alloc in prl.purchase_request_allocation_ids:
                    rl_qty += alloc.product_uom_id._compute_quantity(
                        alloc.requested_product_uom_qty, purchase_uom
                    )
        qty = max(rl_qty, supplierinfo_min_qty)
        return qty

    def _can_be_deleted(self):
        self.ensure_one()
        return self.request_state == "draft"

    def unlink(self):
        if self.mapped("purchase_lines"):
            raise UserError(
                _("You cannot delete a record that refers to purchase lines!")
            )
        """ for line in self:
            if not line._can_be_deleted():
                raise UserError(
                    _(
                        "You can only delete a purchase request line "
                        "if the purchase request is in draft state."
                    )
                ) """
        return super(PurchaseRequestLine, self).unlink()

    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref("purchase_request.view_purchase_request_line_details")
        return {
            "name": _("Detailed Line"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "purchase.request.line",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
            "context": dict(
                self.env.context,
            ),
        }


class EmployeRequestLine(models.Model):

    _name = "employe.request.line"
    _description = "Employe Request Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Description", tracking=True)
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unite de Mesure",
        tracking=True,
    )
    product_qty = fields.Float(
        string="Quantity", tracking=True, digits="Product Unit of Measure"
    )
    request_id = fields.Many2one(
        comodel_name="employe.request",
        string="Employe Request",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="request_id.company_id",
        string="Company",
        store=True,
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        tracking=True,
    )
    analytic_tag_ids = fields.Many2many(
        "account.analytic.tag", string="Analytic Tags", tracking=True
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        related="request_id.requested_by",
        string="Requested by",
        store=True,
    )
    
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        related="request_id.assigned_to",
        string="Assigned to",
        store=True,
    )
    date_start = fields.Date(related="request_id.date_start", store=True)
    description = fields.Text(
        related="request_id.description",
        string="PR Description",
        store=True,
        readonly=False,
    )
    origin = fields.Char(
        related="request_id.origin", string="Source Document", store=True
    )
    date_required = fields.Date(
        string="Request Date",
        required=True,
        tracking=True,
        default=fields.Date.context_today,
    )
    is_purchase = fields.Boolean(string="A acheter")
    is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
    specifications = fields.Text()
    request_state = fields.Selection(
        string="Request state",
        related="request_id.state",
        store=True,
    )
    """ supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Preferred supplier",
        compute="_compute_supplier_id",
        compute_sudo=True,
        store=True,
    ) """
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Preferred supplier",
        compute_sudo=True,
        store=True,
    )
    cancelled = fields.Boolean(readonly=True, default=False, copy=False)

    

    line_cout_ids = fields.One2many(
        comodel_name="purchase.request.line.cout",
        inverse_name="employe_cout_id",
        string="Autres couts",
        readonly=False,
        copy=True,
        tracking=True,
    )

    orderpoint_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint", string="Orderpoint"
    )
   
    price_unit = fields.Float(string='Prix Unitaire', required=False, digits='Product Price')
    cout_total = fields.Float(
        string='Cout d\'achat',
        compute='_compute_cout_total',
        store=True,
        default=0.0
    )
    cout_lies = fields.Monetary(
        string='Couts lies',
        compute='_compute_cout_lies',
        store=True,
        default=0.0
    )
    estimated_cost = fields.Monetary(
        compute="_compute_amount",
        default=0.0,
        help="Estimated cost of Purchase Request Line, not propagated to PO.",
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain=[("purchase_ok", "=", True)],
        tracking=True,
    )
    repair_line_ids = fields.One2many('maintenance.request.line', 'invoice_line_id', readonly=True, copy=False)

    vehicule = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Moyen de transport",
        required=False,
        tracking=True,
    )

    
    def action_product_forecast_report(self):
        self.ensure_one()
        action = self.product_id.action_product_forecast_report()
        action['context'] = {
            'active_id': self.product_id.id,
            'active_model': 'product.product',
            'move_to_match_ids': self.ids,
        }
        """ if self.picking_type_id.code in self._consuming_picking_types():
            warehouse = self.location_id.warehouse_id
        else:
            warehouse = self.location_dest_id.warehouse_id

        if warehouse: 
            action['context']['warehouse'] = warehouse.id"""
        return action
    
    @api.depends(
        "product_id",
        "name",
        "product_uom_id",
        "product_qty",
        "analytic_account_id",
        "date_required",
        "specifications",
        
    )
    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ("approved", "rejected", "done","stock", "po_ro", "paye"):
                rec.is_editable = False
            else:
                rec.is_editable = True
        
    
    @api.depends('product_id')
    def _compute_prix_unitaire(self):
        for line in self:
            line.price_unit = line.product_id.standard_price

    @api.depends("product_id", "product_id.seller_ids")
    def _compute_supplier_id(self):
        for rec in self:
            sellers = rec.product_id.seller_ids.filtered(
                lambda si: not si.company_id or si.company_id == rec.company_id
            )
            rec.supplier_id = sellers[0].name if sellers else False

    """ @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = "[{}] {}".format(self.product_id.code, name)
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name """
    
    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = "[{}] {}".format(self.product_id.code, name)
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name
            sellers = self.product_id.seller_ids
            self.supplier_id = sellers[0].name if sellers else False
            self.price_unit = sellers[0].price if sellers else False
    @api.onchange("supplier_id", "product_id")
    def onchange_supplier_id(self):
        if self.supplier_id:
            
            sellers = self.product_id.seller_ids 
            if sellers:
                for seller in sellers:
                    if self.supplier_id == seller.name:

                        self.price_unit = seller.price
    @api.depends('product_qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.update({
                'estimated_cost' : line.product_qty * line.price_unit
            })
    @api.depends("line_cout_ids")
    def _compute_cout_lies(self):
        for rec in self:
            cout_t = 0.0
            for line in rec.line_cout_ids:
                cout_t += line.cout
            self.cout_lies = cout_t
    
    @api.depends('estimated_cost', 'line_cout_ids')
    def _compute_cout_total(self):
        for main in self:
            print ("DEMANDE:",main.estimated_cost)
            cout_t = 0.0
            for line in main.line_cout_ids:
                cout_t += line.cout
            self.cout_total = cout_t + main.estimated_cost
           
    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({"cancelled": True})

    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({"cancelled": False})

    def write(self, vals):
        res = super(EmployeRequestLine, self).write(vals)
        if vals.get("cancelled"):
            requests = self.mapped("request_id")
            requests.check_auto_reject()
        return res

    def _compute_purchased_qty(self):
        for rec in self:
            rec.purchased_qty = 0.0
            for line in rec.purchase_lines.filtered(lambda x: x.state != "cancel"):
                if rec.product_uom_id and line.product_uom != rec.product_uom_id:
                    rec.purchased_qty += line.product_uom._compute_quantity(
                        line.product_qty, rec.product_uom_id
                    )
                else:
                    rec.purchased_qty += line.product_qty

    @api.depends("purchase_lines.state", "purchase_lines.order_id.state")
    def _compute_purchase_state(self):
        for rec in self:
            temp_purchase_state = False
            if rec.purchase_lines:
                if any(po_line.state == "done" for po_line in rec.purchase_lines):
                    temp_purchase_state = "done"
                elif all(po_line.state == "cancel" for po_line in rec.purchase_lines):
                    temp_purchase_state = "cancel"
                elif any(po_line.state == "purchase" for po_line in rec.purchase_lines):
                    temp_purchase_state = "purchase"
                elif any(
                    po_line.state == "to approve" for po_line in rec.purchase_lines
                ):
                    temp_purchase_state = "to approve"
                elif any(po_line.state == "sent" for po_line in rec.purchase_lines):
                    temp_purchase_state = "sent"
                elif all(
                    po_line.state in ("draft", "cancel")
                    for po_line in rec.purchase_lines
                ):
                    temp_purchase_state = "draft"
            rec.purchase_state = temp_purchase_state

   

    def unlink(self):
        if self.mapped("purchase_lines"):
            raise UserError(
                _("You cannot delete a record that refers to purchase lines!")
            )
        """ for line in self:
            if not line._can_be_deleted():
                raise UserError(
                    _(
                        "You can only delete a purchase request line "
                        "if the purchase request is in draft state."
                    )
                ) """
        return super(PurchaseRequestLine, self).unlink()

    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref("purchase_request.view_purchase_request_line_details")
        return {
            "name": _("Detailed Line"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "purchase.request.line",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
            "context": dict(
                self.env.context,
            ),
        }
