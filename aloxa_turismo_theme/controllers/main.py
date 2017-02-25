# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID, http, tools
from openerp.http import request
from openerp.addons.website.controllers.main import Website
# from openerp.tools import image_resize_and_sharpen, image_save_for_web
from datetime import datetime
from html_table import table_compute
from collections import OrderedDict
from openerp.addons.web.controllers.main import login_redirect, content_disposition
from openerp.addons.website.models.website import slug
# from openerp.addons.auth_signup.controllers.main import AuthSignupHome
import requests
import re
import logging
import base64
import werkzeug.utils
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
    producto_contratado = None
    establecimiento = None
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
        # Recoger los establecimientos
        searchDomain = []
        if not product_category and (product_type == "establecimiento" or not product_type):
            searchDomain.append(('website_published', '=', True))
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if any(params['search']):
                    searchDomain.append('|')
                    searchDomain.append(('name', 'ilike', params['search']))
                    searchDomain.append(('descripcion', 'ilike', params['search']))
                # Localidades
                localidades_k = [s for s in params if s.startswith("localidad-")]
                localidades = [werkzeug.url_unquote_plus(params[s]) for s in localidades_k]
                if any(localidades):
                    searchDomain.append(('city', 'in', [False if q == 'none' else q for q in localidades]))
                # Servicios
                services_k = [s for s in params if s.startswith("service-")]
                services = [int(werkzeug.url_unquote_plus(params[s])) for s in services_k]
                if any(services):
                    searchDomain.append(('services', 'in', services))

                # pydevd.settrace("10.0.3.1")
                param_tipo_est_k = [s for s in params
                                    if s.startswith("tipo_establecimiento-")]
                param_tipo_est = [werkzeug.url_unquote_plus(params[s])
                                  for s in param_tipo_est_k]
                if len(param_tipo_est) > 0:
                    searchDomain.append(('tipo', 'in', param_tipo_est))

            # OrderBy
            if orderby == 'direccion':
                orderby_key = 'street'
            else:
                orderby_key = 'name'

            registros = request.env['turismo.establecimiento']\
                .search(searchDomain).sorted(key=lambda r: r[orderby_key])
            request.session['search_records'] = registros.mapped('id')
            for reg in registros:
                tmp_banner = htmlBannerDirectorio()
                tmp_banner.establecimiento = reg
                events = request.env['event.event'].search([
                                    ('website_published', '=', True),
                                    ('organizer_id', '=', reg.partner_id.id),
                                    ('date_end', '>=', datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT))
                                ], limit=4)
                tmp_banner.events = events
                banners_directorio.append(tmp_banner)
        elif product_type == "evento":
            searchDomain.append(('website_published','=',True))
            searchDomain.append(('date_end','>=',datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)))
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if len(params['search']) > 0:
                    searchDomain.append('|')
                    searchDomain.append(('name', 'ilike', params['search']))
                    searchDomain.append(('descripcion', 'ilike', params['search']))
                # Localidades
                localidades_k = [s for s in params if s.startswith("localidad-")]
                localidades = [werkzeug.url_unquote_plus(params[s]) for s in localidades_k]
                if len(localidades) > 0:
                    searchDomain.append(('organizer_id.city', 'in', [False if q=='none' else q for q in localidades]))
            
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
                searchDomain.append(('product_tur_id.tipo_producto', '=', product_type))
            
            #pydevd.settrace("10.0.3.1")
            if params and 'search' in params.keys():
                if len(params['search']) > 0:
                    searchDomain.append('|')
                    searchDomain.append(('product_tur_id.name', 'ilike', params['search']))
                    searchDomain.append(('product_tur_id.description', 'ilike', params['search']))
                if 'anhada' in params.keys() and len(params['anhada']) > 0:
                    searchDomain.append(('product_tur_id.anho', '=', params['anhada']))
                if 'tipo_vino' in params.keys() and len(params['tipo_vino']) > 0:
                    searchDomain.append(('product_tur_id.tipovino', '=', params['tipo_vino'].lower()))
                if 'tipo_vinagre' in params.keys() and len(params['tipo_vinagre']) > 0:
                    searchDomain.append(('product_tur_id.tipovinagre', '=', params['tipo_vinagre'].lower()))
                if 'tipo_uva' in params.keys() and len(params['tipo_uva']) > 0:
                    searchDomain.append(('product_tur_id.uva', '=', params['tipo_uva'].lower()))
                if 'premios' in params.keys() and len(params['premios']) > 0:
                    searchDomain.append(('product_tur_id.premios', '=', params['premios'].lower()))
                if 'localidad' in params.keys() and len(params['localidad']) > 0:
                    searchDomain.append(('product_tur_id.city', '=', params['localidad'].lower()))
            # OrderBy
            if orderby == 'precio':
                orderby_key = 'list_price'
            else:
                orderby_key = 'name'
            
            productos_contratados = request.env['turismo.producto_contratado_cliente'].search(searchDomain).sorted(key=lambda r: r.product_tur_id[orderby_key])
            request.session['search_records'] = productos_contratados.mapped('id')
            num_items = len(productos_contratados)
            for i in range(num_items):
                tmp_banner = htmlBannerDirectorio()
                tmp_banner.producto_contratado = productos_contratados[i]
                banners_directorio.append(tmp_banner)
                
        # Mezclar items
        #num_items = len(banners_directorio)
        #random_indices = random.sample(range(num_items), num_items)
        #banners_directorio = [ banners_directorio[i] for i in random_indices ]
        
        # Generar tabla HTML
        return (table_compute().process_directory(banners_directorio), len(banners_directorio))
    
    
    def _create_directory_attributes(self, product_type = None, params = None):
        attributes = []
        
        if product_type == 'establecimiento':
            searchDomain = [('website_published','=',True)]
            
            param_tipo_establecimiento = []
            param_localidades = []
            param_services = []
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if len(params['search']) > 0:
                    searchDomain.append('|')
                    searchDomain.append(('name', 'ilike', params['search']))
                    searchDomain.append(('descripcion', 'ilike', params['search']))
                    
                # Localidades
                param_localidades_k = [s for s in params if s.startswith("localidad-")]
                param_localidades = [werkzeug.url_unquote_plus(params[s]) for s in param_localidades_k]
                
                # Tipo Establecimiento
                param_tipo_establecimento_k = [s for s in params if s.startswith("tipo_establecimiento-")]
                param_tipo_establecimiento = [werkzeug.url_unquote_plus(params[s]) for s in param_tipo_establecimento_k]
     
                # Tipo Establecimiento
                param_services_k = [s for s in params if s.startswith("service-")]
                param_services = [int(werkzeug.url_unquote_plus(params[s])) for s in param_services_k]
    
            searchDomainEstablecimientos = list(searchDomain)
            searchDomainLocalidades = []
            searchDomainServices = []
            searchDomainTipos = []
            if any(param_localidades):
                searchDomainLocalidades.append(('city', 'in', [False if q=='none' else q for q in param_localidades]))
            if any(param_services):
                searchDomainServices.append(('services', 'in', [False if q=='none' else q for q in param_services]))
            if any(param_tipo_establecimiento):
                searchDomainTipos.append(('tipo', 'in', [False if q=='none' else q for q in param_tipo_establecimiento])) 
            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-tag'
            attribute.label = "Tipo"
            attribute.name = "tipo_establecimiento"    
            attribute.values = []
            value = attrValueDirectorio()
            value.label = 'Bodegas'
            value.name = 'bodega'
            value.sel = True if value.name in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+searchDomainLocalidades+searchDomainServices+[('tipo','=','bodega')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Restaurantes'
            value.name = 'restaurante'
            value.sel = True if value.name in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+searchDomainLocalidades+searchDomainServices+[('tipo','=','restaurante')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Hospedajes'
            value.name = 'hospedaje'
            value.sel = True if value.name in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+searchDomainLocalidades+searchDomainServices+[('tipo','=','hospedaje')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Viñedos'
            value.name = 'vinhedo'
            value.sel = True if value.name in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+searchDomainLocalidades+searchDomainServices+[('tipo','=','vinhedo')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Arte y Cultura'
            value.name = 'cultural'
            value.sel = True if value.name in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+searchDomainLocalidades+searchDomainServices+[('tipo','=','cultural')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Vinotecas'
            value.name = 'vinoteca'
            value.sel = True if value.name in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+searchDomainLocalidades+searchDomainServices+[('tipo','=','vinoteca')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Otros'
            value.name = 'otro'
            value.sel = True if value.name in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+searchDomainLocalidades+searchDomainServices+[('tipo','=','otro')])
            attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-cubes'
            attribute.label = "Servicios"
            attribute.name = "service"
            
            attribute.values = []
            services = request.env['establecimiento.services'].search([])
            establecimientos = request.env['turismo.establecimiento']
            for service in services:
                value = attrValueDirectorio()
                value.num = establecimientos.search_count(searchDomainEstablecimientos+searchDomainLocalidades+searchDomainTipos+[('services','in',[service.id])])
                value.name = service.id
                value.label = service.name
                value.sel = True if service.id in param_services else False
                attribute.values.append(value)
            attributes.append(attribute)
                            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-map-marker'
            attribute.label = "Localidad"
            attribute.name = "localidad"
            
            #searchDomainLocalidades = list(searchDomain)
            #if len(param_tipo_establecimiento) > 0:
            #    searchDomainLocalidades.append(('tipo', 'in', param_tipo_establecimiento)) 
            
            attribute.values = []
            establecimientos = request.env['turismo.establecimiento'].search(searchDomainEstablecimientos+searchDomainTipos+searchDomainServices, order='city')
            localidades = establecimientos.mapped('city')
            localidades = OrderedDict.fromkeys(localidades).keys()
            for localidad in localidades:
                value = attrValueDirectorio()
                value.num = establecimientos.search_count([('city','=',localidad)])
                value.name = localidad or 'none'
                value.label = localidad or "Sin Definir"
                value.sel = True if localidad in param_localidades or (not localidad and value.name in param_localidades) else False
                attribute.values.append(value)
            attributes.append(attribute)
            
        elif product_type == 'vino':
            searchDomain = [('product_tur_id.website_published','=',True)]
            
            param_tipo_vino = []
            param_tipo_uva = []
            param_premios = []
            param_anhada = []
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if any(params['search']):
                    searchDomain.append('|')
                    searchDomain.append(('product_tur_id.name', 'ilike', werkzeug.url_unquote_plus(params['search'])))
                    searchDomain.append(('product_tur_id.description', 'ilike', werkzeug.url_unquote_plus(params['search'])))
                    
                # Tipo Vino
                param_tipo_vino_k = [s for s in params if s.startswith("tipo_vino-")]
                param_tipo_vino = [werkzeug.url_unquote_plus(params[s]) for s in param_tipo_vino_k]
                
                # Tipo Uva
                param_tipo_uva_k= [s for s in params if s.startswith("tipo_uva-")]
                param_tipo_uva = [werkzeug.url_unquote_plus(params[s]) for s in param_tipo_uva_k]
                
                # Premios
                param_premios_k = [s for s in params if s.startswith("premios-")]
                param_premios = [werkzeug.url_unquote_plus(params[s]) for s in param_premios_k]
                
                # Anhada
                param_anhada_k = [s for s in params if s.startswith("anhada-")]
                param_anhada = [werkzeug.url_unquote_plus(params[s]) for s in param_anhada_k]
                
            searchDomainVinos = list(searchDomain)
            if any(param_tipo_vino):
                searchDomainVinos.append(('product_tur_id.tipovino.nombre', 'in', [False if q=='none' else q for q in param_tipo_vino]))
            if any(param_tipo_uva):
                searchDomainVinos.append(('product_tur_id.uva.nombre', 'in', [False if q=='none' else q for q in param_tipo_uva]))
            if any(param_premios):
                searchDomainVinos.append(('product_tur_id.premios.nombre', 'in', [False if q=='none' else q for q in param_premios]))
            if any(param_anhada):
                searchDomainVinos.append(('product_tur_id.anho', 'in', [False if q=='none' else q for q in param_anhada]))
            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-glass'
            attribute.label = "Tipo Vino"
            attribute.name = "tipo_vino"
            vino_tags = request.env['turismo.vino.tag'].search([], order='nombre')
            vino_tags = vino_tags.mapped('nombre')
            vino_tags = OrderedDict.fromkeys(vino_tags).keys()
            attribute.values = []
            for tag in vino_tags: 
                value = attrValueDirectorio()
                value.num = request.env['turismo.producto_contratado_cliente'].search_count(searchDomainVinos+[('product_tur_id.tipo_producto','=','vino'),
                                                                                             ('product_tur_id.tipovino','=',tag)])
                value.name = value.label = tag
                value.sel = True if value.name in param_tipo_vino else False
                attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-tint'
            attribute.label = "Tipo Uva"
            attribute.name = "tipo_uva"
            uva_tags = request.env['turismo.uva.tag'].search([], order='nombre')
            uva_tags = uva_tags.mapped('nombre')
            uva_tags = OrderedDict.fromkeys(uva_tags).keys()
            attribute.values = []
            for tag in uva_tags: 
                value = attrValueDirectorio()
                value.num = request.env['turismo.producto_contratado_cliente'].search_count(searchDomainVinos+[('product_tur_id.tipo_producto','=','vino'),
                                                                                             ('product_tur_id.uva','=',tag)])
                value.name = value.label = tag
                value.sel = True if value.name in param_tipo_uva else False
                attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.icon = 'fa-star'
            attribute.label = "Premios"
            attribute.name = "premios"
            premio_tags = request.env['turismo.premio.tag'].search([], order='nombre')
            premio_tags = premio_tags.mapped('nombre')
            premio_tags = OrderedDict.fromkeys(premio_tags).keys()
            attribute.values = []
            for tag in premio_tags: 
                value = attrValueDirectorio()
                value.num = request.env['turismo.producto_contratado_cliente'].search_count(searchDomainVinos+[('product_tur_id.tipo_producto','=','vino'),
                                                                                             ('product_tur_id.premios','=',tag)])
                value.name = value.label = tag
                value.sel = True if value.name in param_premios else False
                attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.icon = 'fa-calendar'
            attribute.label = "Añada"
            attribute.name = "anhada"
            vinos = request.env['product.template'].search([('tipo_producto','=','vino')], order='anho')
            anhos = vinos.mapped('anho')
            anhos = OrderedDict.fromkeys(anhos).keys()
            attribute.values = []
            for anho in anhos:
                value = attrValueDirectorio()
                value.num = request.env['turismo.producto_contratado_cliente'].search_count(searchDomainVinos+[('product_tur_id.tipo_producto','=','vino'),
                                                                                             ('product_tur_id.anho','=',anho)])
                value.name = value.label = str(anho)
                value.sel = True if value.name in param_anhada else False
                attribute.values.append(value)
            attributes.append(attribute)
            
        elif product_type == 'evento':
            searchDomain = [('website_published','=',True)]
            param_localidades = []
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if any(params['search']):
                    searchDomain.append('|')
                    searchDomain.append(('name', 'ilike', params['search']))
                    searchDomain.append(('description', 'ilike', params['search']))
                    
                # Localidades
                param_localidades_k = [s for s in params if s.startswith("localidad-")]
                param_localidades = [werkzeug.url_unquote_plus(params[s]) for s in param_localidades_k]
                
            #searchDomainLocalidades = []
            #if len(param_localidades) > 0:
            #    searchDomainLocalidades.append(('address_id.city', 'in', param_localidades))
                
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-map-marker'
            attribute.label = "Localidad"
            attribute.name = "localidad"
            
            #searchDomainLocalidades = list(searchDomain)
            
            _logger.info(param_localidades)
            attribute.values = []
            eventos = request.env['event.event'].search(searchDomain)
            localidades = eventos.mapped('address_id.city')
            localidades = OrderedDict.fromkeys(localidades).keys()
            for localidad in localidades:
                value = attrValueDirectorio()
                value.num = eventos.search_count([('address_id.city','=',localidad)])
                value.name = localidad or 'none'
                value.label = localidad or "Sin Definir"
                value.sel = True if localidad in param_localidades or (not localidad and value.name in param_localidades) else False
                attribute.values.append(value)
            attributes.append(attribute)

        elif product_type == 'vinagre':
            searchDomain = [('product_tur_id.website_published','=',True)]
            
            param_tipo_vinagre = []
            param_tipo_uva = []
            param_premios = []
            param_anhada = []
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if any(params['search']):
                    searchDomain.append('|')
                    searchDomain.append(('name', 'ilike', params['search']))
                    searchDomain.append(('descripcion', 'ilike', params['search']))
                    
                # Tipo Vino
                param_tipo_vinagre_k = [s for s in params if s.startswith("tipo_vinagre-")]
                param_tipo_vinagre = [werkzeug.url_unquote_plus(params[s]) for s in param_tipo_vinagre_k]
                
                # Tipo Uva
                param_tipo_uva_k= [s for s in params if s.startswith("tipo_uva-")]
                param_tipo_uva = [werkzeug.url_unquote_plus(params[s]).lower() for s in param_tipo_uva_k]
                
                # Premios
                param_premios_k = [s for s in params if s.startswith("premios-")]
                param_premios = [werkzeug.url_unquote_plus(params[s]).lower() for s in param_premios_k]
                
                # Anhada
                param_anhada_k = [s for s in params if s.startswith("anhada-")]
                param_anhada = [werkzeug.url_unquote_plus(params[s]).lower() for s in param_anhada_k]
                    
            searchDomainVinagres = list(searchDomain)
            if any(param_tipo_vinagre):
                searchDomainVinagres.append(('product_tur_id.tipovino', 'in', [False if q=='none' else q for q in param_tipo_vinagre]))
            if any(param_tipo_uva):
                searchDomainVinagres.append(('product_tur_id.uva', 'in', [False if q=='none' else q for q in param_tipo_uva]))
            if any(param_premios):
                searchDomainVinagres.append(('product_tur_id.premios', 'in', [False if q=='none' else q for q in param_premios]))
            if any(param_anhada):
                searchDomainVinagres.append(('product_tur_id.anho', 'in', [False if q=='none' else q for q in param_anhada]))
            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-glass'
            attribute.label = "Tipo Vinagre"
            attribute.name = "tipo_vinagre"
            vino_tags = request.env['turismo.vinagre.tag'].search([], order='nombre')
            vino_tags = vino_tags.mapped('nombre')
            vino_tags = OrderedDict.fromkeys(vino_tags).keys()
            attribute.values = []
            for tag in vino_tags: 
                value = attrValueDirectorio()
                value.num = request.env['turismo.producto_contratado_cliente'].search_count(searchDomainVinagres+[('product_tur_id.tipo_producto','=','vinagre'),
                                                                                             ('product_tur_id.tipovinagre','=',tag)])
                value.name = value.label = tag
                attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-tint'
            attribute.label = "Tipo Uva"
            attribute.name = "tipo_uva"
            uva_tags = request.env['turismo.uva.tag'].search([], order='nombre')
            uva_tags = uva_tags.mapped('nombre')
            uva_tags = OrderedDict.fromkeys(uva_tags).keys()
            attribute.values = []
            for tag in uva_tags: 
                value = attrValueDirectorio()
                value.num = request.env['turismo.producto_contratado_cliente'].search_count(searchDomainVinagres+[('product_tur_id.tipo_producto','=','vino'),
                                                                                             ('product_tur_id.uva','=',tag)])
                value.name = value.label = tag
                attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.icon = 'fa-star'
            attribute.label = "Premios"
            attribute.name = "premios"
            premio_tags = request.env['turismo.premio.tag'].search([], order='nombre')
            premio_tags = premio_tags.mapped('nombre')
            premio_tags = OrderedDict.fromkeys(premio_tags).keys()
            attribute.values = []
            for tag in premio_tags: 
                value = attrValueDirectorio()
                value.num = request.env['turismo.producto_contratado_cliente'].search_count(searchDomainVinagres+[('product_tur_id.tipo_producto','=','vinagre'),
                                                                                             ('product_tur_id.premios','=',tag)])
                value.name = value.label = tag
                attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.icon = 'fa-calendar'
            attribute.label = "Añada"
            attribute.name = "anhada"
            vinos = request.env['product.template'].search([('tipo_producto','=','vinagre')], order='anho')
            anhos = vinos.mapped('anho')
            anhos = OrderedDict.fromkeys(anhos).keys()
            attribute.values = []
            for anho in anhos:
                value = attrValueDirectorio()
                value.num = request.env['turismo.producto_contratado_cliente'].search_count(searchDomainVinagres+[('product_tur_id.tipo_producto','=','vinagre'),
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
    
    @http.route(['/contratar_link'], type='http', auth="public", website=True)
    def solicitud_link(self):
        servicios = request.env['product.template'].search([('servicio','=',True)]);
        values = {
            'servicios': servicios
        }
        return request.website.render("aloxa_turismo_theme.solicitud_link", values)
    
    @http.route(['/registrarse',
                 '/editar_usuario',
                 '/registrar_empresa'], type='http', auth="public", website=True)
    def registrarse_editar_usuario(self):
        state_orm = request.env['res.country.state']
        states_ids = state_orm.search([])
        values = dict({'states':states_ids})
        
        if request.httprequest.path.startswith('/editar_usuario'):
            cr, uid, context = request.cr, request.uid, request.context
            if not request.session.uid:
                return login_redirect()
            user = request.env['res.users'].search([('id','=',uid)])
            values.update({ 'partner': user.partner_id })
            return request.website.render("aloxa_turismo_theme.editar_usuario", values)
        elif request.httprequest.path.startswith('/registrar_empresa'):
            return request.website.render("aloxa_turismo_theme.registro_empresa", values)
        else:
            return request.website.render("aloxa_turismo_theme.registro_usuario", values)
    
    @http.route(['/_editar_usuario'], type='http', auth="public", methods=["POST"], website=True)
    def editar_usuario(self, name, email, phone=None, old_password=None, password=None, street=None, city=None, 
                      province=None, postalcode=None, website_url=None, cnif=None, image=None, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        
        user = request.env['res.users'].search([('id','=',uid)])
        if password and old_password != user.password:
            return http.redirect_with_hash('/editar_usuario')
        
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
        
    @http.route(['/_crear_usuario'], type='http', auth="public", methods=["POST"], website=True)
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
                'turista': True
            })
            
        user_partner.sudo().write(regData)
        return http.redirect_with_hash('/panel')
    
    @http.route(['/crear_establecimiento',
                 '/editar_establecimiento/<model("turismo.establecimiento"):stablisment>'], type='http', auth="public", methods=["GET"], website=True)
    def nuevo_editar_establecimiento(self, stablisment=None):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        user = request.env['res.users'].search([('id','=',uid)])
        state_orm = request.env['res.country.state']
        states_ids = state_orm.search([])
        services_orm = request.env['establecimiento.services']
        services_ids = services_orm.search([])
        
        values = {
            'partner': user.partner_id,
            'states': states_ids,
            'est': stablisment,
            'services': services_ids,
        }
        return request.website.render('aloxa_turismo_theme.crear_establecimiento', values)
    @http.route(['/_crear_editar_establecimiento'], type='http', auth="public", methods=["POST"], website=True)
    def crear_editar_establecimiento(self, name, type, image, phone=None,street=None, city=None, province=None, postalcode=None, url_trip=None, desc=None, est_id=None, **kwargs):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        user = request.env['res.users'].search([('id','=',uid)])
        ModelCountry = request.env['res.country']
        country_id = ModelCountry.search([('name','=','Spain')])
        ModelEstablecimiento = request.session.model('turismo.establecimiento')
        
        # Servicios
        param_services_k = [s for s in kwargs if s.startswith("service-")]
        param_services = [int(werkzeug.url_unquote_plus(kwargs[s]).lower()) for s in param_services_k]
        
        modelData = {
            'name': name,
            'tipo': type,
            'street': street,
            'zip': postalcode,
            'state_id': province,
            'country_id': country_id.id,
            'phone': phone,
            'use_parent_address': False,
            'city': city,
            'tripadvisor_url': url_trip,
            'descripcion': desc,
            'res_partner_id': user.partner_id.id,
            'services': [(6, 0, param_services)] if not len(param_services) == 0 else [],
        }
        
        if image.filename:
            modelData.update({'imagen': base64.encodestring(image.read())})
        if not est_id:
            establecimiento_id = ModelEstablecimiento.create(modelData)
            establecimiento_id = ModelEstablecimiento.browse([establecimiento_id])
        else:
            establecimiento_id = ModelEstablecimiento.browse([int(est_id)])
            establecimiento_id.write(modelData)
        return http.redirect_with_hash('/panel/establecimientos#%s' % slug(establecimiento_id))
    
    @http.route(['/preview/establecimiento/<model("turismo.establecimiento"):establecimiento>',
                 '/preview/producto/<model("product.template"):producto>',
                 ], type='http', auth="user", methods=["GET"], website=True)
    def preview(self, producto=None, establecimiento=None):
        if not request.session.uid:
            return login_redirect()
        if establecimiento:
            events = request.env['event.event'].search([('website_published','=',True),
                                                    ('organizer_id','=',establecimiento.partner_id.id),
                                                    ('date_end','>=',datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT))])
            products = request.env['product.template'].search([('seller_ids.name','in',[establecimiento.partner_id.id])])
            values = {
                'establecimiento': establecimiento,
                'events': events,
                'products_table': table_compute().process_productos_establecimiento(products),
            }
            return request.website.render("aloxa_turismo_theme.establecimiento_details", values)
        else:
            values = {
                'producto_contratado': producto
            }
            return request.website.render("aloxa_turismo_theme.product_details", values)
    
    @http.route(['/_add_product'], type='http', auth="user", methods=["POST"], website=True)
    def add_product(self, est_id, product):
        if not request.session.uid:
            return login_redirect()
        
        ModelTurismoEst = request.env['turismo.establecimiento']
        establecimiento_id = ModelTurismoEst.browse([int(est_id)])
        ModelSupplierInfo = request.env['product.supplierinfo']
        supplierinfo_id = ModelSupplierInfo.search([('name','=',establecimiento_id.partner_id.id),('product_tmpl_id','=',product)])
        if not supplierinfo_id:
            supplierinfo_id = ModelSupplierInfo.create({
                'name': establecimiento_id.partner_id.id,
                'delay': 1,
                'min_qty': 0.0,
                'sequence': 1,
                'product_tmpl_id': product
            })
        ModelProductTemplate = request.env['product.template']
        product_id = ModelProductTemplate.browse([int(product)])
        product_id.seller_ids |= supplierinfo_id
        return http.redirect_with_hash('/panel/establecimientos')
    
    @http.route(['/_add_image'], type='http', auth="user", methods=["POST"], website=True)
    def add_image(self, est_id, name, image):
        if not request.session.uid:
            return login_redirect()
        
        ModelTurismoEst = request.env['turismo.establecimiento']
        establecimiento_id = ModelTurismoEst.browse([int(est_id)])
        ModelEstImages = request.env['establecimiento.images']
        image_id = ModelEstImages.create({
            'name': name,
            'image': base64.encodestring(image.read()),
        })
        establecimiento_id.images |= image_id
        return http.redirect_with_hash('/panel/establecimientos')
    
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
        return http.redirect_with_hash('/panel/establecimientos')
    
    @http.route(['/crear_producto',
                 '/editar_producto/<model("product.template"):product>'], type='http', auth="user", methods=["GET"], website=True)
    def nuevo_editar_producto(self, product=None):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        user = request.env['res.users'].search([('id','=',uid)])
        values = {
            'bodegas': request.env['turismo.establecimiento'].search([('res_partner_id','=',user.partner_id.id),('tipo','=','bodega')]),
            'prod': product
        }
        return request.website.render('aloxa_turismo_theme.crear_producto', values)
    @http.route(['/_crear_editar_producto'], type='http', auth="user", methods=["POST"], website=True)
    def crear_editar_producto(self, name, type, price, image=None, anhada=None, uva=None, subtipo=None, bodega=None, premios=None, desc=None, prod_id=None, vender=False):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        user = request.env['res.users'].search([('id','=',uid)])
        ModelProductTemplate = request.session.model('product.template')
        
        # FIXME: Super guarrada!
        if type == 'otro':
            type = None
            
        recordValues = {
            'name': name,
            'tipo_producto': type,
            'list_price': price,
            'description': desc,
            'website_published': False,
            'uom_id': 1,
            'uom_po_id': 1,
            'sale_ok': vender,
        }
        
        if image.filename:
            recordValues.update({'image': base64.encodestring(image.read())})
        
        if type in ['vino','vinagre']:
            ModelUvaTag = request.env['turismo.uva.tag']
            uva_tag_id = ModelUvaTag.search([('nombre','=',uva)])
            if not uva_tag_id:
                uva_tag_id = ModelUvaTag.create({'nombre':uva})
                
            ModelPremiosTag = request.env['turismo.premio.tag']
            premios_tag_id = ModelPremiosTag.search([('nombre','=',premios)])
            if not premios_tag_id:
                premios_tag_id = ModelPremiosTag.create({'nombre':premios})
            
            recordValues.update({
                'anho': anhada,
                'uva': uva_tag_id.id,
                'establecimiento_id': bodega,
                'premios': [premios_tag_id.id],
            })
            if type == 'vino':
                ModelVinoTag = request.env['turismo.vino.tag']
                vino_tag_id = ModelVinoTag.search([('nombre','=',subtipo)])
                if not vino_tag_id:
                    vino_tag_id = ModelVinoTag.create({'nombre':subtipo})
                recordValues.update({'tipovino': vino_tag_id.id})
            elif type == 'vinagre':
                ModelVinagreTag = request.env['turismo.vinagre.tag']
                vinagre_tag_id = ModelVinagreTag.search([('nombre','=',subtipo)])
                if not vino_tag_id:
                    vinagre_tag_id = ModelVinagreTag.create({'nombre':subtipo})
                recordValues.update({'tipovinagre': vinagre_tag_id.id})
                
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
        return http.redirect_with_hash('/panel/productos#%s' % slug(product_template_id))
    
    @http.route(['/_crear_link'], type='http', auth="user", methods=["POST"], website=True)
    def crear_link(self, typelink, image, date_start, date_end, est_id=None, prod_id=None):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
        if est_id is None and prod_id is None:
            return http.redirect_with_hash('/panel/links')
        
        user = request.env['res.users'].search([('id','=',uid)])
        ModelProductoContratadoCliente = request.session.model('turismo.producto_contratado_cliente')
        producto_contratado_cliente_id = ModelProductoContratadoCliente.create({
            'partner_id': user.partner_id.id,
            'product_id': typelink,
            'establecimiento_id': est_id,
            'product_tur_id': prod_id,
            'image': base64.encodestring(image.read()),
            'fecha_inicio': date_start,
            'fecha_fin': date_end,
        })
        return http.redirect_with_hash('/panel/%s' % ('establecimientos' if est_id else 'productos'))

    @http.route(['/crear_evento',
                 '/crear_evento/<model("turismo.establecimiento"):establecimiento>'], type='http', auth="user", methods=["GET"], website=True)
    def nuevo_evento(self, establecimiento=None):
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
        if not establecimiento:
            values['establecimientos'] = request.env['turismo.establecimiento'].search([('res_partner_id','=',user.partner_id.id)])
        else:
            values['est_partner'] = establecimiento.partner_id
        
        return request.website.render("aloxa_turismo_theme.crear_evento", values)
    
    @http.route(['/_crear_evento'], type='http', auth="user", methods=["POST"], website=True)
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
        
        est = request.env['turismo.establecimiento'].search([('partner_id.id','=',organizer)], limit=1)
        return http.redirect_with_hash('/panel/establecimientos#%s' % slug(est))
    
    @http.route(['/panel',
                 '/panel/establecimientos',
                 '/panel/productos',
                 '/panel/eventos',
                 '/panel/facturas',
                 '/panel/links',
                 '/panel/vinos'], type='http', auth="user", website=True)
    def panel_cliente(self):
        cr, uid, context = request.cr, request.uid, request.context
        if not request.session.uid:
            return login_redirect()
            
        user = request.env['res.users'].search([('id','=',uid)])
        values = dict()
        if request.httprequest.path.endswith('/productos'):
            values['panel'] = 'products'
        elif user.partner_id.is_company and request.httprequest.path.endswith('/establecimientos'):
            values['servicios'] = request.env['product.template'].search([('servicio','=',True)]);
            values['panel'] = 'establishments'
            values['products_partner'] = request.env['product.template'].search([('seller_ids.name','in',[user.partner_id.id])])
            values['establecimientos'] = request.env['turismo.establecimiento'].search([('res_partner_id','=',user.partner_id.id)])
        elif user.partner_id.is_company and request.httprequest.path.endswith('/eventos'):
            values['panel'] = 'events'
            establishment_ids = request.env['turismo.establecimiento'].search([
                ('res_partner_id', '=', user.partner_id.id)
            ]).mapped('partner_id.id')
            event_ids = request.env['event.event'].search([
                ('organizer_id', 'in', establishment_ids)
            ])
            values['events'] = event_ids
        elif user.partner_id.is_company and request.httprequest.path.endswith('/links'):
            values['panel'] = 'links'
            products_c_ids = user.partner_id.product_contratado_cliente_ids
            values['links'] = products_c_ids
            values['servicios'] = request.env['product.template'].search([('servicio','=',True)]);
        elif user.partner_id.is_company and request.httprequest.path.endswith('/facturas'):
            values['panel'] = 'invoices'
            invoice_ids = request.env['account.invoice'].search([
                ('partner_id', '=', user.partner_id.id)
            ], order="date_invoice DESC")
            values['invoices'] = invoice_ids
        elif user.partner_id.is_company and request.httprequest.path.endswith('/vinos'):
            values['panel'] = 'wines'
            values['servicios'] = request.env['product.template'].search([('servicio','=',True)]);
            values['productos'] = request.env['product.template'].search([('seller_ids.name','in',[user.partner_id.id])])
        else:
            values['panel'] = 'general'
            if user.partner_id.is_company:
                values['num_productos'] = request.env['product.template'].search_count([('seller_ids.name','in',[user.partner_id.id])])
                establecimientos = request.env['turismo.establecimiento'].search([('res_partner_id','=',user.partner_id.id)])
                values['num_establecimientos'] = len(establecimientos)
                num_events = 0
                for est in establecimientos:
                    num_events = num_events + request.env['event.event'].search_count([('organizer_id','=',est.partner_id.id)])
                values['num_eventos'] = num_events
        
        values['partner'] = user.partner_id
        return request.website.render("aloxa_turismo_theme.panel_cliente", values)
    
    @http.route(['/factura/descargar'], type='http', auth="user", methods=['GET'], website=True)
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
                 '/directorio/establecimientos',
                 '/establecimiento/<model("turismo.establecimiento"):establishment>',
                 '/directorio/vinos',
                 '/vino/<model("turismo.producto_contratado_cliente"):contracted_product>',
                 # '/directorio/vinagres',
                 '/directorio/eventos',
                 '/evento/<model("event.event"):event>'
                 ], type='http', auth="public", methods=['GET'], website=True)
    def directorio(self, establishment=None, event=None, contracted_product=None, **params):
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

        keep_url = '/directorio'
        category_type = None
        if request.httprequest.path.startswith('/directorio/establecimientos') or establishment:
            keep_url = '/directorio/establecimientos'
            category_type = "establecimiento"
            categories = request.env['product.public.category'].search(['&',('parent_id', '=', False),('link', '=', True),('name', '=', 'Establecimientos')])
        elif request.httprequest.path.startswith('/directorio/vinos') or contracted_product:
            keep_url = '/directorio/vinos'
            category_type = "vino"
            categories = request.env['product.public.category'].search(['&',('parent_id', '=', False),('link', '=', True),('name', '=', 'Vinos')])
            # Los vinos no tienen mapa
            if request.session['directory_view'] == 'map':
                request.session['directory_view'] = 'grid'
#         elif request.httprequest.path.startswith('/directorio/vinagres'):
#             keep_url = '/directorio/vinagres'
#             category_type = "vinagre"
#             categories = request.env['product.public.category'].search(['&',('parent_id', '=', False),('link', '=', True),('name', '=', 'Vinagres')])
#             # Los vinagres no tienen mapa
#             if request.session['directory_view'] == 'map':
#                 request.session['directory_view'] = 'grid'
        elif request.httprequest.path.startswith('/directorio/eventos') or event:
            keep_url = '/directorio/eventos'
            category_type = "evento"

        keep = QueryURL(keep_url, search='', attrib=attrib_list)

        # orderby
        orderby = str(params['orderby'].lower()) if params and 'orderby' in params.keys() else 'nombre'
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

        if request.session['directory_view'] == 'form' or is_direct_form:
            # Validar SRI
            sri = False
            if params and 'sri' in params.keys():
                sri = int(params['sri'])-1
                if sri < 0:
                    sri = 0
                elif sri >= len(request.session['search_records']):
                    sri = len(request.session['search_records'])-1

            if category_type == 'establecimiento':
                if not establishment and request.session['search_records']:
                    if not sri:
                        sri = 0
                    establishment = request.env['turismo.establecimiento'].browse([request.session['search_records'][sri]])

                if establishment:
                    # Buscar SRI del establecimiento
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
                            prev_est = request.env['turismo.establecimiento'].browse([request.session['search_records'][sri-1]])
                        if sri < len(request.session['search_records'])-1:
                            next_est = request.env['turismo.establecimiento'].browse([request.session['search_records'][sri+1]])

                    events = request.env['event.event'].search([
                                        ('website_published', '=', True),
                                        ('organizer_id', '=', establishment.partner_id.id),
                                        ('date_end', '>', datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT))
                                    ])
                    products = request.env['product.template'].search([('website_published','=',True),
                                                                       ('establecimiento_id','=',establishment.id)])
                    related_est = request.env['turismo.establecimiento'].search([
                                            ('id', '!=', establishment.id),
                                            ('res_partner_id', '=', establishment.res_partner_id.id)
                                        ])
                    values.update({
                        'sri': sri+1,
                        'prev_est': prev_est,
                        'next_est': next_est,
                        'establishment': establishment,
                        'events': events,
                        'related': related_est,
                        'products_table': table_compute().process_productos_establecimiento(products),
                    })
                else:
                    request.session['directory_view'] = 'grid'
            elif category_type == 'vino':
                if not contracted_product and request.session['search_records']:
                    if not sri:
                        sri = 0
                    contracted_product = request.env['turismo.producto_contratado_cliente'].browse([request.session['search_records'][sri]])
                if contracted_product:
                    # Buscar SRI del establecimiento
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
                            prev_event = request.env['turismo.producto_contratado_cliente'].browse([request.session['search_records'][sri-1]])
                        if sri < len(request.session['search_records'])-1:
                            next_event = request.env['turismo.producto_contratado_cliente'].browse([request.session['search_records'][sri+1]])
                    related_prods = request.env['turismo.producto_contratado_cliente'].search([('id', '!=', contracted_product.id),('partner_id', '=', contracted_product.partner_id.id)])
                    values.update({
                        'sri': sri+1,
                        'prev_prod': prev_event,
                        'next_prod': next_event,
                        'contracted_product': contracted_product,
                        'related': related_prods,
                    })
                else:
                    request.session['directory_view'] = 'grid'
            elif category_type == 'evento':
                if not event and request.session['search_records']:
                    if not sri:
                        sri = 0
                    event = request.env['event.event'].browse([request.session['search_records'][sri]])
                if event:
                    # Buscar SRI del establecimiento
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
                            prev_event = request.env['event.event'].browse([request.session['search_records'][sri-1]])
                        if sri < len(request.session['search_records'])-1:
                            next_event = request.env['event.event'].browse([request.session['search_records'][sri+1]])
                    related_events = request.env['event.event'].search([('id', '!=', event.id),('organizer_id', '=', event.organizer_id.id)])
                    values.update({
                        'sri': sri+1,
                        'prev_event': prev_event,
                        'next_event': next_event,
                        'event': event,
                        'related': related_events,
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