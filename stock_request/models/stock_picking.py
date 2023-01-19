# Copyright 2017-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    stock_request_ids = fields.One2many(
        comodel_name="stock.request",
        string="Stock Requests",
        compute="_compute_stock_request_ids",
    )
    stock_request_count = fields.Integer(
        "Stock Request #", compute="_compute_stock_request_ids"
    )
    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        
        tracking=True,
        
    )
    @api.depends("move_lines")
    def _compute_stock_request_ids(self):
        for rec in self:
            rec.stock_request_ids = rec.move_lines.mapped("stock_request_ids")
            rec.stock_request_count = len(rec.stock_request_ids)

    def action_view_stock_request(self):
        """
        :return dict: dictionary value for created view
        """
        action = self.env.ref("stock_request.action_stock_request_form").read()[0]

        requests = self.mapped("stock_request_ids")
        if len(requests) > 1:
            action["domain"] = [("id", "in", requests.ids)]
        elif requests:
            action["views"] = [
                (self.env.ref("stock_request.view_stock_request_form").id, "form")
            ]
            action["res_id"] = requests.id
        return action

    
    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:

            res = self.env['ir.actions.act_window']._for_xml_id('fleet.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.vehicle_id.id, group_by=False),
                domain=[('vehicle_id', '=', self.vehicle_id.id)]
            )
            return res
        return False
