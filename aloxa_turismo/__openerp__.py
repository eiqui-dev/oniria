# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 SoluciÃ³ns Aloxa S.L. <info@aloxa.eu>
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
{
    'name': "aloxa_turismo",

    'summary': """
        Módulo de gestión de plataforma de Turismo""",

    'description': """
        Gestión de plataformas de promoción Turística integrada
    """,

    'author': "Solucions Aloxa S.L.",
    'website': "http://www.aloxa.eu",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'turismo',
    "icon": "/aloxa_turismo/static/src/img/icon.png",    
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale', 'mail','website_event_sale','website_event_register_free_with_sale'],

    # always loaded
    'data': [
        'data/ir.model.data.csv',
        'data/turismo.opciones.csv',               
        'views/establishments.xml',
        'views/comun.xml',
        'views/products.xml',
        'security/ir.model.access.csv',
	    'views/turists.xml',
        #'views/reservas.xml',
        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [        
    ],
}
