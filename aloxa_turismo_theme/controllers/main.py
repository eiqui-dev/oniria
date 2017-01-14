  # -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from datetime import datetime
from html_table import table_compute
from collections import OrderedDict
import re
import random
import logging
_logger = logging.getLogger(__name__)
#import pydevd

class QueryURL(object):
    def __init__(self, path='', **args):
        self.path = path
        self.args = args

    def __call__(self, path=None, **kw):
        if not path:
            path = self.path
        for k,v in self.args.items():
            kw.setdefault(k,v)
        l = []
        for k,v in kw.items():
            if v:
                if isinstance(v, list) or isinstance(v, set):
                    l.append(werkzeug.url_encode([(k,i) for i in v]))
                else:
                    l.append(werkzeug.url_encode([(k,v)]))
        if l:
            path += '?' + '&'.join(l)
        return path
    
# Clase intermedia para generar la tabla del directorio
class htmlBannerDirectorio:
    producto_contratado = None
    establecimiento = None

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

class website_aloxa_turismo(http.Controller):
    def _get_banners_directorio(self, orderby, product_category=None, product_type=None, params=None):
        banners_directorio = []
        
        #pydevd.settrace("10.0.3.1")
        # Recoger los establecimientos
        searchDomain = []
        if not product_category and (product_type == "establecimiento" or not product_type):
            searchDomain.append(('website_published','=',True))
            #_logger.error("my variable : %r", params)
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if len(params['search']) > 0:
                    searchDomain.append('|')
                    searchDomain.append(('nombre', 'ilike', params['search']))
                    searchDomain.append(('descripcion', 'ilike', params['search']))
                # Localidades
                localidades_k = [s for s in params if s.startswith("localidad-")]
                localidades = [params[s] for s in localidades_k]
                if len(localidades) > 0:
                    searchDomain.append(('localidad', 'in', localidades))
                    
                #pydevd.settrace("10.0.3.1")
                param_tipo_establecimento_k = [s for s in params if s.startswith("tipo_establecimiento-")]
                param_tipo_establecimiento = [params[s].lower() for s in param_tipo_establecimento_k]
                if len(param_tipo_establecimiento) > 0:
                    searchDomain.append(('tipo', 'in', param_tipo_establecimiento))
                    
            # OrderBy
            if orderby == 'direccion':
                orderby_key = 'direccion'
            else:
                orderby_key = 'nombre'

            registros = request.env['turismo.establecimiento'].search(searchDomain).sorted(key=lambda r: r[orderby_key])
            for reg in registros:
                tmp_banner = htmlBannerDirectorio()
                tmp_banner.establecimiento = reg
                banners_directorio.append(tmp_banner)
        else:
            # Recoger los banners
            searchDomain = ['|','&',('fecha_fin', '>=', datetime.now()),('fecha_fin', '=', False),('publicado', '=', True),('product_id.link_position', '=', 'Directorio')]
            if product_category:
                searchDomain.append(('public_category_id', '=', product_category.id))
            if product_type:
                searchDomain.append(('product_tur_id.tipo_producto', '=', product_type))
            
            #pydevd.settrace("10.0.3.1")
            if params and 'search' in params.keys():
                if len(params['search']) > 0:
                    searchDomain.append('|')
                    searchDomain.append(('name', 'ilike', params['search']))
                    searchDomain.append(('description', 'ilike', params['search']))
                if 'anhada' in params.keys() and len(params['anhada']) > 0:
                    searchDomain.append(('product_tur_id.anho', '=', params['anhada']))
                if 'tipo_vino' in params.keys() and len(params['tipo_vino']) > 0:
                    searchDomain.append(('product_tur_id.vino', '=', params['tipo_vino'].lower()))
                if 'tipo_uva' in params.keys() and len(params['tipo_uva']) > 0:
                    searchDomain.append(('product_tur_id.uva', '=', params['tipo_uva'].lower()))
                if 'premios' in params.keys() and len(params['premios']) > 0:
                    searchDomain.append(('product_tur_id.premios', '=', params['premios'].lower()))
                if 'tipo_vinhedo' in params.keys() and len(params['tipo_vinhedo']) > 0:
                    searchDomain.append(('product_tur_id.tipo', '=', params['tipo_vinhedo'].lower()))
                if 'localidad' in params.keys() and len(params['localidad']) > 0:
                    searchDomain.append(('product_tur_id.localidad', '=', params['localidad'].lower()))
            # OrderBy
            if orderby == 'precio':
                orderby_key = 'list_price'
            else:
                orderby_key = 'name'
            
            productos_contratados = request.env['turismo.producto_contratado_cliente'].search(searchDomain).sorted(key=lambda r: r.product_tur_id[orderby_key])
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
        return table_compute().process_directory(banners_directorio)
    
    
    def _create_directory_attributes(self, product_type = None, params = None):
        attributes = []
        
        if product_type == 'establecimiento':
            searchDomain = [('website_published','=',True)]
            
            param_tipo_establecimiento = []
            param_localidades = []
            if params and 'search' in params.keys():
                # Busqueda por cajetin
                if len(params['search']) > 0:
                    searchDomain.append('|')
                    searchDomain.append(('nombre', 'ilike', params['search']))
                    searchDomain.append(('descripcion', 'ilike', params['search']))
                    
                # Localidades
                param_localidades_k = [s for s in params if s.startswith("localidad-")]
                param_localidades = [params[s] for s in param_localidades_k]
                
                # Tipo Establecimiento
                param_tipo_establecimento_k = [s for s in params if s.startswith("tipo_establecimiento-")]
                param_tipo_establecimiento = [params[s].lower() for s in param_tipo_establecimento_k]
                    
            searchDomainEstablecimientos = list(searchDomain)
            if len(param_localidades) > 0:
                searchDomainEstablecimientos.append(('localidad', 'in', param_localidades))
            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-tag'
            attribute.label = "Tipo"
            attribute.name = "tipo_establecimiento"    
            attribute.values = []
            value = attrValueDirectorio()
            value.label = 'Bodegas'
            value.name = 'bodega'
            value.sel = True if value.name.lower() in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+[('tipo','=','bodega')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Restaurantes'
            value.name = 'restaurante'
            value.sel = True if value.name.lower() in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+[('tipo','=','restaurante')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Hospedajes'
            value.name = 'hospedaje'
            value.sel = True if value.name.lower() in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+[('tipo','=','hospedaje')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Viñedos'
            value.name = 'vinhedo'
            value.sel = True if value.name.lower() in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+[('tipo','=','vinhedo')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Arte y Cultura'
            value.name = 'cultural'
            value.sel = True if value.name.lower() in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+[('tipo','=','cultural')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Vinotecas'
            value.name = 'vinoteca'
            value.sel = True if value.name.lower() in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+[('tipo','=','vinoteca')])
            attribute.values.append(value)
            value = attrValueDirectorio()
            value.label = 'Otros'
            value.name = 'otro'
            value.sel = True if value.name.lower() in param_tipo_establecimiento else False
            value.num = request.env['turismo.establecimiento'].search_count(searchDomainEstablecimientos+[('tipo','=','otro')])
            attribute.values.append(value)
            attributes.append(attribute)
                            
            attribute = attrDirectorio()
            attribute.open = True
            attribute.icon = 'fa-map-marker'
            attribute.label = "Localidad"
            attribute.name = "localidad"
            
            searchDomainLocalidades = list(searchDomain)
            if len(param_tipo_establecimiento) > 0:
                searchDomainLocalidades.append(('tipo', 'in', param_tipo_establecimiento)) 
            
            attribute.values = []
            establecimientos = request.env['turismo.establecimiento'].search(searchDomainLocalidades, order='localidad')
            localidades = establecimientos.mapped('localidad')
            localidades = OrderedDict.fromkeys(localidades).keys()
            for localidad in localidades:
                value = attrValueDirectorio()
                value.num = establecimientos.search_count([('localidad','=',localidad)])
                value.name = value.label = localidad
                value.sel = True if localidad in param_localidades else False
                attribute.values.append(value)
            attributes.append(attribute)
            
        elif product_type == 'vino':
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
                value.num = request.env['turismo.producto_contratado_cliente'].search_count([('product_tur_id.vino_id.tipo','=',tag)])
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
                value.num = request.env['turismo.producto_contratado_cliente'].search_count([('product_tur_id.vino_id.uva','=',tag)])
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
                value.num = request.env['turismo.producto_contratado_cliente'].search_count([('product_tur_id.vino_id.premios','=',tag)])
                value.name = value.label = tag
                attribute.values.append(value)
            attributes.append(attribute)
            
            attribute = attrDirectorio()
            attribute.icon = 'fa-calendar'
            attribute.label = "Añada"
            attribute.name = "anhada"
            vinos = request.env['turismo.vino'].search([], order='anho')
            anhos = vinos.mapped('anho')
            anhos = OrderedDict.fromkeys(anhos).keys()
            attribute.values = []
            for anho in anhos:
                value = attrValueDirectorio()
                value.num = request.env['turismo.producto_contratado_cliente'].search_count([('product_tur_id.vino_id.anho','=',anho)])
                value.name = value.label = anho
                attribute.values.append(value)
            attributes.append(attribute)
            
        return attributes
            
    
    
    @http.route(['/contratar_link'], type='http', auth="public", website=True)
    def solicitud_link(self):
        servicios = request.env['product.template'].search([('servicio','=',True)]);
        values = {
            'servicios': servicios
        }
        return request.website.render("aloxa_turismo_theme.solicitud_link", values)
    
    @http.route(['/establecimiento/<model("turismo.establecimiento"):establecimiento>'], type='http', auth="public", website=True)
    def establecimiento(self, establecimiento):
        values = {
            'establecimiento': establecimiento
        }
        return request.website.render("aloxa_turismo_theme.establecimiento_details", values)
    
    @http.route([
                 '/vinhedo/<model("product.template"):producto>',
                 '/vino/<model("product.template"):producto>'
                 ], type='http', auth="public", website=True)
    def producto_contratado(self, producto):
        values = {
            'producto_contratado': producto
        }
        return request.website.render("aloxa_turismo_theme.product_details", values)
    
    
    @http.route([
                 '/directorio',
                 '/directorio/categoria/<model("product.public.category"):category>',
                 '/directorio/establecimientos',
                 '/directorio/vinos',
                 '/directorio/vinhedos'
                 ], type='http', auth="public", methods=['GET'], website=True)
    def directorio(self, category=None, **params):
        categories = []
        #pydevd.settrace("10.0.3.1")
        attrib_list = request.httprequest.args.getlist('attrib')
        keep = QueryURL('/directorio', category=category and int(category), search='', attrib=attrib_list)
        
        if not 'directory_view' in request.session:
            request.session['directory_view'] = 'grid'

        category_type = None
        if request.httprequest.path.endswith('/establecimientos'):
            category_type = "establecimiento"
            categories = request.env['product.public.category'].search(['&',('parent_id', '=', False),('link', '=', True),('name', '=', 'Establecimientos')])
        elif request.httprequest.path.endswith('/vinos'):
            category_type = "vino"
            categories = request.env['product.public.category'].search(['&',('parent_id', '=', False),('link', '=', True),('name', '=', 'Vinos')])
            # Los vinos no tienen mapa
            if request.session['directory_view'] == 'map':
                request.session['directory_view'] = 'grid'

        # orderby
        orderby = str(params['orderby'].lower()) if params and 'orderby' in params.keys() else 'nombre'

        values = {
            'orderby': orderby,
            'category': category,
            'categories': categories,
            'category_type': category_type,
            'attributes': self._create_directory_attributes(product_type=category_type, params=params),
            'keep': keep,
            'bins': self._get_banners_directorio(orderby, product_category=category, product_type=category_type, params=params),
            'rows': 4,
            'search': params['search'] if params and 'search' in params.keys() else ''
        }
        return request.website.render("aloxa_turismo_theme.directory", values)
    
    
    ## JSON-RPC
    @http.route(['/_set_directory_view/grid',
                 '/_set_directory_view/list',
                 '/_set_directory_view/map'], type='json', auth="public", website=True)
    def set_directory_view(self):
        if request.httprequest.path.endswith('/grid'):
            request.session['directory_view'] = 'grid'
        elif request.httprequest.path.endswith('/list'):
            request.session['directory_view'] = 'list'
        elif request.httprequest.path.endswith('/map'):
            request.session['directory_view'] = 'map'
        return []
            
    @http.route(['/solicitar_link/get_services'], type='json', auth="public", website=True)
    def calendario_get_events(self):
        if not request.session.uid:
            return {'error': 'anonymous_user'}
        else:
            partner_id = request.env['res.users'].browse(request.uid).partner_id.id
            events = request.env['calendar.event'].search([('partner_ids','in',partner_id)])
            result = []
            for event in events:
                result.append({                          
                    'title': event.name,
                    'start': event.start,
                    'end': event.stop if not event.allday else None,
                    'allDay': event.allday,
                    'id': event.id
                });
                
            return result