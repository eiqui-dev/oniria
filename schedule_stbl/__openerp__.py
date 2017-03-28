# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name' : 'schedule_stbl',
    'version' : '1.1',
    'author' : 'OpenERP SA',
    'category' : 'Hidden/Dependency',
    'website' : 'http://www.openerp.com',
    'description': """
Module for schedule_stbl management.
===============================

A schedule_stbl represent something that can be scheduled (a developer on a task or a
work center on manufacturing orders). This module manages a schedule_stbl calendar
associated to every schedule_stbl. It also manages the leaves of every schedule_stbl.
    """,
    'author': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'depends': ['base','aloxa_turismo'],
    'data': ['schedule_stbl_view.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
