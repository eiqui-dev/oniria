# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
#import pydevd

##Ampliación del modelo customer para turists##
class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = "res.partner"	

    turist = fields.Boolean(
	    string="Turista",
	    help="Activa este check si el contacto es un visitante/turist")
res_partner()


