# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
try:
    import simplejson as json
except ImportError:
    import json     # noqa
import urllib
import logging
_logger = logging.getLogger(__name__)

def matrix_distance(origin, dest):
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&mode=driving&units=metric' % (','.join(origin), ','.join(dest))

    try:
        result = json.load(urllib.urlopen(url))
    except Exception, e:
        raise exceptions.AccessError(_('Cannot contact google apis servers. Please make sure that your internet connection is up and running (%s).') % e)
    if result['status'] != 'OK':
        return None

    try:
        dist_matrix = result['rows'][0]['elements']
        return dist_matrix['distance'], dist_matrix['duration']
    except (KeyError, ValueError):
        return None


# Ampliar res_partner
class res_partner(models.Model):
    _inherit = 'res.partner'
    
    def get_matrix_distance(self, partner_id):
        return matrix_distance(self._get_geo_location_array(), partner_id._get_geo_location_array())
    
    def _get_geo_location_array(self):
        return [self.partner_latitude, self.partner_longitude]
    
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
        partner_id.geo_localize()
        return partner_id