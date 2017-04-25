# -*- coding: utf-8 -*-

from openerp import models, api, fields, exceptions
from datetime import datetime, date
from openerp.addons.website.models.website import slugify
from controllers.html_table import table_compute
import random
import re
import logging
_logger = logging.getLogger(__name__)
#import pydevd

# Metodos para la pagina principal del sitio web, se hace asi por no pisar a kingfisher en la pagina principal
class website(models.Model):
    _inherit = 'website'
    _name = "website"
        
    def sanitize_url(self, url):
        if url:
            matchObj = re.match(r'^https?://', url, re.M|re.I)
            if not matchObj:
                url = "http://" + url # TODO: Por defecto http, quizas mejor https ?
        return url

    def get_banners_portada(self):
        #pydevd.settrace("10.0.3.1")
        #('product_id.link_position', '=', 'Portada')
        banners = self.env['turismo.contract_product_customer'].search(['|','&',('fecha_fin', '>=', datetime.now()),('fecha_fin', '=', False),('publicado', '=', True),('product_id.link_position', '=', 'Portada')])
        num_banners = len(banners)
        random_indices = random.sample(range(num_banners), num_banners)
        banners = [ banners[i] for i in random_indices ]
        return table_compute().process_home(banners)
    
    def get_composed_address(self, partner, sep):
        return sep.join([x for x in [partner.street,
                            partner.street2,
                            partner.zip,
                            partner.city,
                            partner.country_id.name] if x])
    
    def get_float_hours(self, hours):
        minutes = int(round(hours * 60))
        return "%02d:%02d" % divmod(minutes, 60)
    
    def get_current_year(self):
        return date.today().year
    
    def get_day_of_week(self, day):
        days = (u'Lunes', u'Martes', u'Miércoles', u'Jueves', u'Viernes', u'Sábado', u'Domingo')
        return days[int(day)]
    
    def get_stablisment_events(self, stablisment_id):
        ModelEventEvent = self.env['event.event']
        event_ids = ModelEventEvent.search([('organizer_id','=',stablisment_id)])
        return event_ids
    
    def get_stablisment_products(self, stablisment_id):
        ModelProductTemplate = self.env['product.template']
        product_ids = ModelProductTemplate.search([('seller_ids.name','in',[stablisment_id])])
        return product_ids
    
    def get_contrated_stablisment_links(self, uid, stablisment_id):
        user = self.env['res.users'].browse([uid])
        products_c = user.partner_id.contract_product_customer_ids
        links = list()
        for product in products_c:
            if stablisment_id == product.establishment_id.id:
                links.append(product)
        return links
    
    def get_contrated_product_links(self, uid, product_id):
        user = self.env['res.users'].browse([uid])
        products_c = user.partner_id.contract_product_customer_ids
        links = list()
        for product in products_c:
            if product_id == product.product_tur_id.id:
                links.append(product)
        return links
