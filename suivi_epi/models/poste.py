# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SuiviEpiPoste(models.Model):
    _inherit = 'hr.job'
    _description = "Liste des poste de l'entreprise"
    
    epi_line_ids = fields.One2many(
        string='EPI',
        comodel_name='suivi.epi.line',
        inverse_name='poste_id',
    )


    @api.onchange('epi_line_ids')
    def _onchange_epi_line_ids(self):
        for rec in self:
            employees = self.env['hr.employee'].search([])
            jobs = self.env['hr.job'].search([])
            for job in jobs:
                emp = self.env['hr.employee'].search([('job_id', '=', job.id)])
                epi_line = self.env['suivi.epi.line'].search([('poste_id', '=', job.id)])
                if len(emp) > 0 :
                    print("yes caaaa")
                    for em in emp :
                        em.epi_ids = epi_line
                
    

    
    