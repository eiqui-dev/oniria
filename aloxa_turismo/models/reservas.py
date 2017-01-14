# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
#import pydevd

##Ampliación del modelo cliente para turistas##
class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = "res.partner"	

    turista = fields.Boolean(
	    string="Turista",
	    help="Activa este check si el contacto es un visitante/turista")
res_partner()


class hotel_room(models.Model):
    _name = 'hotel.room'
    _inherit = 'hotel.room'
    
    #field
    
hotel_room()


class folio_room_line(models.Model):

    _name = 'folio.room.line'
    _inherit = 'folio.room.line'
    _description = 'Reservas de Visitas'
    _rec_name = 'room_id'

    room_id = fields.Many2one(comodel_name='hotel.room', string='Visita id')
    folio_id = fields.Many2one('hotel.folio', string='Número de Folio')

folio_room_line()

