# -*- coding: utf-8 -*-
# © Openlabs Technologies & Consulting (P) Limited
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Stock picking pricing V15',
    'version': '15.1',
    'category': 'Generic Modules/Sales & Purchases',
    'website': 'http://www.meengineeringexpertise.com',
    'author': 'MeEngineeringExpertise',
    'depends': ['base', 'sale','sale_stock','stock_account','purchase'],
    'data': [
        'views/sale.xml',
        'views/report.xml',
        'views/report_invoice.xml',
    ],
    'installable': True,
}
