# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
import logging
_logger = logging.getLogger(__name__)

# Ampliar res_partner
class res_partner(models.Model):
    _inherit = 'res.partner'
    
    def get_composed_address(self, sep):
        return sep.join([x for x in [self.street,
                            self.street2,
                            self.zip,
                            self.city,
                            self.country_id.name] if x])
    
    def find_address_or_create(self, street, city, state, country, postalcode):
        partner_id = self.search([('street','=',street),
                                  ('city','=',city),
                                  ('state_id','=',state),
                                  ('country_id','=',country),
                                  ('zip','=',postalcode)])
        if not partner_id:
            partner_id = self.create({
                'name': 'Direccion Evento',
                'street': street,
                'city': city,
                'state_id': state,
                'country_id': country,
                'zip': postalcode
            })
        return partner_id