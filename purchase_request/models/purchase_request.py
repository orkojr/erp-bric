# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import datetime

_STATES = [
    ("draft", "Bon de commande Interne"),
    ("soumettre", "Soumis"),
    ("to_approve", "Demande Achat"),
    ("approved", "Approved"),
    ("approved_direction", "Validation de la direction"),
    ("rejected", "Rejected"),
    ("stock", "En Stock"),
    ("paye", "Paid"),
]
_OBJET = [
    ("appro_mp", "Approvisionnement MP"),
    ("appro", "Autres Approvisionnements"),
    ("distrib", "Distribution"),
    ("admin", "Administration"),
    ("prod", "Production"),
    ("maint", "Maintenance"),
    ("projet", "Chantier"),
]

_MODE = [
    ("bank", "Banque"),
    ("caisse", "Caisse"),

]

_STATES1 = [
    ("draft", "Bon de commande Interne"),
    ("soumettre", "Soumis"),
    ("to_approve", "A approuver "),
    ("approved", "Approbation du RA"),
    ("approved_direction", "Validation de la direction"),
    ("rejected", "Rejeté"),
    ("stock", "En Stock"),
    ("paye", "Payé"),
]
class request_motif(models.Model):

    _name = "request.motif"
    _rec_name = "name"

		
    name = fields.Char(string='Nom', required=True)
    description = fields.Char(string='Description')

class purchase_location(models.Model):

    _name = "purchase.location"
    _rec_name = "name"

		
    name = fields.Char(string='Nom', required=True)
    description = fields.Char(string='Description')

