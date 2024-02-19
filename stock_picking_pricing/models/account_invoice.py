# -*- encoding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution    
#    Copyright (C) 2004-2017 NEXTMA (http://nextma.com). All Rights Reserved
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

# import convertion
from . import convertion
from odoo import api,models,fields



class AccountMove(models.Model):
    
    _inherit = "account.move"

    total_lettre = fields.Char('Total en lettres', compute='get_amount_letter')

    @api.depends('amount_total')
    def get_amount_letter(self):
        for rec in self:
        # amount = convertion.trad(self.amount_total,self.currency_id.name)
            rec.total_lettre  = convertion.trad(rec.amount_total,'DH')
            # self.total_lettre = convertion.trad(self.amount_total,'DH').upper()
        #return amount

