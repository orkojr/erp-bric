# -*- coding: utf-8 -*-

from ntpath import join
from pkg_resources import require
from odoo import api, fields, models


class CustomCrmClient(models.Model):
    _name = 'res.partner'
    _inherits = {'crm.lead': 'user_id'}
    _description = """Decrit les clients."""
    _sql_constraints =  [
        ('name_unique','UNIQUE(code_client)',
         'Le code du  client doit etre Unique!'),       
    ]


    code_client = fields.Char('Code client',required=True, help="Identifie de maniere unique un client")
    prenom = fields.Char('Prenom',required=True, help="Prenom  client")
    nom = fields.Char('Nom',required=True, help="Nom  client")
    email = fields.Char('Email', help="Adresse Email  client")
    ville = fields.Char('Ville', help="Ville Client")
    cp = fields.Char('Code Postal', help="Code postal")
    pays = fields.Char('Pays', help="pays")
    phone = fields.Char('Telephone', help="Telephone client")
    
    user_id = fields.Many2one(
        string='User id',
        comodel_name='crm.lead',
        ondelete='restrict',
        help="Pour identifier l'utilisateur",
        auto_join=True
        
    )

    
    quartier_id = fields.Many2one(
        string='quartier',
        comodel_name='bric.quartier',
        ondelete='restrict',
        help = "Indique le quartier du client",
        auto_join=True,
        
    )
    