class PurchaseRequest(models.Model):

    _name = "purchase.request"
    _description = "Purchase Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("purchase.request")

    @api.model
    def _default_picking_type(self):
        type_obj = self.env["stock.picking.type"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        types = type_obj.search(
            [("code", "=", "incoming"), ("warehouse_id.company_id", "=", company_id)]
        )
        if not types:
            types = type_obj.search(
                [("code", "=", "incoming"), ("warehouse_id", "=", False)]
            )
        return types[:1]

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("approved", "rejected", "approved_direction"):
                rec.is_editable = False
            else:
                rec.is_editable = True

    name = fields.Char(
        string="Request Reference",
        required=True,
        default=lambda self: _("New"),
        tracking=True,
        readonly=True,
    )
    is_name_editable = fields.Boolean(
        default=lambda self: self.env.user.has_group("base.group_no_one"),
    )
    origin = fields.Char(string="Source Document")
    date_start = fields.Date(
        string="Creation date",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        tracking=True,
    )
    date_demande_autorisation = fields.Date(
        string="Date de demande d'autorisation",
        help="Date when the user initiated the request.",
        
        tracking=True,
    )
    date_approbation = fields.Date(
        string="Date Approbation",
        help="Date when the user initiated the request.",
       
        tracking=True,
    )
    date_validation = fields.Date(
        string="Date de validation de la direction",
        help="Date when the user initiated the request.",
        
        tracking=True,
    )
    date_paiement = fields.Date(
        string="Date de Paiement",
        help="Date when the user initiated the request.",
        
        tracking=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        required=True,
        copy=False,
        tracking=True,
        default=_get_default_requested_by,string="Demande interne de",
        index=True,
    )
    service_id = fields.Many2one(
        'hr.department', 
        'Service Beneficiaire', 
        
    )
    service_demandeur_id = fields.Many2one(
        'hr.department', 
        'Service', 
        required=True,
    )
    chantier_id = fields.Many2one(
        'project.project', 'Chantier affecte')
    motif = fields.Many2one(
        'request.motif', 
        'Raison', 
        
    )
    motif_achat = fields.Many2one(
        'account.budget.post', 
        'Motif', required=True
        
    )
    lieu = fields.Many2one(
        'purchase.location', 
        'Lieu Achat', 
        
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
        string="Approver",
        tracking=True,
        
        domain=lambda self: [
            (
                "groups_id",
                "in",
                self.env.ref("purchase_request.group_purchase_request_manager").id,
            )
        ],
        index=True,
    )
    description = fields.Text()
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=False,
        default=_company_get,
        tracking=True,
    )
    line_ids = fields.One2many(
        comodel_name="purchase.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
        tracking=True,
    )
    
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="line_ids.product_id",
        string="Product",
        readonly=True,
    )
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )
    objet = fields.Selection(
        selection=_OBJET,
        string="Objet",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="appro",
    )
    mode_payment = fields.Selection(
        selection=_MODE,
        string="Mode de paiement",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="caisse",
    )
    is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
    is_administration = fields.Boolean(string="Administration", default = False, readonly=True)
    to_approve_allowed = fields.Boolean(compute="_compute_to_approve_allowed")
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="livrer à",
        
        default=_default_picking_type,
    )
    group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Procurement Group",
        copy=False,
        index=True,
    )
    line_count = fields.Integer(
        string="Purchase Request Line count",
        compute="_compute_line_count",
        readonly=True,
    )
    move_count = fields.Integer(
        string="Stock Move count", compute="_compute_move_count", readonly=True
    )
    purchase_count = fields.Integer(
        string="Purchases count", compute="_compute_purchase_count", readonly=True
    )
    invoice_count = fields.Integer(
        string="Invoices count", compute="_compute_invoice_count", readonly=True
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    estimated_cost = fields.Monetary(
        compute="_compute_estimated_cost",
        string="Total Estimated Cost",
        store=True,
    )
    emplo_req_ids = fields.Many2one("employe.request", string='Demande interne', copy=False)
    
    #repair_ids = fields.One2many('maintenance.request', 'purchase_id', readonly=True, copy=False)
    @api.onchange('requested_by')
    def onchange_requested_by(self):
        department_id = self.requested_by.employee_id.department_id.id
        return {'value': {'service_demandeur_id': department_id}}
        
    @api.depends("line_ids", "line_ids.line_cout_ids")
    def _compute_estimated_cost(self):
        for rec in self:
            cout =0
            for line in rec.line_ids:
                print("COUTS LIES", line.cout_lies)
                #cout += line.estimated_cost
                cout_lies =0
                for lin in line.line_cout_ids:
                    cout_lies += cout_lies + lin.cout
                cout += line.estimated_cost + cout_lies
            self.estimated_cost = cout 
            #rec.estimated_cost = sum(rec.line_ids.mapped("cout_total"))

    @api.depends("line_ids")
    def _compute_purchase_count(self):
        for rec in self:
            rec.purchase_count = len(rec.mapped("line_ids.purchase_lines.order_id"))
    
    @api.depends("line_ids")
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.mapped("line_ids"))

    def action_view_purchase_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        lines = self.mapped("line_ids.purchase_lines.order_id")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action
    
    def action_view_account_move(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_receipt_type")
        lines = self.mapped("line_ids.invoice_lines.move_id")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("account.view_move_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_move_count(self):
        for rec in self:
            rec.move_count = len(
                rec.mapped("line_ids.purchase_request_allocation_ids.stock_move_id")
            )

    def action_view_stock_picking(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        # remove default filters
        action["context"] = {}
        lines = self.mapped(
            "line_ids.purchase_request_allocation_ids.stock_move_id.picking_id"
        )
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.mapped("line_ids"))

    def action_view_purchase_request_line(self):
        action = (
            self.env.ref("purchase_request.purchase_request_line_form_action")
            .sudo()
            .read()[0]
        )
        lines = self.mapped("line_ids")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase_request.purchase_request_line_form").id, "form")
            ]
            action["res_id"] = lines.ids[0]
        return action

    @api.depends("state", "line_ids.product_qty", "line_ids.cancelled")
    def _compute_to_approve_allowed(self):
        for rec in self:
            
            status = rec.state == "soumettre" and any(
                not line.cancelled and line.product_qty for line in rec.line_ids
            )
            rec.to_approve_allowed = status
            
    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({"state": "draft", "name": self._get_default_name()})
        return super(PurchaseRequest, self).copy(default)

    @api.model
    def _get_partner_id(self, request):
        user_id = request.assigned_to or self.env.user
        return user_id.partner_id.id

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._get_default_name()
        request = super(PurchaseRequest, self).create(vals)
        if vals.get("assigned_to"):
            partner_id = self._get_partner_id(request)
            request.message_subscribe(partner_ids=[partner_id])
        return request

    def write(self, vals):
        res = super(PurchaseRequest, self).write(vals)
        for request in self:
            if vals.get("assigned_to"):
                partner_id = self._get_partner_id(request)
                request.message_subscribe(partner_ids=[partner_id])
        return res

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a purchase request which is not draft.")
                )
        return super(PurchaseRequest, self).unlink()

    def button_draft(self):
        self.mapped("line_ids").do_uncancel()
        if self.state == 'approved':
            return self.write({"state": "to_approve"})
        else:
            return self.write({"state": "approved"})
    def button_submit(self):
        
        return self.write({"state": "soumettre"})

    def button_to_approve(self):
        self.to_approve_allowed_check()
        #default=fields.Date.context_today,
        return self.write({"state": "to_approve", "date_demande_autorisation": fields.Date.today()})

    def button_stock(self):
        
        return self.write({"state": "stock"})

    def button_approved(self):
        if self.objet == "appro_mp":
            """ for line in self.line_ids:
                if len(line.line_cout_ids) == 0:
                     raise UserError(
                    _(
                        "Svp Veuillez renseigner les couts lies a l'achat de la Matiere Premiere"
                        "Cliquez sur le bouton :Autres couts lies"
                    )
                )     """ 
        requete = self.env["employe.request"].search([("purchase_ids", "=", self.id)])
        requete.write({"state":"approved"})
        return self.write({"state": "approved", "date_approbation": fields.Date.today()})

    def button_rejected(self):
        self.mapped("line_ids").do_cancel()
        return self.write({"state": "rejected"})

    @api.model
    def _prepare_purchase_order(self, supplier_id, picking_type, group_id, company):
        if not supplier_id:
            raise UserError(_("Renseigner le fournisseur. Cependant si un fournisseur n'est pas connu. Veuillez indiquer sur l'article!"))
        
        data = {
            "partner_id": supplier_id.id,
            "fiscal_position_id": supplier_id.property_account_position_id
            and supplier_id.property_account_position_id.id
            or False,
            "picking_type_id": picking_type.id,
            "company_id": company.id,
            "group_id": group_id.id,
            "state":'purchase',
            "purchase_request": self.id,
            "mode_payment": self.mode_payment,

        }

        
        return data
    @api.model
    def _prepare_purchase_order_line(self, po, item):
        if not item.product_id:
            raise UserError(_("Please select a product for all lines"))
        product = item.product_id

        
        qty = item.product_qty
        # Suggest the supplier min qty as it's done in Odoo core
        #min_qty = item._get_supplier_min_qty(product, po.partner_id)
        #qty = max(qty, min_qty)
        date_required = item.date_required
        vals = {
            "name": product.name,
            "order_id": po.id,
            "product_id": product.id,
            "product_uom": item.product_uom_id.id,
            "price_unit": item.price_unit,
            "product_qty": qty,
            "account_analytic_id": item.analytic_account_id.id,
            "purchase_request_lines": [(4, item.id)],
            "date_planned": datetime(
                date_required.year, date_required.month, date_required.day
            ),
            "move_dest_ids": [(4, x.id) for x in item.move_dest_ids],
        }
        print ("Tableau de valeurs",vals)
        if item.analytic_tag_ids:
            vals["analytic_tag_ids"] = [
                (4, ati) for ati in item.analytic_tag_ids.ids
            ]
        #self._execute_purchase_line_onchange(vals)
        return vals

    @api.model
    def _prepare_account_move(self):
        move_type = self._context.get('default_move_type', 'in_receipt')    
        
        data = {
               
            'move_type': move_type,
            'company_id': self.company_id,
            'invoice_line_ids': [],
            'purchase_request': self,
            
        }
        return data
    @api.model
    def _prepare_account_move_line(self, item, move=False):
        if not item.product_id:
            raise UserError(_("Please select a product for all lines"))
        product = item.product_id

        
        date_required = item.date_required
        vals = {
            "name": product.name,
            
            "product_id": product.id,
            "product_uom_id": product.uom_po_id.id or product.uom_id.id,
            "price_unit": item.price_unit,
            "quantity": item.product_qty,
            "account_id": product.property_account_expense_id.id,
       
        }
     
        return vals
    def make_purchase_order(self):
        res = []
        purchase_obj = self.env["purchase.order"]
        po_line_obj = self.env["purchase.order.line"]
        pr_line_obj = self.env["purchase.request.line"]
        move_obj = self.env["account.move"]
        move_line_obj = self.env["account.move.line"]
        purchase = False
        compteur = 0
        supplier = []
        item_tab = []
        invoice_vals_list = []
        print ("TABLEAU FOURNISSEUR",supplier)
        for item in self.line_ids:
            if item.supplier_id:
                if item.supplier_id not in supplier:
                    supplier.append(item.supplier_id)
            else: 
                if item.is_recu == False:
                    raise UserError(_("Veuillez preciser si il y'a pas de fournisseur pour cette demande"))
                else:
                    item_tab.append(item)
        if len(item_tab) != 0:

            po_data = self._prepare_account_move()
            for item_line in item_tab:
            #line = item.line_id
                if item_line.product_qty <= 0.0:
                    raise UserError(_("Enter a positive quantity."))
            
                # ENLEVER LA GENERATION DES ECRITURES COMPTABLES

                po_data['invoice_line_ids'].append((0, 0, self._prepare_account_move_line(item_line)))
                #item.request_id.write({"state": "po_ro"})
                #po_line_data = self._prepare_account_move_line(purchase, item)
            invoice_vals_list.append(po_data)  
            moves = self.env['account.move']
            AccountMove = self.env['account.move'].with_context(default_move_type='in_receipt')
            for vals in invoice_vals_list:
                moves |= AccountMove.with_company(vals['company_id']).create(vals)
           
        print ("TABLEAU FOURNISSEUR",supplier)
        for sup in supplier:
            line_ids = pr_line_obj.search([("supplier_id", "=", sup.id),("request_id", "=", self.id),("purchase_state", "=", 'draft')])
            if line_ids:
                purchase = line_ids[0].purchase_lines[0].order_id
                print ("PO",purchase)
            else:
                purchase = False
            
            if not purchase:
                print ("TABLEAU 1111")
                po_data = self._prepare_purchase_order(
                        sup,
                        self.picking_type_id,
                        self.group_id,
                        self.company_id
                        )
                purchase = purchase_obj.create(po_data)
                line_ids = pr_line_obj.search([("supplier_id", "=", sup.id),("request_id", "=", self.id)])
                for item in line_ids:
                    #line = item.line_id
                    if item.product_qty <= 0.0:
                        raise UserError(_("Enter a positive quantity."))
                    """ if self.purchase_count !=0:
                        purchase =self.purchase_order_id """ 
                    
                
                    
                    po_line_data = self._prepare_purchase_order_line(purchase, item)
                    print ("TABLEAU",po_line_data)
                    new_pr_line = True
                    """ if item.keep_description:
                        po_line_data["name"] = item.name """
                    po_line = po_line_obj.create(po_line_data)
                    """ print ("TABLEAU",po_line.price_unit)
                    new_qty = pr_line_obj._calc_new_qty(
                        line, po_line=po_line, new_pr_line=new_pr_line
                    )
                    print ("TABLEAU****",po_line.price_unit)
                    po_line.product_qty = new_qty
                    print ("TABLEAU****",po_line.price_unit) """
                    #po_line._onchange_quantity()
                    # The onchange quantity is altering the scheduled date of the PO
                    # lines. We do not want that:
                    print ("TABLEAU****",po_line.price_unit)
                    date_required = item.date_required
                    po_line.date_planned = datetime(
                        date_required.year, date_required.month, date_required.day
                    )
                    res.append(purchase.id)
            else:
                for item in line_ids:

                    #line = item.line_id
                    if item.product_qty <= 0.0:
                        raise UserError(_("Enter a positive quantity."))
                    """ if self.purchase_count !=0:
                        purchase =self.purchase_order_id """ 
                    
                    if item.purchase_state == 'draft':
                        line_ids = po_line_obj.search([("order_id", "=", purchase.id),("product_id", "=", item.product_id.id)])
                        if line_ids:
                            line_ids[0].write({"product_qty": item.product_qty,"price_unit": item.price_unit})
                    else:
                        po_line_data = self._prepare_purchase_order_line(purchase, item)
                        print ("TABLEAU",po_line_data)
                        new_pr_line = True
                        """ if item.keep_description:
                            po_line_data["name"] = item.name """
                        po_line = po_line_obj.create(po_line_data)
                        """ print ("TABLEAU",po_line.price_unit)
                        new_qty = pr_line_obj._calc_new_qty(
                            line, po_line=po_line, new_pr_line=new_pr_line
                        )
                        print ("TABLEAU****",po_line.price_unit)
                        po_line.product_qty = new_qty
                        print ("TABLEAU****",po_line.price_unit) """
                        #po_line._onchange_quantity()
                        # The onchange quantity is altering the scheduled date of the PO
                        # lines. We do not want that:
                        print ("TABLEAU****",po_line.price_unit)
                        date_required = item.date_required
                        po_line.date_planned = datetime(
                            date_required.year, date_required.month, date_required.day
                        )
                        res.append(purchase.id)

        return {
            "domain": [("id", "in", res)],
            "name": _("RFQ"),
            "view_mode": "tree,form",
            "res_model": "purchase.order",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }
    def button_done(self):
        self.write({"state": "approved_direction"})
        requete = self.env["employe.request"].search([("purchase_ids", "=", self.id)])
        requete.write({"state":"approved_direction"})
        self.make_purchase_order()

        

    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({"state": "rejected"})

    def to_approve_allowed_check(self):
        for rec in self:
            if rec.to_approve_allowed==False:
                raise UserError(
                    _(
                        "You can't request an approval for a purchase request "
                        "which is empty. (%s)"
                    )
                    % rec.name
                )

