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

class event_event(models.Model):
    _inherit = "event.event"	

    address_id = fields.Many2one('turismo.establishment', string='Location',
        default=lambda self: self.env.user.company_id.partner_id,
        readonly=False, states={'done': [('readonly', True)]})


