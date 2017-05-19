# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID, http, tools
from openerp.http import request
from openerp.addons.website.controllers.main import Website
# from openerp.tools import image_resize_and_sharpen, image_save_for_web
from datetime import datetime
from html_table import table_compute
from collections import OrderedDict
from openerp.addons.auth_signup.res_users import SignupError
from openerp.addons.web.controllers.main import login_redirect, content_disposition
from openerp.addons.website.models.website import slug
# from openerp.addons.auth_signup.controllers.main import AuthSignupHome
import googlemaps
import requests
import re
import base64
import werkzeug.utils
import logging

_logger = logging.getLogger(__name__)
# import pydevd


class QueryURL(object):
    def __init__(self, path='', **args):
        self.path = path
        self.args = args

    def __call__(self, path=None, **kw):
        if not path:
            path = self.path
        for k, v in self.args.items():
            kw.setdefault(k,v)
        l = []
        for k, v in kw.items():
            if v:
                if isinstance(v, list) or isinstance(v, set):
                    l.append(werkzeug.url_encode([(k, i) for i in v]))
                else:
                    l.append(werkzeug.url_encode([(k, v)]))
        if l:
            path += '?' + '&'.join(l)
        return path


# Clase intermedia para generar la tabla del directorio
class htmlBannerDirectorio:
    contract_product = None
    establishment = None
    events = None


class attrDirectorio:
    label = None
    name = None
    values = None
    open = False
    icon = None


class attrValueDirectorio:
    label = None
    name = None
    num = None
    sel = False


