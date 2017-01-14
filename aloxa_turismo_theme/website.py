# -*- coding: utf-8 -*-

from openerp import models, api, fields, exceptions
from datetime import datetime
from openerp.addons.website.models.website import slugify
from controllers.html_table import table_compute
import random
import re
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
        banners = self.env['turismo.producto_contratado_cliente'].search(['|','&',('fecha_fin', '>=', datetime.now()),('fecha_fin', '=', False),('publicado', '=', True),('product_id.link_position', '=', 'Portada')])
        num_banners = len(banners)
        random_indices = random.sample(range(num_banners), num_banners)
        banners = [ banners[i] for i in random_indices ]
        return table_compute().process_home(banners)
