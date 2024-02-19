# -*- encoding: utf-8 -*-

from odoo import models,fields, api


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    etablissement = fields.Char(string=u'Établissement')
    niveau_scolaire = fields.Char(string=u'Niveau scolaire')