class PurchaseAccountMove(models.Model):
    _inherit = "account.move"
    employe_request = fields.Many2one(comodel_name="employe.request", readonly=True, copy=False, string="Demande interne")    
    purchase_request = fields.Many2one(comodel_name="purchase.request", readonly=True, copy=False, string="Demande d'achat")    
    group_ligne = fields.Boolean(string="Grouper les lignes de depenses")

class PurchaseARequest(models.Model):
    _inherit = "purchase.request"

    motif = fields.Many2one(
        'request.motif', 
        'Raison', 
        
    )

class EmployeRequest(models.Model):

    _name = "employe.request"
    _description = "Employee Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("purchase.request")

    """ @api.model
    def _default_picking_type(self):
        type_obj = self.env["stock.picking.type"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        types = type_obj.search(
            [("code", "=", "incoming"), ("warehouse_id.company_id", "=", company_id)]
        )
        if not types:
            types = type_obj.search(
                [("code", "=", "incoming"), ("warehouse_id", "=", False)]
            )
        return types[:1] """

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("soumettre", "to_approve", "approved", "approved_direction", "rejected", "stock", "paid"):
                rec.is_editable = False
            else:
                rec.is_editable = True

    name = fields.Char(
        string="Reference",
        
        readonly=True,
    )
    is_name_editable = fields.Boolean(
        default=lambda self: self.env.user.has_group("base.group_no_one"),
    )
    origin = fields.Char(string="Source Document")
    date_start = fields.Date(
        string="Date de creation",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        tracking=True,
    )
    date_demande_autorisation = fields.Date(
        string="Date de soumission",
        help="Date when the user initiated the request.",
        
        tracking=True,
    )
    date_approbation = fields.Date(
        string="Date Approbation",
        help="Date when the user initiated the request.",
       
        tracking=True,
    )
    date_validation = fields.Date(
        string="Date de validation de la direction",
        help="Date when the user initiated the request.",
        
        tracking=True,
    )
    date_paiement = fields.Date(
        string="Date de Paiement",
        help="Date when the user initiated the request.",
        
        tracking=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        required=True,
        copy=False,
        tracking=True,
        readonly=True,
        default=_get_default_requested_by,string="Demande par",
        index=True,
    )
    service_id = fields.Many2one(
        'hr.department', 
        'Service Beneficiaire', 
        required=True,
    )
    service_demandeur_id = fields.Many2one(
        'hr.department', 
        'Service', 
        readonly=True,
        required=True,
    )
    chantier_id = fields.Many2one(
        'project.project', 'Chantier affecte')
    
    motif_achat = fields.Many2one(
        'account.budget.post', 
        'Motif'
        
    )
   
    
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Approbateur",
        tracking=True,
        
        domain=lambda self: [
            (
                "groups_id",
                "in",
                self.env.ref("purchase_request.group_employe_request_manager").id,
            )
        ],
        index=True,
    )
    description = fields.Text()
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=False,
        default=_company_get,
        tracking=True,
    )
    line_ids = fields.One2many(
        comodel_name="employe.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
        tracking=True,
    )
    
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="line_ids.product_id",
        string="Product",
        readonly=True,
    )
    state = fields.Selection(
        selection=_STATES1,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )
    objet = fields.Selection(
        selection=_OBJET,
        string="Objet",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="appro",
    )
    is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
    to_approve_allowed = fields.Boolean(compute="_compute_to_approve_allowed")
    is_administration = fields.Boolean(string="Depenses Administratives", default = False)
    
    is_enlevement = fields.Boolean(string="Enlèvement MP", default = False)
    commande_id = fields.Many2one("purchase.order", string='Bon de commande', copy=False)
    purchase_count = fields.Integer(
        string="Purchases count", compute="_compute_purchase_count", readonly=True
    )
    
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    estimated_cost = fields.Monetary(
        compute="_compute_estimated_cost",
        string="Total Estimated Cost",
        store=True,
    )
    purchase_ids = fields.Many2one("purchase.request", string='Demande dachat', copy=False)
    purchase_request_count = fields.Integer(compute='_get_charged')
    
    @api.depends('purchase_ids')
    def _get_charged(self):
        
        for order in self:
            
            order.purchase_request_count = len(order.purchase_ids)

    #repair_ids = fields.One2many('maintenance.request', 'purchase_id', readonly=True, copy=False)
    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)
    
    @api.onchange('requested_by')
    def onchange_requested_by(self):
        department_id = self.requested_by.employee_id.department_id.id
        return {'value': {'service_demandeur_id': department_id}}
        
    @api.depends("line_ids", "line_ids.line_cout_ids")
    def _compute_estimated_cost(self):
        for rec in self:
            cout =0
            for line in rec.line_ids:
                print("COUTS LIES", line.cout_lies)
                #cout += line.estimated_cost
                cout_lies =0
                for lin in line.line_cout_ids:
                    cout_lies += cout_lies + lin.cout
                cout += line.estimated_cost + cout_lies
            self.estimated_cost = cout 
            #rec.estimated_cost = sum(rec.line_ids.mapped("cout_total"))

    @api.depends("line_ids")
    def _compute_purchase_count(self):
        for rec in self:
            rec.purchase_count = len(rec.mapped("line_ids.purchase_lines.order_id"))
    
    @api.depends("line_ids")
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.mapped("line_ids"))

    def action_view_purchase_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("purchase_request.purchase_request_form_action")
        requests = self.purchase_ids
        print ('CHARGEMENT:',requests)
        action = self.env["ir.actions.actions"]._for_xml_id("purchase_request.purchase_request_form_action")
        if len(requests) > 1:
            action['domain'] = [('id', 'in', requests.ids)]
        elif len(requests) == 1:
        
            form_view = [(self.env.ref('purchase_request.view_purchase_request_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = requests.id
        return action
    
    def action_view_account_move(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_receipt_type")
        lines = self.mapped("line_ids.invoice_lines.move_id")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("account.view_move_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_move_count(self):
        for rec in self:
            rec.move_count = len(
                rec.mapped("line_ids.purchase_request_allocation_ids.stock_move_id")
            )

    def action_view_stock_picking(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        # remove default filters
        action["context"] = {}
        lines = self.mapped(
            "line_ids.purchase_request_allocation_ids.stock_move_id.picking_id"
        )
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.mapped("line_ids"))

    def action_view_purchase_request_line(self):
        action = (
            self.env.ref("purchase_request.purchase_request_line_form_action")
            .sudo()
            .read()[0]
        )
        lines = self.mapped("line_ids")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase_request.purchase_request_line_form").id, "form")
            ]
            action["res_id"] = lines.ids[0]
        return action

    @api.depends("state", "line_ids.product_qty", "line_ids.cancelled")
    def _compute_to_approve_allowed(self):
        for rec in self:
            
            status = rec.state == "soumettre" and any(
                not line.cancelled and line.product_qty for line in rec.line_ids
            )
            rec.to_approve_allowed = status
            
    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({"state": "draft", "name": self._get_default_name()})
        return super(EmployeRequest, self).copy(default)

    @api.model
    def _get_partner_id(self, request):
        user_id = request.assigned_to or self.env.user
        return user_id.partner_id.id

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self._get_default_name()
        request = super(EmployeRequest, self).create(vals)
        if vals.get("assigned_to"):
            partner_id = self._get_partner_id(request)
            request.message_subscribe(partner_ids=[partner_id])
        return request

    def write(self, vals):
        res = super(EmployeRequest, self).write(vals)
        """ for request in self:
            if vals.get("assigned_to"):
                partner_id = self._get_partner_id(request)
                request.message_subscribe(partner_ids=[partner_id]) """
        return res 

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a purchase request which is not draft.")
                )
        return super(EmployeRequest, self).unlink()

    def button_draft(self):
        self.mapped("line_ids").do_uncancel()
        return self.write({"state": "draft"})
    def button_submit(self):
        for line in self.line_ids:
                if line.product_id.suivi_vehicule == True:
                    if not line.vehicule:
                        raise UserError(_("Veuillez renseigner le vehicule."))
        
        return self.write({"state": "soumettre", "date_demande_autorisation": fields.Date.today()})
    
    def button_submit_admin(self):
        for line in self.line_ids:
                if line.product_id.suivi_vehicule == True:
                    if not line.vehicule:
                        raise UserError(_("Veuillez renseigner le vehicule."))
        
        return self.write({"state": "soumettre", "date_demande_autorisation": fields.Date.today()})
    def button_to_approve(self):
        self.to_approve_allowed_check()
        self.make_purchase_request()
        return self.write({"state": "to_approve", "date_demande_autorisation": fields.Date.today()})

    def button_stock(self):
        
        return self.write({"state": "stock"})

    def button_approved(self):
        return self.write({"state": "approved", "date_approbation": fields.Date.today()})

    def button_rejected(self):
        self.mapped("line_ids").do_cancel()
        return self.write({"state": "rejected"})

    
    def _prepare_purchase_request(self, request_by, service_id, service_demandeur, objet, description):
     
        
        data = {
            "requested_by": request_by.id,
            "service_id": service_id.id,
            "service_demandeur_id": service_demandeur.id,
            "objet": objet,
            "description":description,
            "state":'to_approve',
            "emplo_req_ids": self.id,
            "assigned_to": self.assigned_to.id,


        }
        return data
   
    def _prepare_purchase_request_line(self, po, item):
        if not item.product_id:
            raise UserError(_("Please select a product for all lines"))
        product = item.product_id

        qty = item.product_qty
        
        vals = {
            "name": item.name,
            "request_id": po.id,
            "product_id": product.id,
            "product_uom_id": item.product_uom_id.id,
            
            "product_qty": qty,
            "vehicule": item.vehicule.id,
            
            
        }
        print ("Tableau de valeurs",vals)
        
        return vals


    def make_purchase_request(self):
        res = []
        purchase_obj = self.env["purchase.request"]
        po_line_obj = self.env["purchase.order.line"]
        pr_line_obj = self.env["purchase.request.line"]
        purchase = False
        compteur = 0
        supplier = []
        #print ("TABLEAU FOURNISSEUR",supplier)
        #request_by = self.env["res.users"].browse(self.env.uid)
        request_by = self.requested_by
        print ("TABLEAU FOURNISSEUR",request_by)
        service = request_by.employee_id.department_id
        service_beneficiaire = self.service_id
        objet = self.objet
        description = self.description
        po_data = self._prepare_purchase_request(
                request_by,
                service_beneficiaire,
                service,
                objet,
                description
                )
        purchase = purchase_obj.create(po_data)
        
        for item in self.line_ids:
            #line = item.line_id
            if item.is_purchase == True:
              
        
            
                po_line_data = self._prepare_purchase_request_line(purchase, item)
                
                po_line = pr_line_obj.create(po_line_data)
            
            
            res.append(purchase.id)
           
        self.purchase_ids=purchase.id
            
            

            

        #line.request_id.write({"state": "po_ro"})
        return {
            "domain": [("id", "in", res)],
            "name": _("Demande d'achat"),
            "view_mode": "tree,form",
            "res_model": "purchase.request",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }

    def make_purchase_request_admin(self):
        res = []
        purchase_obj = self.env["purchase.request"]
        po_line_obj = self.env["purchase.order.line"]
        pr_line_obj = self.env["purchase.request.line"]
        purchase = False
        compteur = 0
        supplier = []
        #print ("TABLEAU FOURNISSEUR",supplier)
        #request_by = self.env["res.users"].browse(self.env.uid)
        request_by = self.requested_by
        print ("TABLEAU FOURNISSEUR",request_by)
        service = request_by.employee_id.department_id
        service_beneficiaire = self.service_id
        objet = self.objet
        description = self.description
        po_data = self._prepare_purchase_request(
                request_by,
                service_beneficiaire,
                service,
                objet,
                description
                )
        purchase = purchase_obj.create(po_data)
        purchase.write({"is_administration":True})
        for item in self.line_ids:
            po_line_data = self._prepare_purchase_request_line(purchase, item)
            
            po_line = pr_line_obj.create(po_line_data)
        
            
            res.append(purchase.id)
           
        self.purchase_ids=purchase.id
            
            

            

        #line.request_id.write({"state": "po_ro"})
        return {
            "domain": [("id", "in", res)],
            "name": _("Demande d'achat"),
            "view_mode": "tree,form",
            "res_model": "purchase.request",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }

    @api.model
    def _prepare_account_move(self):
        move_type = self._context.get('default_move_type', 'in_receipt')    
        
        data = {
               
            'move_type': move_type,
            'company_id': self.company_id,
            'invoice_line_ids': [],
            'employe_request': self,
            
        }
        return data
    @api.model
    def _prepare_account_move_line(self, item, move=False):
        if not item.product_id:
            raise UserError(_("Please select a product for all lines"))
        product = item.product_id

        
        date_required = item.date_required
        vals = {
            "name": product.name,
            
            "product_id": product.id,
            "product_uom_id": product.uom_po_id.id or product.uom_id.id,
            "price_unit": item.price_unit,
            "quantity": item.product_qty,
            "account_id": product.property_account_expense_id.id,
       
        }
     
        return vals

    def make_purchase_order(self):
        res = []
        purchase_obj = self.env["purchase.order"]
        po_line_obj = self.env["purchase.order.line"]
        pr_line_obj = self.env["purchase.request.line"]
        move_obj = self.env["account.move"]
        move_line_obj = self.env["account.move.line"]
        purchase = False
        compteur = 0
        supplier = []
        item_tab = []
        invoice_vals_list = []
        print ("TABLEAU FOURNISSEUR",supplier)
        po_data = self._prepare_account_move()
        for item in self.line_ids:
            if item.supplier_id:
                if item.supplier_id not in supplier:
                    supplier.append(item.supplier_id)
            

            
            
            if item.product_qty <= 0.0:
                raise UserError(_("Enter a positive quantity."))
        
            # ENLEVER LA GENERATION DES ECRITURES COMPTABLES

            po_data['invoice_line_ids'].append((0, 0, self._prepare_account_move_line(item)))
            #item.request_id.write({"state": "po_ro"})
            #po_line_data = self._prepare_account_move_line(purchase, item)
        invoice_vals_list.append(po_data)  
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_receipt')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)
        res.append(moves.id)
        return {
            "domain": [("id", "in", res)],
            "name": _("RFQ"),
            "view_mode": "tree,form",
            "res_model": "account.move",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }
    def button_done(self):
        self.write({"state": "approved_direction"})
        
        self.make_purchase_order()

        

    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({"state": "rejected"})

    def to_approve_allowed_check(self):
        for rec in self:
            if rec.line_ids:
                i=0
                for line in rec.line_ids:
                    if line.is_purchase:
                        i = i+1
                    
                if i==0:
                    raise UserError(
                    _(
                        "Veuillez preciser quel article a acheter")
                
                )
            if rec.to_approve_allowed==False:
                raise UserError(
                    _(
                        "You can't request an approval for a purchase request "
                        "which is empty. (%s)"
                    )
                    % rec.name
                )