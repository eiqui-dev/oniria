# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
#import pydevd

##Ampliación del modelo customer para turists##
class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = "res.partner"	

    turist = fields.Boolean(
	    string="Turist",
	    help="Turist Contact")
res_partner()


