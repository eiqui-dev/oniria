# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Solucións Aloxa S.L. <info@aloxa.eu>
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
    'name': "aloxa_turismo_theme",

    'summary': """
        Módulo de gestión de plataforma de Turismo Web""",

    'description': """
        Web de promoción Turística integrada
    """,

    'author': "Solucions Aloxa S.L.",
    'website': "http://www.aloxa.eu",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Theme/Creative',
    "icon": "/aloxa_turismo_theme/static/src/img/icon.png",    
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website', 'website_sale', 'aloxa_turismo', 'l10n_es_partner', 'website_google_apis', 'horario'],

    # always loaded
    'data': [
        'views/website/external_footer.xml',
        'views/website/external_menu.xml',
        'views/website/general.xml',
        'views/website/home.xml',
        'views/website/directory.xml',
        'views/website/directory_grid.xml',
        'views/website/directory_list.xml',
        'views/website/directory_map.xml',
        'views/website/directory_form_establecimiento.xml',
        'views/website/directory_form_event.xml',
        'views/website/panel_cliente.xml',
        'views/website/establecimiento_template.xml',
        'views/website/producto_contratado_template.xml',
        'views/website/solicitar_link_template.xml',
        'views/website/registro_usuario.xml',
        'views/website/registro_empresa.xml',
        'views/website/editar_usuario.xml',
        'views/website/crear_editar_establecimiento.xml',
        'views/website/crear_editar_producto.xml',
        'views/website/crear_evento.xml',
        'views/website/rutas_template.xml',
        
        'views/website/inherit_website_sale_products.xml',
        
        'data/data.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [        
    ],
}