# -*- encoding: utf-8 -*-

from odoo import models,fields, api

class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    fond = fields.Char(string=u'Fond')
    theme = fields.Char(string=u'Théme')
    collection = fields.Char(string=u'COLLECTION')
    auteur = fields.Char(string=u'AUTEUR')
    editeur = fields.Char(string=u'EDITEUR')
    date_parution = fields.Date(string=u'Date de parution')