class website_aloxa_turismo(Website):
    def _get_banners_directorio(self, orderby, product_category=None, product_type=None, params=None):
        banners_directorio = []
        request.session['search_records'] = False

        # pydevd.settrace("10.0.3.1")
        # Recoger los establishments
        searchDomain = []
        if not product_category and (product_type == "establishment" or not product_type):
            searchDomain.append(('website_published', '=', True))
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if any(params['search']):
                    searchDomain.append('|')
                    searchDomain.append(('name', 'ilike', params['search']))
                    searchDomain.append(('description', 'ilike', params['search']))		    
                # t_localities
                t_localities_k = [s for s in params if s.startswith("locality-")]
                t_localities = [werkzeug.url_unquote_plus(params[s]) for s in t_localities_k]
                if any(t_localities):
                    searchDomain.append(('city', 'in', [False if q == 'none' else q for q in t_localities]))
                # Services
                services_k = [s for s in params if s.startswith("service-")]
                services = [int(werkzeug.url_unquote_plus(params[s])) for s in services_k]
                if any(services):
                    searchDomain.append(('services', 'in', services))

                # pydevd.settrace("10.0.3.1")
                param_type_est_k = [s for s in params
                                    if s.startswith("type_establishment-")]
                param_type_est = [werkzeug.url_unquote_plus(params[s])
                                  for s in param_type_est_k]
                if len(param_type_est) > 0:
                    searchDomain.append(('type_s', 'in', param_type_est))

            # OrderBy
            if orderby == 'direccion':
                orderby_key = 'street'
            else:
                orderby_key = 'name'

            registros = request.env['turismo.establishment']\
                .search(searchDomain).sorted(key=lambda r: r[orderby_key])
            request.session['search_records'] = registros.mapped('id')
            for reg in registros:
                tmp_banner = htmlBannerDirectorio()
                tmp_banner.establishment = reg
                events = request.env['event.event'].search([
                                    ('website_published', '=', True),
                                    ('organizer_id', '=', reg.partner_id.id),
                                    ('date_end', '>=', datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT))
                                ], limit=4)
                tmp_banner.events = events
                banners_directorio.append(tmp_banner)
        elif product_type == "event":
            searchDomain.append(('website_published','=',True))
            searchDomain.append(('date_end','>=',datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)))
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if len(params['search']) > 0:
                    searchDomain.append('|')
                    searchDomain.append(('name', 'ilike', params['search']))
                    searchDomain.append(('description', 'ilike', params['search']))		    
		if 'date_event' in params.keys() and len(params['date_event']) > 0:
		    date_event = datetime.strptime(werkzeug.url_unquote_plus(params['date_event']), tools.DEFAULT_SERVER_DATETIME_FORMAT)
		    date_str = date_event.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
                    searchDomain.append(('date_begin', '>=', date_str))
		    searchDomain.append(('date_end', '<=', date_str))
                # t_localities
                t_localities_k = [s for s in params if s.startswith("locality-")]
                t_localities = [werkzeug.url_unquote_plus(params[s]) for s in t_localities_k]
                if len(t_localities) > 0:
                    searchDomain.append(('address_id.city', 'in', [False if q=='none' else q for q in t_localities]))
            	# Services
                services_k = [s for s in params if s.startswith("service-")]
                services = [int(werkzeug.url_unquote_plus(params[s])) for s in services_k]
                if any(services):
                    searchDomain.append(('address_id.services', 'in', services))
		            
            # OrderBy
            if orderby == 'direccion':
                orderby_key = 'street'
            else:
                orderby_key = 'name'
                
            registros = request.env['event.event'].search(searchDomain).sorted(key=lambda r: r[orderby_key])
            request.session['search_records'] = registros.mapped('id')
            for reg in registros:
                tmp_banner = htmlBannerDirectorio()
                tmp_banner.events = reg
                banners_directorio.append(tmp_banner)
        else:
            # Recoger los banners
            searchDomain = ['|','&',('fecha_fin', '>=', datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)),('fecha_fin', '=', False),('product_tur_id.website_published', '=', True),('product_id.link_position', '=', 'Directorio')]
            if product_category:
                searchDomain.append(('public_category_id', '=', product_category.id))
            if product_type:
                searchDomain.append(('product_tur_id.type_product', '=', product_type))
            
            #pydevd.settrace("10.0.3.1")
            if params and 'search' in params.keys():
                if len(params['search']) > 0:
                    searchDomain.append('|')
                    searchDomain.append(('product_tur_id.name', 'ilike', params['search']))
                    searchDomain.append(('product_tur_id.description', 'ilike', params['search']))
                if 'anhada' in params.keys() and len(params['anhada']) > 0:
                    searchDomain.append(('product_tur_id.anho', '=', params['anhada']))
                if 'type_wine' in params.keys() and len(params['type_wine']) > 0:
                    searchDomain.append(('product_tur_id.typewine', '=', params['type_wine'].lower()))
                if 'type_vinagre' in params.keys() and len(params['type_vinagre']) > 0:
                    searchDomain.append(('product_tur_id.typevinagre', '=', params['type_vinagre'].lower()))
                if 'type_grape' in params.keys() and len(params['type_grape']) > 0:
                    searchDomain.append(('product_tur_id.grape', '=', params['type_grape'].lower()))
                if 'awards' in params.keys() and len(params['awards']) > 0:
                    searchDomain.append(('product_tur_id.awards', '=', params['awards'].lower()))
                if 'locality' in params.keys() and len(params['locality']) > 0:
                    searchDomain.append(('product_tur_id.city', '=', params['locality'].lower()))
            # OrderBy
            if orderby == 'precio':
                orderby_key = 'list_price'
            else:
                orderby_key = 'name'
            
            products_contratados = request.env['turismo.contract_product_customer'].search(searchDomain).sorted(key=lambda r: r.product_tur_id[orderby_key])
            request.session['search_records'] = products_contratados.mapped('id')
            num_items = len(products_contratados)
            for i in range(num_items):
                tmp_banner = htmlBannerDirectorio()
                tmp_banner.contract_product = products_contratados[i]
                banners_directorio.append(tmp_banner)
                
        # Mezclar items
        #num_items = len(banners_directorio)
        #random_indices = random.sample(range(num_items), num_items)
        #banners_directorio = [ banners_directorio[i] for i in random_indices ]
        
        # Generar tabla HTML
        return (table_compute().process_directory(banners_directorio), len(banners_directorio))
    
    
    def _create_directory_attributes(self, product_type = None, params = None):
        attributes = []
        
        if product_type == 'establishment':
            searchDomain = [('website_published','=',True)]
            
            param_type_establishment = []
            param_t_localities = []
            param_services = []
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if len(params['search']) > 0:
                    searchDomain.append('|')
                    searchDomain.append(('name', 'ilike', params['search']))
                    searchDomain.append(('description', 'ilike', params['search']))
                    
                # t_localities
                param_t_localities_k = [s for s in params if s.startswith("locality-")]
                param_t_localities = [werkzeug.url_unquote_plus(params[s]) for s in param_t_localities_k]
                
                # Type establishment
                param_type_establecimento_k = [s for s in params if s.startswith("type_establishment-")]
                param_type_establishment = [werkzeug.url_unquote_plus(params[s]) for s in param_type_establecimento_k]
     
                # Type establishment
                param_services_k = [s for s in params if s.startswith("service-")]
                param_services = [int(werkzeug.url_unquote_plus(params[s])) for s in param_services_k]
    
            searchDomainestablishments = list(searchDomain)
            searchDomaint_localities = []
            searchDomainServices = []
            searchDomainTypes = []
            if any(param_t_localities):
                searchDomaint_localities.append(('city', 'in', [False if q=='none' else q for q in param_t_localities]))
            if any(param_services):
                searchDomainServices.append(('services', 'in', [False if q=='none' else q for q in param_services]))
            if any(param_type_establishment):
                searchDomainTypes.append(('type_s', 'in', [False if q=='none' else q for q in param_type_establishment])) 
            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-tag'
            attribute.label = "Type"
            attribute.name = "type_establishment"    
            attribute.values = []
            value = attrValueDirectorio()
            value.label = 'Winecellars'
            value.name = 'winecellar'
            value.sel = True if value.name in param_type_establishment else False
            value.num = request.env['turismo.establishment'].search_count(searchDomainestablishments+searchDomaint_localities+searchDomainServices+[('type_s','=','winecellar')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Restaurants'
            value.name = 'restaurant'
            value.sel = True if value.name in param_type_establishment else False
            value.num = request.env['turismo.establishment'].search_count(searchDomainestablishments+searchDomaint_localities+searchDomainServices+[('type_s','=','restaurant')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Lodgings'
            value.name = 'lodging'
            value.sel = True if value.name in param_type_establishment else False
            value.num = request.env['turismo.establishment'].search_count(searchDomainestablishments+searchDomaint_localities+searchDomainServices+[('type_s','=','lodging')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Vineyards'
            value.name = 'vineyard'
            value.sel = True if value.name in param_type_establishment else False
            value.num = request.env['turismo.establishment'].search_count(searchDomainestablishments+searchDomaint_localities+searchDomainServices+[('type_s','=','vineyard')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Art and Culture'
            value.name = 'cultural'
            value.sel = True if value.name in param_type_establishment else False
            value.num = request.env['turismo.establishment'].search_count(searchDomainestablishments+searchDomaint_localities+searchDomainServices+[('type_s','=','cultural')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'winebars'
            value.name = 'winebar'
            value.sel = True if value.name in param_type_establishment else False
            value.num = request.env['turismo.establishment'].search_count(searchDomainestablishments+searchDomaint_localities+searchDomainServices+[('type_s','=','winebar')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Others'
            value.name = 'other'
            value.sel = True if value.name in param_type_establishment else False
            value.num = request.env['turismo.establishment'].search_count(searchDomainestablishments+searchDomaint_localities+searchDomainServices+[('type_s','=','other')])
            attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-cubes'
            attribute.label = "Services"
            attribute.name = "service"
            
            attribute.values = []
            services = request.env['establishment.services'].search([])
            establishments = request.env['turismo.establishment']
            for service in services:
                value = attrValueDirectorio()
                value.num = establishments.search_count(searchDomainestablishments+searchDomaint_localities+searchDomainTypes+[('services','in',[service.id])])
                value.name = service.id
                value.label = service.name
                value.sel = True if service.id in param_services else False
                attribute.values.append(value)
            attributes.append(attribute)
                            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-map-marker'
            attribute.label = "locality"
            attribute.name = "locality"
            
            #searchDomaint_localities = list(searchDomain)
            #if len(param_type_establishment) > 0:
            #    searchDomaint_localities.append(('type', 'in', param_type_establishment)) 
            
            attribute.values = []
            establishments = request.env['turismo.establishment'].search(searchDomainestablishments+searchDomainTypes+searchDomainServices, order='city')
            t_localities = establishments.mapped('city')
            t_localities = OrderedDict.fromkeys(t_localities).keys()
            for locality in t_localities:
                value = attrValueDirectorio()
                value.num = establishments.search_count([('city','=',locality)])
                value.name = locality or 'none'
                value.label = locality or "Sin Definir"
                value.sel = True if locality in param_t_localities or (not locality and value.name in param_t_localities) else False
                attribute.values.append(value)
            attributes.append(attribute)
            
        elif product_type == 'wine':
            searchDomain = [('product_tur_id.website_published','=',True)]
            
            param_type_wine = []
            param_type_grape = []
            param_awards = []
            param_anhada = []
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if any(params['search']):
                    searchDomain.append('|')
                    searchDomain.append(('product_tur_id.name', 'ilike', werkzeug.url_unquote_plus(params['search'])))
                    searchDomain.append(('product_tur_id.description', 'ilike', werkzeug.url_unquote_plus(params['search'])))
                    
                # Wine type
                param_type_wine_k = [s for s in params if s.startswith("type_wine-")]
                param_type_wine = [werkzeug.url_unquote_plus(params[s]) for s in param_type_wine_k]
                
                # Grape type
                param_type_grape_k= [s for s in params if s.startswith("type_grape-")]
                param_type_grape = [werkzeug.url_unquote_plus(params[s]) for s in param_type_grape_k]
                
                # Awards
                param_awards_k = [s for s in params if s.startswith("awards-")]
                param_awards = [werkzeug.url_unquote_plus(params[s]) for s in param_awards_k]
                
                # Anhada
                param_anhada_k = [s for s in params if s.startswith("anhada-")]
                param_anhada = [werkzeug.url_unquote_plus(params[s]) for s in param_anhada_k]
                
            searchDomainwines = list(searchDomain)
            if any(param_type_wine):
                searchDomainwines.append(('product_tur_id.typewine.name', 'in', [False if q=='none' else q for q in param_type_wine]))
            if any(param_type_grape):
                searchDomainwines.append(('product_tur_id.grape.name', 'in', [False if q=='none' else q for q in param_type_grape]))
            if any(param_awards):
                searchDomainwines.append(('product_tur_id.awards.name', 'in', [False if q=='none' else q for q in param_awards]))
            if any(param_anhada):
                searchDomainwines.append(('product_tur_id.anho', 'in', [False if q=='none' else q for q in param_anhada]))
            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-glass'
            attribute.label = "Wine type"
            attribute.name = "type_wine"
            wine_tags = request.env['turismo.wine.tag'].search([], order='name')
            wine_tags = wine_tags.mapped('name')
            wine_tags = OrderedDict.fromkeys(wine_tags).keys()
            attribute.values = []
            for tag in wine_tags: 
                value = attrValueDirectorio()
                value.num = request.env['turismo.contract_product_customer'].search_count(searchDomainwines+[('product_tur_id.type_product','=','wine'),
                                                                                             ('product_tur_id.typewine','=',tag)])
                value.name = value.label = tag
                value.sel = True if value.name in param_type_wine else False
                attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-tint'
            attribute.label = "Grape type"
            attribute.name = "type_grape"
            grape_tags = request.env['turismo.grape.tag'].search([], order='name')
            grape_tags = grape_tags.mapped('name')
            grape_tags = OrderedDict.fromkeys(grape_tags).keys()
            attribute.values = []
            for tag in grape_tags: 
                value = attrValueDirectorio()
                value.num = request.env['turismo.contract_product_customer'].search_count(searchDomainwines+[('product_tur_id.type_product','=','wine'),
                                                                                             ('product_tur_id.grape','=',tag)])
                value.name = value.label = tag
                value.sel = True if value.name in param_type_grape else False
                attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.icon = 'fa-star'
            attribute.label = "Awards"
            attribute.name = "awards"
            award_tags = request.env['turismo.award.tag'].search([], order='name')
            award_tags = award_tags.mapped('name')
            award_tags = OrderedDict.fromkeys(award_tags).keys()
            attribute.values = []
            for tag in award_tags: 
                value = attrValueDirectorio()
                value.num = request.env['turismo.contract_product_customer'].search_count(searchDomainwines+[('product_tur_id.type_product','=','wine'),
                                                                                             ('product_tur_id.awards','=',tag)])
                value.name = value.label = tag
                value.sel = True if value.name in param_awards else False
                attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.icon = 'fa-calendar'
            attribute.label = "Year"
            attribute.name = "anhada"
            wines = request.env['product.template'].search([('type_product','=','wine')], order='anho')
            anhos = wines.mapped('anho')
            anhos = OrderedDict.fromkeys(anhos).keys()
            attribute.values = []
            for anho in anhos:
                value = attrValueDirectorio()
                value.num = request.env['turismo.contract_product_customer'].search_count(searchDomainwines+[('product_tur_id.type_product','=','wine'),
                                                                                             ('product_tur_id.anho','=',anho)])
                value.name = value.label = str(anho)
                value.sel = True if value.name in param_anhada else False
                attribute.values.append(value)
            attributes.append(attribute)
            
        elif product_type == 'event':
            searchDomain = [('website_published','=',True),('date_end','>=',datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT))]
 	     # Type establishment
           
            param_services = []
	    param_t_localities = []
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if any(params['search']):
                    searchDomain.append('|')
                    searchDomain.append(('name', 'ilike', params['search']))
                    searchDomain.append(('description', 'ilike', params['search']))
                    
                # t_localities
                param_t_localities_k = [s for s in params if s.startswith("locality-")]
                param_t_localities = [werkzeug.url_unquote_plus(params[s]) for s in param_t_localities_k]

		# t_services
		param_services_k = [s for s in params if s.startswith("service-")]
            	param_services = [int(werkzeug.url_unquote_plus(params[s])) for s in param_services_k]
            
	    searchDomainevents = list(searchDomain)
            if any(param_t_localities):
                searchDomainevents.append(('address_id.city', 'in', [False if q=='none' else q for q in param_t_localities]))
            if any(param_services):
                searchDomainevents.append(('address_id.services', 'in', [False if q=='none' else q for q in param_services]))   
            #searchDomaint_localities = []
            #if len(param_t_localities) > 0:
            #    searchDomaint_localities.append(('address_id.city', 'in', param_t_localities))
                
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-map-marker'
            attribute.label = "locality"
            attribute.name = "locality"
            
            #searchDomaint_localities = list(searchDomain)
            
            _logger.info(param_t_localities)
            attribute.values = []
            eventos = request.env['event.event'].search(searchDomain)
            t_localities = eventos.mapped('address_id.city')
            t_localities = OrderedDict.fromkeys(t_localities).keys()
            for locality in t_localities:
                value = attrValueDirectorio()
                value.num = eventos.search_count(searchDomainevents+[('address_id.city','=',locality)])
                value.name = locality or 'none'
                value.label = locality or "Sin Definir"
                value.sel = True if locality in param_t_localities or (not locality and value.name in param_t_localities) else False
                attribute.values.append(value)
            attributes.append(attribute)

	    attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-map-marker'
            attribute.label = "Services"
            attribute.name = "service"

	    attribute.values = []
            t_services = eventos.mapped('address_id.services')
	    t_services = OrderedDict.fromkeys(t_services).keys()
            establishments = request.env['turismo.establishment']
            for service in t_services:
                value = attrValueDirectorio()
                value.num = eventos.search_count(searchDomainevents+[('address_id.services','in',service.id)])
                value.name = service.id
                value.label = service.name
                value.sel = True if service.id in param_services else False
                attribute.values.append(value)
            attributes.append(attribute)

        elif product_type == 'vinagre':
            searchDomain = [('product_tur_id.website_published','=',True)]
            
            param_type_vinagre = []
            param_type_grape = []
            param_awards = []
            param_anhada = []
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if any(params['search']):
                    searchDomain.append('|')
                    searchDomain.append(('name', 'ilike', params['search']))
                    searchDomain.append(('description', 'ilike', params['search']))
                    
                # Wine type
                param_type_vinagre_k = [s for s in params if s.startswith("type_vinagre-")]
                param_type_vinagre = [werkzeug.url_unquote_plus(params[s]) for s in param_type_vinagre_k]
                
                # Grape type
                param_type_grape_k= [s for s in params if s.startswith("type_grape-")]
                param_type_grape = [werkzeug.url_unquote_plus(params[s]).lower() for s in param_type_grape_k]
                
                # Awards
                param_awards_k = [s for s in params if s.startswith("awards-")]
                param_awards = [werkzeug.url_unquote_plus(params[s]).lower() for s in param_awards_k]
                
                # Anhada
                param_anhada_k = [s for s in params if s.startswith("anhada-")]
                param_anhada = [werkzeug.url_unquote_plus(params[s]).lower() for s in param_anhada_k]
                    
            searchDomainVinagres = list(searchDomain)
            if any(param_type_vinagre):
                searchDomainVinagres.append(('product_tur_id.typewine', 'in', [False if q=='none' else q for q in param_type_vinagre]))
            if any(param_type_grape):
                searchDomainVinagres.append(('product_tur_id.grape', 'in', [False if q=='none' else q for q in param_type_grape]))
            if any(param_awards):
                searchDomainVinagres.append(('product_tur_id.awards', 'in', [False if q=='none' else q for q in param_awards]))
            if any(param_anhada):
                searchDomainVinagres.append(('product_tur_id.anho', 'in', [False if q=='none' else q for q in param_anhada]))
            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-glass'
            attribute.label = "Type Vinagre"
            attribute.name = "type_vinagre"
            wine_tags = request.env['turismo.vinagre.tag'].search([], order='name')
            wine_tags = wine_tags.mapped('name')
            wine_tags = OrderedDict.fromkeys(wine_tags).keys()
            attribute.values = []
            for tag in wine_tags: 
                value = attrValueDirectorio()
                value.num = request.env['turismo.contract_product_customer'].search_count(searchDomainVinagres+[('product_tur_id.type_product','=','vinagre'),
                                                                                             ('product_tur_id.typevinagre','=',tag)])
                value.name = value.label = tag
                attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-tint'
            attribute.label = "Grape type"
            attribute.name = "type_grape"
            grape_tags = request.env['turismo.grape.tag'].search([], order='name')
            grape_tags = grape_tags.mapped('name')
            grape_tags = OrderedDict.fromkeys(grape_tags).keys()
            attribute.values = []
            for tag in grape_tags: 
                value = attrValueDirectorio()
                value.num = request.env['turismo.contract_product_customer'].search_count(searchDomainVinagres+[('product_tur_id.type_product','=','wine'),
                                                                                             ('product_tur_id.grape','=',tag)])
                value.name = value.label = tag
                attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.icon = 'fa-star'
            attribute.label = "Awards"
            attribute.name = "awards"
            award_tags = request.env['turismo.award.tag'].search([], order='name')
            award_tags = award_tags.mapped('name')
            award_tags = OrderedDict.fromkeys(award_tags).keys()
            attribute.values = []
            for tag in award_tags: 
                value = attrValueDirectorio()
                value.num = request.env['turismo.contract_product_customer'].search_count(searchDomainVinagres+[('product_tur_id.type_product','=','vinagre'),
                                                                                             ('product_tur_id.awards','=',tag)])
                value.name = value.label = tag
                attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.icon = 'fa-calendar'
            attribute.label = "Year"
            attribute.name = "anhada"
            wines = request.env['product.template'].search([('type_product','=','vinagre')], order='anho')
            anhos = wines.mapped('anho')
            anhos = OrderedDict.fromkeys(anhos).keys()
            attribute.values = []
            for anho in anhos:
                value = attrValueDirectorio()
                value.num = request.env['turismo.contract_product_customer'].search_count(searchDomainVinagres+[('product_tur_id.type_product','=','vinagre'),
                                                                                             ('product_tur_id.anho','=',anho)])
                value.name = value.label = anho
                attribute.values.append(value)
            attributes.append(attribute)
            
        return attributes
    
    def _sanitize_cnif(self, cnif):
        if cnif:
            matchObj = re.match(r'^\w\w', cnif, re.M|re.I)
            if not matchObj:
                cnif = "ES" + cnif
        return cnif
    
    @http.route(['/create_link'], type='http', auth="public", website=True)
    def solicitud_link(self):
        services = request.env['product.template'].search([('service','=',True)]);
        values = {
            'services': services
        }
        return request.website.render("aloxa_turismo_theme.create_link", values)
    
    @http.route(['/register_user',
                 '/edit_user',
                 '/register_company'], type='http', auth="public", website=True)
    def registrarse_edit_usuario(self):
        state_orm = request.env['res.country.state']
        states_ids = state_orm.search([])
        values = dict({'states':states_ids})
        
        if request.httprequest.path.startswith('/edit_user'):
            cr, uid, context = request.cr, request.uid, request.context
            if not request.session.uid:
                return login_redirect()
            user = request.env['res.users'].search([('id','=',uid)])
            values.update({ 'partner': user.partner_id })
            return request.website.render("aloxa_turismo_theme.edit_user", values)
        elif request.httprequest.path.startswith('/register_company'):
            return request.website.render("aloxa_turismo_theme.register_company", values)
        else:
            return request.website.render("aloxa_turismo_theme.register_user", values)
    
    @http.route(['/_edit_user'], type='http', auth="public", methods=["POST"], website=True)
    def edit_usuario(self, name, email, phone=None, old_password=None, password=None, street=None, city=None, 
                      province=None, postalcode=None, website_url=None, cnif=None, image=None, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        
        user = request.env['res.users'].search([('id','=',uid)])
        if password and old_password != user.password:
            return http.redirect_with_hash('/edit_user')
        
        ModelCountry = request.env['res.country']
        country_id = ModelCountry.search([('name','=','Spain')])
        
        cnif = self._sanitize_cnif(cnif)
        
        regPartnerData = {
            'name':name,
            'email': email,
            'image': base64.encodestring(image.read()),
            'website': website_url,
            'street': street,
            'zip': postalcode,
            'state_id': province,
            'city': city,
            'phone': phone,
            'country_id': country_id.id,
            'vat': cnif,
        }
        
        regUserData = {
            'login': email
        }
        if image.filename:
            regPartnerData.update({'image': base64.encodestring(image.read())})
        if password:
            regUserData.update({'password':password})
        
        user.write(regUserData)
        user.partner_id.write(regPartnerData)
        return http.redirect_with_hash('/panel')
        
    @http.route(['/_create_user'], type='http', auth="public", methods=["POST"], website=True)
    def crear_usuario(self, name, email, password, iscompany=False, **kw):
        #Validacion del recaptcha
        payload = {'secret': request.website.recaptcha_private_key, 'response': kw['g-recaptcha-response']}
        #Cotejamos con el API de Google la validacion
        res = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
        success = request.website.is_captcha_valid(payload)
        #if not success:
        #    return http.redirect_with_hash('/registrarse')
        
        # Crear Usuario
        db, login, password_f = request.registry['res.users'].signup(request.cr, 
                                                SUPERUSER_ID, 
                                                {
                                                    'name': name,
                                                    'login': email,
                                                    'password': password,
                                                    'active': True,
                                                })
        request.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
        uid = request.session.authenticate(db, login, password_f)
        if not uid:
            raise SignupError(_('Authentification Failed.'))
        
        kw['cnif'] = cnif = self._sanitize_cnif(kw['cnif'])
        
        # Actualizar Partner
        user_partner = request.env['res.users'].browse(uid).partner_id
        regData = {
            'name':name,
            'email': email,
            'customer': True,
            'active': True,
            'website_published': True,
            'vat': kw['cnif'],
        }
        if iscompany:
            ModelCountry = request.env['res.country']
            country_id = ModelCountry.search([('name','=','Spain')])
            regData.update({
                'supplier': True,
                'is_company': True,
                'website': kw['website_url'],
                'street': kw['street'],
                'state_id': kw['province'],
                'zip': kw['postalcode'],
                'city': kw['city'],
                'phone': kw['phone'],
                'country_id': country_id.id,
            })
            if kw['image'].filename:
                regData.update({'image': base64.encodestring(kw['image'].read())});
        else:
            regData.update({
                'turist': True
            })
            
        user_partner.sudo().write(regData)
        return http.redirect_with_hash('/panel')
    
    @http.route(['/create_establishment',
                 '/edit_establishment/<model("turismo.establishment"):stablisment>'], type='http', auth="public", methods=["GET"], website=True)
    def nuevo_edit_establishment(self, stablisment=None):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        user = request.env['res.users'].search([('id','=',uid)])
        state_orm = request.env['res.country.state']
        states_ids = state_orm.search([])
        services_orm = request.env['establishment.services']
        services_ids = services_orm.search([])
        
        values = {
            'partner': user.partner_id,
            'states': states_ids,
            'est': stablisment,
            'services': services_ids,
        }
        return request.website.render('aloxa_turismo_theme.create_establishment', values)
    @http.route(['/_create_edit_establishment'], type='http', auth="public", methods=["POST"], website=True)
    def crear_edit_establishment(self, name, type_s, image, phone=None,street=None, city=None, province=None, postalcode=None, url_trip=None, desc=None, est_id=None, **kwargs):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        user = request.env['res.users'].search([('id','=',uid)])
        ModelCountry = request.env['res.country']
        country_id = ModelCountry.search([('name','=','Spain')])
        Modelestablishment = request.session.model('turismo.establishment')
        
        # Services
        param_services_k = [s for s in kwargs if s.startswith("service-")]
        param_services = [int(werkzeug.url_unquote_plus(kwargs[s]).lower()) for s in param_services_k]
        
        modelData = {
            'name': name,
            'type_s': type,
            'street': street,
            'zip': postalcode,
            'state_id': province,
            'country_id': country_id.id,
            'phone': phone,
            'use_parent_address': False,
            'city': city,
            'tripadvisor_url': url_trip,
            'description': desc,
            'res_partner_id': user.partner_id.id,
            'services': [(6, 0, param_services)] if not len(param_services) == 0 else [],
        }
        
        if image.filename:
            modelData.update({'image': base64.encodestring(image.read())})
        if not est_id:
            establishment_id = Modelestablishment.create(modelData)
            establishment_id = Modelestablishment.browse([establishment_id])
        else:
            establishment_id = Modelestablishment.browse([int(est_id)])
            establishment_id.write(modelData)
        return http.redirect_with_hash('/panel/establishments#%s' % slug(establishment_id))
    
    @http.route(['/preview/establishment/<model("turismo.establishment"):establishment>',
                 '/preview/product/<model("product.template"):product>',
                 ], type='http', auth="user", methods=["GET"], website=True)
    def preview(self, product=None, establishment=None):
        if not request.session.uid:
            return login_redirect()
        if establishment:
            events = request.env['event.event'].search([('website_published','=',True),
                                                    ('organizer_id','=',establishment.partner_id.id),
                                                    ('date_end','>=',datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT))])
            products = request.env['product.template'].search([('seller_ids.name','in',[establishment.partner_id.id])])
            values = {
                'establishment': establishment,
                'events': events,
                'products_table': table_compute().process_products_establishment(products),
            }
            return request.website.render("aloxa_turismo_theme.establishment_details", values)
        else:
            values = {
                'contract_product': product
            }
            return request.website.render("aloxa_turismo_theme.product_details", values)
    
    @http.route(['/_add_product'], type='http', auth="user", methods=["POST"], website=True)
    def add_product(self, est_id, product):
        if not request.session.uid:
            return login_redirect()
        
        ModelTurismoEst = request.env['turismo.establishment']
        establishment_id = ModelTurismoEst.browse([int(est_id)])
        ModelSupplierInfo = request.env['product.supplierinfo']
        supplierinfo_id = ModelSupplierInfo.search([('name','=',establishment_id.partner_id.id),('product_tmpl_id','=',product)])
        if not supplierinfo_id:
            supplierinfo_id = ModelSupplierInfo.create({
                'name': establishment_id.partner_id.id,
                'delay': 1,
                'min_qty': 0.0,
                'sequence': 1,
                'product_tmpl_id': product
            })
        ModelProductTemplate = request.env['product.template']
        product_id = ModelProductTemplate.browse([int(product)])
        product_id.seller_ids |= supplierinfo_id
        return http.redirect_with_hash('/panel/establishments')
    
    @http.route(['/_add_image'], type='http', auth="user", methods=["POST"], website=True)
    def add_image(self, est_id, name, image):
        if not request.session.uid:
            return login_redirect()
        
        ModelTurismoEst = request.env['turismo.establishment']
        establishment_id = ModelTurismoEst.browse([int(est_id)])
        ModelEstImages = request.env['establishment.images']
        image_id = ModelEstImages.create({
            'name': name,
            'image': base64.encodestring(image.read()),
        })
        establishment_id.images |= image_id
        return http.redirect_with_hash('/panel/establishments')
    
    @http.route(['/_create_ticket'], type='http', auth="user", methods=["POST"], website=True)
    def create_ticket(self, event_id, name, deadline, price, seats_max):
        if not request.session.uid:
            return login_redirect()
        
        ModelEvent = request.env['event.event']
        event = ModelEvent.browse([int(event_id)])
        ModelEventTicket = request.env['event.event.ticket']
        ticket_id = ModelEventTicket.create({
            'name': name,
            'deadline': deadline, 
            'price': price, 
            'seats_max': seats_max,
            'event_id': event_id,
            'product_id': request.env['product.product'].search([('event_ok','=',True)], limit=1).id,
        })
        event.event_ticket_ids |= ticket_id
        return http.redirect_with_hash('/panel/establishments')
    
    @http.route(['/create_product',
                 '/edit_product/<model("product.template"):product>'], type='http', auth="user", methods=["GET"], website=True)
    def nuevo_edit_product(self, product=None):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        user = request.env['res.users'].search([('id','=',uid)])
        values = {
            'winecellars': request.env['turismo.establishment'].search([('res_partner_id','=',user.partner_id.id),('type','=','winecellar')]),
            'prod': product
        }
        return request.website.render('aloxa_turismo_theme.create_product', values)
    @http.route(['/_create_edit_product'], type='http', auth="user", methods=["POST"], website=True)
    def crear_edit_product(self, name, type, price, image=None, anhada=None, grape=None, subtype=None, winecellar=None, awards=None, desc=None, prod_id=None, vender=False):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        user = request.env['res.users'].search([('id','=',uid)])
        ModelProductTemplate = request.session.model('product.template')
        
        # FIXME: Super guarrada!
        if type == 'other':
            type = None
            
        recordValues = {
            'name': name,
            'type_product': type,
            'list_price': price,
            'description': desc,
            'website_published': False,
            'uom_id': 1,
            'uom_po_id': 1,
            'sale_ok': vender,
        }
        
        if image.filename:
            recordValues.update({'image': base64.encodestring(image.read())})
        
        if type in ['wine','vinagre']:
            ModelgrapeTag = request.env['turismo.grape.tag']
            grape_tag_id = ModelgrapeTag.search([('name','=',grape)])
            if not grape_tag_id:
                grape_tag_id = ModelgrapeTag.create({'name':grape})
                
            ModelAwardsTag = request.env['turismo.award.tag']
            awards_tag_id = ModelAwardsTag.search([('name','=',awards)])
            if not awards_tag_id:
                awards_tag_id = ModelAwardsTag.create({'name':awards})
            
            recordValues.update({
                'anho': anhada,
                'grape': grape_tag_id.id,
                'establishment_id': winecellar,
                'awards': [awards_tag_id.id],
            })
            if type == 'wine':
                ModelwineTag = request.env['turismo.wine.tag']
                wine_tag_id = ModelwineTag.search([('name','=',subtype)])
                if not wine_tag_id:
                    wine_tag_id = ModelwineTag.create({'name':subtype})
                recordValues.update({'typewine': wine_tag_id.id})
            elif type == 'vinagre':
                ModelVinagreTag = request.env['turismo.vinagre.tag']
                vinagre_tag_id = ModelVinagreTag.search([('name','=',subtype)])
                if not wine_tag_id:
                    vinagre_tag_id = ModelVinagreTag.create({'name':subtype})
                recordValues.update({'typevinagre': vinagre_tag_id.id})
                
        if not prod_id:
            product_template_id = ModelProductTemplate.create(recordValues)
            ModelProductSupplierInfo = request.session.model('product.supplierinfo')
            product_supplierinfo_id = ModelProductSupplierInfo.create({
                'name': user.partner_id.id,
                'delay': 1,
                'min_qty': 0.0,
                'sequence': 1,
                'product_tmpl_id': product_template_id
            })
            product_template_id = ModelProductTemplate.browse([product_template_id])
            product_template_id.write({'seller_ids': [ModelProductSupplierInfo.browse([product_supplierinfo_id])]})
        else:
            product_template_id = ModelProductTemplate.browse([int(prod_id)])
            product_template_id.write(recordValues);
        return http.redirect_with_hash('/panel/%ss#%s' % (type, slug(product_template_id)))
    
    @http.route(['/_create_link'], type='http', auth="user", methods=["POST"], website=True)
    def crear_link(self, typelink, image, date_start, date_end, est_id=None, prod_id=None):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        if est_id is None and prod_id is None:
            return http.redirect_with_hash('/panel/links')
        
        user = request.env['res.users'].search([('id','=',uid)])
        ModelProductContratadoCustomer = request.session.model('turismo.contract_product_customer')
        contract_product_customer_id = ModelProductContratadoCustomer.create({
            'partner_id': user.partner_id.id,
            'product_id': typelink,
            'establishment_id': est_id,
            'product_tur_id': prod_id,
            'image': base64.encodestring(image.read()),
            'fecha_inicio': date_start,
            'fecha_fin': date_end,
        })
        return http.redirect_with_hash('/panel/%s' % ('establishments' if est_id else 'products'))

    @http.route(['/create_event',
                 '/create_event/<model("turismo.establishment"):establishment>'], type='http', auth="user", methods=["GET"], website=True)
    def nuevo_evento(self, establishment=None):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        
        user = request.env['res.users'].search([('id','=',uid)])
        country_ids = request.env['res.country'].search([])
        states_ids = request.env['res.country.state'].search([])
        values = dict({
            'states': states_ids,
            'countries': country_ids,
        })
        if not establishment:
            values['establishments'] = request.env['turismo.establishment'].search([('res_partner_id','=',user.partner_id.id)])
        else:
            values['est_partner'] = establishment.partner_id
        
        return request.website.render("aloxa_turismo_theme.create_event", values)
    
    @http.route(['/_create_event'], type='http', auth="user", methods=["POST"], website=True)
    def crear_evento(self, organizer, name, date_begin, date_end, seats_min, seats_max, desc, street, province, postalcode, country, city):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        user = request.env['res.users'].search([('id','=',uid)])
        ModelEventEvent = request.session.model('event.event')
        ModelResPartner = request.env['res.partner']
        address_id = ModelResPartner.find_address_or_create(street, city, province, country, postalcode)
        
        event_id = ModelEventEvent.create({
            'name': name,
            'address_id': address_id.id,
            'organizer_id': organizer,
            'date_begin': date_begin,
            'date_end': date_end,
            'seats_min': seats_min,
            'seats_max': seats_max,
            'description': desc,
            'user_id': uid,
            'website_published': True,
        })
        
        est = request.env['turismo.establishment'].search([('partner_id.id','=',organizer)], limit=1)
        return http.redirect_with_hash('/panel/establishments#%s' % slug(est))
    
    @http.route(['/panel',
                 '/panel/establishments',
                 '/panel/products',
                 '/panel/events',
                 '/panel/invoices',
                 '/panel/links',
                 '/panel/wines'], type='http', auth="user", website=True)
    def panel_customer(self):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
            
        user = request.env['res.users'].search([('id','=',uid)])
        values = dict()
        if request.httprequest.path.endswith('/products'):
            values['panel'] = 'products'
        elif user.partner_id.is_company and request.httprequest.path.endswith('/establishments'):
            values['services'] = request.env['product.template'].search([
                ('service', '=', True)
            ]);
            values['panel'] = 'establishments'
            values['products_partner'] = request.env['product.template'].search([
                ('seller_ids.name', 'in', [user.partner_id.id])
            ])
            values['establishments'] = request.env['turismo.establishment'].search([
                ('res_partner_id', '=', user.partner_id.id)
            ])
        elif user.partner_id.is_company and request.httprequest.path.endswith('/events'):
            values['panel'] = 'events'
            establishment_ids = request.env['turismo.establishment'].search([
                ('res_partner_id', '=', user.partner_id.id)
            ]).mapped('partner_id.id')
            event_ids = request.env['event.event'].search([
                ('organizer_id', 'in', establishment_ids)
            ])
            values['events'] = event_ids
        elif user.partner_id.is_company and request.httprequest.path.endswith('/links'):
            values['panel'] = 'links'
            products_c_ids = user.partner_id.contract_product_customer_ids
            values['links'] = products_c_ids
            values['services'] = request.env['product.template'].search([('service','=',True)]);
        elif user.partner_id.is_company and request.httprequest.path.endswith('/invoices'):
            values['panel'] = 'invoices'
            invoice_ids = request.env['account.invoice'].search([
                ('partner_id', '=', user.partner_id.id)
            ], order="date_invoice DESC")
            values['invoices'] = invoice_ids
        elif user.partner_id.is_company and request.httprequest.path.endswith('/wines'):
            values['panel'] = 'wines'
            values['services'] = request.env['product.template'].search([
                ('service', '=', True)
            ])
            values['products'] = request.env['product.template'].search([
                ('seller_ids.name', 'in', [user.partner_id.id])
            ])
        else:
            values['panel'] = 'general'
            if user.partner_id.is_company:
                values['num_products'] = request.env['product.template'].search_count([
                    ('seller_ids.name', 'in', [user.partner_id.id])
                ])
                establishments = request.env['turismo.establishment'].search([
                    ('res_partner_id', '=', user.partner_id.id)
                ])
                values['num_establishments'] = len(establishments)
                num_events = 0
                for est in establishments:
                    num_events = num_events + request.env['event.event'].search_count([
                        ('organizer_id', '=', est.partner_id.id)
                    ])
                values['num_eventos'] = num_events
                values['num_links'] = len(user.partner_id.contract_product_customer_ids)
        
        values['partner'] = user.partner_id
        return request.website.render("aloxa_turismo_theme.panel_customer", values)
    
    @http.route(['/invoice/download'], type='http', auth="user", methods=['GET'], website=True)
    def generate_invoice_report(self, id):
        if not request.session.uid:
            return {'error': 'anonymous_user'}

        cr, uid, context = request.cr, request.uid, request.context
        User = request.registry['res.users']
        current_user = User.browse(cr, SUPERUSER_ID, uid, context=context)
        childs_users = request.env['res.users'].search([('partner_id.parent_id', '=', current_user.partner_id.id)])
        partner_ids = [current_user.partner_id.id]
        for user_child in childs_users:
            partner_ids.append(user_child.partner_id.id)
            
        domain = [('partner_id', 'in', partner_ids),('id', '=', id)]
        invoice = request.env['account.invoice'].search(domain, limit=1)
        if invoice:
            report_data = request.env['report'].get_pdf(invoice, 'account.report_invoice')
            return request.make_response(
                            report_data, [('Content-Type', 'application/pdf'),
                              ('Content-Disposition',
                               content_disposition('Factura-%s.pdf' % str(invoice.number)))])
        return request.redirect('/panel')

    @http.route([
                 # '/directorio',
                 # '/directorio/categoria/<model("product.public.category"):category>',
                 '/directory/establishments',
                 '/establishment/<model("turismo.establishment"):establishment>',
                 '/directory/wines',
                 '/wine/<model("turismo.contract_product_customer"):contracted_product>',
                 # '/directorio/vinagres',
                 '/directory/events',
                 '/event/<model("event.event"):event>'
                 ], type='http', auth="public", methods=['GET'], website=True)
    def directory(self, establishment=None, event=None, contracted_product=None, **params):
        categories = []
        #pydevd.settrace("10.0.3.1")
        attrib_list = request.httprequest.args.getlist('attrib')

        # Por defecto vista 'grid'
        if 'directory_view' not in request.session:
            request.session['directory_view'] = 'grid'

        # Si viene con 'slug' forzas la vista a 'form'
        is_direct_form = False
        if establishment or event or contracted_product:
            is_direct_form = True
            params = {}  # Reset params

        keep_url = '/directory'
        category_type = None
        if request.httprequest.path.startswith('/directory/establishments') or establishment:
            keep_url = '/directory/establishments'
            category_type = "establishment"
            categories = request.env['product.public.category'].search(['&',('parent_id', '=', False),('link', '=', True),('name', '=', 'establishments')])
        elif request.httprequest.path.startswith('/directory/wines') or contracted_product:
            keep_url = '/directory/wines'
            category_type = "wine"
            categories = request.env['product.public.category'].search(['&',('parent_id', '=', False),('link', '=', True),('name', '=', 'wines')])
            # Los wines no tienen mapa
            if request.session['directory_view'] == 'map':
                request.session['directory_view'] = 'grid'
#         elif request.httprequest.path.startswith('/directorio/vinagres'):
#             keep_url = '/directorio/vinagres'
#             category_type = "vinagre"
#             categories = request.env['product.public.category'].search(['&',('parent_id', '=', False),('link', '=', True),('name', '=', 'Vinagres')])
#             # Los vinagres no tienen mapa
#             if request.session['directory_view'] == 'map':
#                 request.session['directory_view'] = 'grid'
        elif request.httprequest.path.startswith('/directory/events') or event:
            keep_url = '/directory/events'
            category_type = "event"

        keep = QueryURL(keep_url, search='', attrib=attrib_list)

        # orderby
        orderby = str(params['orderby'].lower()) if params and 'orderby' in params.keys() else 'name'
        bins, numres = self._get_banners_directorio(orderby, product_type=category_type, params=params)

        values = {
            'orderby': orderby,
            'categories': categories,
            'category_type': category_type,
            'attributes': self._create_directory_attributes(product_type=category_type, params=params),
	    'keep': keep,
            'bins': bins,
            'numresults': numres,
            'rows': 4,
            'search': params['search'] if params and 'search' in params.keys() else '',
            'is_direct_form': is_direct_form,
        }
	if "date_event" in params:
		values.update({'date_event':params['date_event']})
	else:
		values.update({'date_event':datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)})		

        if request.session['directory_view'] == 'form' or is_direct_form:
            # Validar SRI
            sri = False
            if params and 'sri' in params.keys():
                sri = int(params['sri'])-1
                if sri < 0:
                    sri = 0
                elif sri >= len(request.session['search_records']):
                    sri = len(request.session['search_records'])-1

            if category_type == 'establishment':
                est_model = request.env['turismo.establishment']
                if not establishment and request.session['search_records']:
                    if not sri:
                        sri = 0
                    establishment = est_model.browse([request.session['search_records'][sri]])

                if establishment:
                    # Buscar SRI del establishment
                    if not sri:
                        count = 0
                        for rec_id in request.session['search_records']:
                            if establishment.id == rec_id:
                                sri = count
                                break
                            count = count+1

                    prev_est = False
                    next_est = False
                    if request.session['search_records']:
                        if sri > 0:
                            prev_est = est_model.browse([request.session['search_records'][sri-1]])
                        if sri < len(request.session['search_records'])-1:
                            next_est = est_model.browse([request.session['search_records'][sri+1]])

                    events = request.env['event.event'].search([
                                        ('website_published', '=', True),
                                        ('organizer_id', '=', establishment.partner_id.id),
                                        ('date_end', '>', datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT))
                                    ])
                    products = request.env['product.template'].search([('website_published','=',True),
                                                                       ('establishment_id','=',establishment.id)])
                    # RELATED ESTABLISHMENTS
                    gKey = request.website.google_maps_key
                    client = googlemaps.Client(gKey)

                    city_ests = est_model.search([
                        ('city', '=ilike', establishment.city),
                        ('id', '!=', establishment.id),
                    ])

                    related_est = []
                    origins = [{'lat': establishment.partner_latitude, 'lng': establishment.partner_longitude}]
                    destinations = []
                    for est in city_ests:
                        related_est.append([est, 0])
                        destinations.append(
                            (est.partner_latitude, est.partner_longitude)
                        )

                    if any(destinations):
                        matrix = client.distance_matrix(origins, destinations)
                        if any(matrix['rows'][0]['elements']):
                            for index in range(len(matrix['rows'][0]['elements'])):
                                elm = matrix['rows'][0]['elements'][index]
                                if elm['status'] == 'OK':
                                    related_est[index][1] = elm['distance']['value']

                    # Search lower distance (Bubble Sort... slow life :B)
                    for passnum in range(len(related_est)-1, 0, -1):
                        for i in range(passnum):
                                if related_est[i][1] > related_est[i+1][1]:
                                    temp = related_est[i]
                                    related_est[i] = related_est[i+1]
                                    related_est[i+1] = temp

                    values.update({
                        'sri': sri+1,
                        'prev_est': prev_est,
                        'next_est': next_est,
                        'establishment': establishment,
                        'events': events,
                        'related': related_est[:6],
                        'products_table': table_compute().process_products_establishment(products),
                    })
                else:
                    request.session['directory_view'] = 'grid'
            elif category_type == 'wine':
                if not contracted_product and request.session['search_records']:
                    if not sri:
                        sri = 0
                    contracted_product = request.env['turismo.contract_product_customer'].browse([request.session['search_records'][sri]])
                if contracted_product:
                    # Buscar SRI del establishment
                    if not sri:
                        count = 0
                        for rec_id in request.session['search_records']:
                            if contracted_product.id == rec_id:
                                sri = count
                                break
                            count = count+1
    
                    prev_event = False
                    next_event = False
                    if request.session['search_records']:
                        if sri > 0:
                            prev_event = request.env['turismo.contract_product_customer'].browse([request.session['search_records'][sri-1]])
                        if sri < len(request.session['search_records'])-1:
                            next_event = request.env['turismo.contract_product_customer'].browse([request.session['search_records'][sri+1]])
                    related_prods = request.env['turismo.contract_product_customer'].search([('id', '!=', contracted_product.id),('partner_id', '=', contracted_product.partner_id.id)])
                    values.update({
                        'sri': sri+1,
                        'prev_prod': prev_event,
                        'next_prod': next_event,
                        'contracted_product': contracted_product,
                        'related': related_prods,
                    })
                else:
                    request.session['directory_view'] = 'grid'
            elif category_type == 'event':
                ev_model = request.env['event.event']
                if not event and request.session['search_records']:
                    if not sri:
                        sri = 0
                    event = ev_model.browse([request.session['search_records'][sri]])
                if event:
                    # Buscar SRI del event
                    if not sri:
                        count = 0
                        for rec_id in request.session['search_records']:
                            if event.id == rec_id:
                                sri = count
                                break
                            count = count+1

                    prev_event = False
                    next_event = False
                    if request.session['search_records']:
                        if sri > 0:
                            prev_event = ev_model.browse([request.session['search_records'][sri-1]])
                        if sri < len(request.session['search_records'])-1:
                            next_event = ev_model.browse([request.session['search_records'][sri+1]])
                    
                    # RELATED EVENTS
                    gKey = request.website.google_maps_key
                    client = googlemaps.Client(gKey)

                    city_events = ev_model.search([
                        ('address_id.city', '=ilike', event.address_id.city),
                        ('id', '!=', event.id),
                    ])

                    related_events = []
                    origins = [{'lat': event.address_id.partner_latitude, 'lng': event.address_id.partner_longitude}]
                    destinations = []
                    for ev in city_events:
                        related_events.append([ev, 0])
                        destinations.append(
                            (ev.address_id.partner_latitude, ev.address_id.partner_longitude)
                        )

                    if any(destinations):
                        matrix = client.distance_matrix(origins, destinations)
                        if any(matrix['rows'][0]['elements']):
                            for index in range(len(matrix['rows'][0]['elements'])):
                                elm = matrix['rows'][0]['elements'][index]
                                if elm['status'] == 'OK':
                                    related_events[index][1] = elm['distance']['value']

                    # Search lower distance (Bubble Sort... slow life :B)
                    for passnum in range(len(related_events)-1, 0, -1):
                        for i in range(passnum):
                            if related_events[i][1] > related_events[i+1][1]:
                                temp = related_events[i][1]
                                related_events[i] = related_events[i+1]
                                related_events[i+1] = temp

                    values.update({
                        'sri': sri+1,
                        'prev_event': prev_event,
                        'next_event': next_event,
                        'event': event,
                        'related': related_events[:6],
                    })
                else:
                    request.session['directory_view'] = 'grid'

        return request.website.render("aloxa_turismo_theme.directory", values)

    @http.route([
                 '/rutas'
                 ], type='http', auth="public", methods=['GET'], website=True)
    def rutas(self):
        values = {}
        return request.website.render("aloxa_turismo_theme.pageRoutes", values)
    
    
    ## JSON-RPC
    @http.route([
                '/_set_directory_view/form',
                '/_set_directory_view/grid',
                '/_set_directory_view/list',
                '/_set_directory_view/map'], type='json', auth="public", website=True)
    def set_directory_view(self):
        if request.httprequest.path.endswith('/grid'):
            request.session['directory_view'] = 'grid'
        elif request.httprequest.path.endswith('/list'):
            request.session['directory_view'] = 'list'
        elif request.httprequest.path.endswith('/map'):
            request.session['directory_view'] = 'map'
        elif request.httprequest.path.endswith('/form'):
            request.session['directory_view'] = 'form'
        return []

    ## JSON-RPC
#     @http.route(['/_upload_image'], type='json', auth="public", website=True)
#     def upload_image(self, fileimage):
#         try:
#             #pydevd.settrace("10.0.3.1")
#             attachment_id = Model.create({
#                 'name': ufile.filename,
#                 'datas': base64.encodestring(ufile.read()),
#                 'datas_fname': ufile.filename,
#                 'res_model': model,
#                 'res_id': int(id),
#                 'dolmar_type': dolmar_type
#             }, request.context)
#             args = {
#                 'filename': ufile.filename,
#                 'id':  attachment_id,
#                 'dolmar_type': dolmar_type
#             }
#         except Exception:
#             args = {'error': "Something horrible happened"}
#             _logger.exception("Fail to upload attachment %s" % ufile.filename)
#         return out % (simplejson.dumps(callback), simplejson.dumps(args))
