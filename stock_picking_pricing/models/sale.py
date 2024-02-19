from odoo import api, models, fields, _
import odoo.addons.decimal_precision as dp
from . import convertion
import datetime
from odoo.exceptions import Warning,UserError
from collections import defaultdict
from odoo.tools import float_compare, float_round, pycompat


class StockRule(models.Model):
    _inherit = 'stock.rule'


    # tax_ids = fields.Many2many('account.tax', 'stock_move_taxe', 'move_id', 'tax_id', 'Taxes')
    # discount = fields.Float(string='Rem.(%)',digits=dp.get_precision('Discount'))
    # price_unit2 = fields.Float('P.Unitaire', help="Technical field used to record the product cost set by the user during a picking confirmation (when costing method used is 'average price' or 'real'). Value given in company currency and in product uom.", digits=dp.get_precision('Product Price'))

    # def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        result = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
        if  values.get('sale_line_id', False):
            line_id = values.get('sale_line_id', False)
            line = self.env['sale.order.line'].search([('id','=',line_id)])
            result['price_unit2'] = line.price_unit
            result['discount'] = line.discount
            result['tax_ids'] = [(6, 0, line.tax_id.ids)]
        return result


# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'

#     
#     def _prepare_procurement_values(self, group_id=False):
#         values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
#         values.update({
#             'price_unit2':self.price_unit,
#             'discount':self.discount,
#             'tax_ids':[(6, 0, self.tax_id.ids)],
#         })
#         return values


##-----------------------------------------------


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    total_without_discount = fields.Float(compute='_get_total_without_discount', digits=dp.get_precision('Account'))
    total_discount = fields.Float(compute='_get_total_discount', digits=dp.get_precision('Account'))
    amount_untaxed = fields.Float(compute='_get_amount_untaxed', string="H.T", digits=dp.get_precision('Account'))
    amount_tax = fields.Float(compute='_get_amount_tax', string='TVA', digits=dp.get_precision('Account'))
    amount_total = fields.Float(compute='_get_amount_total',string="T.T.C", digits=dp.get_precision('Account'))
    
    total_lettre = fields.Char('Total en lettres', compute='get_amount_letter')

    bl_fournisseur = fields.Char('Réf bl fournisseur')

    ##---
    livreur = fields.Char('Livreur', track_visibility="onchange")
    ##--
    poids_total = fields.Float("Poid total", compute="compute_weight")
    
    @api.depends('move_lines')
    def compute_weight(self):
        for rec in self:
            rec.poids_total = sum(line.product_qty*line.product_id.weight for line in rec.move_lines)
    
    @api.depends('amount_total')
    def get_amount_letter(self):
        for rec in self:
            if rec.amount_total:
                rec.total_lettre = convertion.trad(rec.amount_total,'DH').upper()

            else:
                rec.total_lettre = ''

    @api.depends('move_lines')
    def _get_total_without_discount(self):
        for rec in self:
            if rec.move_lines:
                    rec.total_without_discount =sum(r.total_without_discount for r in rec.move_lines)
    
    @api.depends('move_lines')
    def _get_total_discount(self):
        for rec in self:
            if rec.move_lines:
                rec.total_discount =sum(r.total_discount for r in rec.move_lines)
        
        
    @api.depends('move_lines')
    def _get_amount_total(self):
        for rec in self:
            if rec.move_lines:
                    rec.amount_total =sum(r.amount_total for r in rec.move_lines)
            else:
                rec.amount_total = 0

    @api.depends('move_lines')
    def _get_amount_untaxed(self):
        for rec in self:
            if rec.move_lines:
                rec.amount_untaxed =sum(r.amount_untaxed for r in rec.move_lines)
            # @todo else line added
            else : rec.amount_untaxed =0

    @api.depends('move_lines')
    def _get_amount_tax(self):
        for rec in self:
            if rec.move_lines:
                rec.amount_tax =sum(r.amount_tax for r in rec.move_lines)

            
class stockMove(models.Model):
    _inherit = 'stock.move'


    total_without_discount = fields.Float(compute='_get_total_without_discount',  digits=dp.get_precision('Account'),store=True)
    amount_untaxed = fields.Float(compute='get_amount', store=True, digits=dp.get_precision('Account'),string='Total HT')
    amount_tax = fields.Float(compute='get_amount', store=True,string='TVA', digits=dp.get_precision('Account'))
    amount_total = fields.Float(compute='get_amount', store=True, string='Total TTC',digits=dp.get_precision('Account'))
    tax_ids = fields.Many2many('account.tax', 'stock_move_taxe', 'move_id', 'tax_id', 'Taxes')
    discount = fields.Float(string='Rem.(%)',digits=dp.get_precision('Discount'))
    total_discount = fields.Float(compute='_get_total_discount',store=True,string='Remise',)
    price_unit2 = fields.Float('P.Unitaire', help="Technical field used to record the product cost set by the user during a picking confirmation (when costing method used is 'average price' or 'real'). Value given in company currency and in product uom.", digits=dp.get_precision('Product Price'))
 
    price_unit_ttc = fields.Float('P.U TTC', compute="compute_pu_ttc")

    @api.depends('amount_total','product_uom_qty')
    def compute_pu_ttc(self):
        for rec in self:
            if rec.amount_total and rec.product_uom_qty:
                rec.price_unit_ttc = rec.amount_total/rec.product_uom_qty
            else:
                rec.price_unit_ttc = 0
    price_unit_ttc_nd =fields.Float('P.U TTC Sans remise', compute="compute_pu_ttc2") 

    @api.depends('product_uom_qty', 'discount', 'price_unit2', 'tax_ids')
    def compute_pu_ttc2(self):
        for rec in self:
            if rec.amount_total and rec.product_uom_qty:
                price = rec.price_unit2
                taxes = rec.tax_ids.compute_all(price,quantity=1.0, product=rec.product_id, partner=rec.picking_id.partner_id)
                rec.price_unit_ttc_nd = taxes['total_included']
            # @todo else line added
            else: rec.price_unit_ttc_nd = 0

            
    def _prepare_move_split_vals(self, uom_qty):
        res=super(stockMove,self)._prepare_move_split_vals(uom_qty)
        res.update({'price_unit2':self.price_unit2})
        return res

    
    @api.depends('product_uom_qty', 'discount', 'price_unit2', 'tax_ids')
    def get_amount(self):
        """
        Compute the amounts of the  lines.
        """
        for line in self:
            price = line.price_unit2 * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_ids.compute_all(price,quantity=line.product_uom_qty, product=line.product_id, partner=line.picking_id.partner_id)
            line.amount_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            line.amount_total = taxes['total_included']
            line.amount_untaxed =  taxes['total_excluded']


    @api.depends('price_unit2','product_uom_qty','discount')        
    def _get_total_discount(self):
        for rec in self:
            rec.total_discount = rec.price_unit2 * rec.product_uom_qty * rec.discount / 100
            
    @api.depends('total_without_discount')        
    def _get_total_without_discount(self):
        for rec in self:
            rec.total_without_discount = rec.price_unit2 * rec.product_uom_qty

    @api.onchange('product_id')
    def onchange_product(self):
        for rec in self:
            if rec.product_id:
                rec.tax_ids = rec.product_id.taxes_id


class product_template(models.Model):
    _inherit = "product.template"

    margin = fields.Float('Marge', compute="compute_margin")

    percent_margin = fields.Float('Marge %', compute="compute_margin")


    @api.depends('list_price','standard_price')
    def compute_margin(self):
        for record in self:
            record.margin = record.list_price - record.standard_price
            if record.list_price!=0:
                record.percent_margin = (record.margin/record.list_price)*100
            # todo else line added
            else:
                record.percent_margin = 0

class purchase_order_line(models.Model):        
    _inherit ='purchase.order.line'
    
    
    def _prepare_stock_moves(self, picking):
        stock_move_lines = super(purchase_order_line, self)._prepare_stock_moves(picking)
        for i in range(0, len(stock_move_lines)):
                  stock_move_lines[i]['price_unit2'] = self.price_unit
                  # @todo discount line added
                  stock_move_lines[i]['discount'] = self.discount
                  stock_move_lines[i]['tax_ids'] = [(6, 0, self.taxes_id.ids)]
        return stock_move_lines


