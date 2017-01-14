# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
import re
from fnmatch import translate
#import pydevd

'''
Modelo comun con campos comunes a establecimientos
'''
class establecimiento(models.Model):
    _name = 'turismo.establecimiento'
    _rec_name = 'nombre'
    
   
    
    def default_nombre(self):        
        if 'res_partner_id' in self.env.context:
            partner = self.env['res.partner'].search([('id','=',self.env.context['res_partner_id'])])
            return partner.name
        return ''
    
    def default_direccion(self):        
        if 'res_partner_id' in self.env.context:
            partner = self.env['res.partner'].search([('id','=',self.env.context['res_partner_id'])])
            direccion = ''
            if partner.street:
                direccion += partner.street
            #===================================================================
            # if partner.city:
            #     direccion += ', ' + partner.city                
            #===================================================================
            return direccion
        return ''
    
    def default_localidad(self):        
        if 'res_partner_id' in self.env.context:
            partner = self.env['res.partner'].search([('id','=',self.env.context['res_partner_id'])])
            localidad = ''
            if partner.city:
                localidad += partner.city               
            return localidad
        return ''
    
    def default_imagen(self):        
        if 'res_partner_id' in self.env.context:
            partner = self.env['res.partner'].search([('id','=',self.env.context['res_partner_id'])])
            return partner.image
        return None
    
    def default_res_partner_id(self):        
        if 'res_partner_id' in self.env.context:
            partner = self.env['res.partner'].search([('id','=',self.env.context['res_partner_id'])])
            return partner
        return False

    def default_web(self):        
        if 'res_partner_id' in self.env.context:
            partner = self.env['res.partner'].search([('id','=',self.env.context['res_partner_id'])])
            return partner.website
        return ''
    
    def get_tripadvisor_id(self):
        matchObj = re.match('^https?://.+-d([0-9]+).+\.html$', self.tripadvisor_url, re.IGNORECASE)
        return int(matchObj.group(1)) if matchObj else -1
    
    # Constraints
    @api.one
    @api.constrains('tripadvisor_url')
    def _check_tripadvisor_url(self):
        if self.tripadvisor_url and not re.match('^https?://.+-d[0-9]+.+\.html$', self.tripadvisor_url, re.IGNORECASE):
            raise exceptions.ValidationError("Url de TripAdvisor Incorrecta")
    
    #fields
    latitud = fields.Float('Latitud', digits=(6,3))
    longitud = fields.Float('Longitud', digits=(6,3))
    imagen = fields.Binary('Imagen', default=default_imagen)
    nombre = fields.Char(string='Nombre', size=80, default=default_nombre, translate=True)
    descripcion = fields.Text(string='Descripción', translate=True)   
    direccion = fields.Char(string='Dirección', size=120, default=default_direccion, translate=True)
    localidad = fields.Char(string='Localidad', size=120, default=default_localidad, translate=True)
    horario = fields.Char(string='Horario', size=120)
    res_partner_id = fields.Many2one('res.partner', 'Cliente', default=default_res_partner_id)   
    tripadvisor_url = fields.Char(string="TripAdvisor Url", size=255)
    idiomas = fields.Many2many('turismo.idioma.tag', string='Idiomas')
    comarca = fields.Many2many('turismo.comarca.tag', string='Comarca')
    tipo = fields.Selection([('bodega','Bodega'), ('restaurante','Restaurante'),('hospedaje','Hospedaje'),('cultural','Arte y Cultura'),('vinoteca','Vinoteca'), ('vinhedo','Viñedo'),('otro','Otro')],'Tipo de Establecimiento', translate=True, required=True)    
    web = fields.Char(string="Web", size=255, default=default_web)
    website_published = fields.Boolean('Disponible en el sitio web', copy=False)
    
establecimiento()


'''
Modelo para tags de idiomas
'''
class comarca_tag(models.Model):
    _name='turismo.comarca.tag'
    _rec_name='nombre'
    
    #Fields
    nombre = fields.Char('Nombre', size=80)
    
comarca_tag()

'''
Modelo para tags de idiomas
'''
class idioma_tag(models.Model):
    _name='turismo.idioma.tag'
    _rec_name='nombre'
    
    #Fields
    nombre = fields.Char('Nombre', size=80)
    
idioma_tag()


'''
Modelo para Bodegas
Hereda del modelo comun turismo.establecimiento

class bodega(models.Model):
    _name = 'turismo.bodega'
    _rec_name = 'nombre'
    _inherits = {'turismo.establecimiento':'establecimiento_id'}   
    #_inherit = 'turismo.establecimiento'
    
    # Metodo requerido en el directorio de establecimientos cuando se filtra por bodega
    def get_tripadvisor_id(self):
        matchObj = re.match('^https?://.+-d([0-9]+).+\.html$', self.tripadvisor_url, re.IGNORECASE)
        return int(matchObj.group(1)) if matchObj else -1
    
    establecimiento_id = fields.Many2one('turismo.establecimiento', 'Establecimiento')
    partner_id = fields.Many2one('res.partner', 'Cliente')
    bodega_product_ids = fields.One2many('product.template', 'bodega_id', 'Productos de la Bodega')
    
bodega()
'''
'''
Modelo para Restaurantes
Hereda del modelo comun turismo.establecimiento

class restaurante(models.Model):
    _name = 'turismo.restaurante'
    _rec_name = 'nombre'
    _inherits = {'turismo.establecimiento':'establecimiento_id'}
    #_inherit = 'turismo.establecimiento'    
 
    establecimiento_id = fields.Many2one('turismo.establecimiento', 'Establecimiento')
    partner_id = fields.Many2one('res.partner', 'Cliente')
    #restaurante_product_ids = fields.One2many('product.template', 'restaurante_id', 'Productos del Restaurante')
    
restaurante()
'''
'''
Modelo para Hospedajes
Hereda del modelo comun turismo.establecimiento

class hospedaje(models.Model):
    _name = 'turismo.hospedaje'
    _rec_name = 'nombre'
    _inherits = {'turismo.establecimiento':'establecimiento_id'}
    #_inherit = 'turismo.establecimiento'    

    establecimiento_id = fields.Many2one('turismo.establecimiento', 'Establecimiento')    
    partner_id = fields.Many2one('res.partner', 'Cliente')
    #hospedaje_product_ids = fields.One2many('product.template', 'hospedaje_id', 'Productos del Hospedaje')
    
hospedaje()
'''
'''
Modelo para establecimiento de Arte y Cultura
Hereda del modelo comun turismo.establecimiento

class cultural(models.Model):
    _name = 'turismo.cultural'
    _rec_name = 'nombre'
    _inherits = {'turismo.establecimiento':'establecimiento_id'}
    #_inherit = 'turismo.establecimiento'    
    
    establecimiento_id = fields.Many2one('turismo.establecimiento', 'Establecimiento')
    partner_id = fields.Many2one('res.partner', 'Cliente')
    #cultural_product_ids = fields.One2many('product.template', 'cultural_id', 'Productos de Arte y Cultura')
    
cultural()
'''
'''
Modelo para Vinotecas
Hereda del modelo comun turismo.establecimiento

class vinoteca(models.Model):
    _name = 'turismo.vinoteca'
    _rec_name = 'nombre'
    _inherits = {'turismo.establecimiento':'establecimiento_id'}
    #_inherit = 'turismo.establecimiento'    

    establecimiento_id = fields.Many2one('turismo.establecimiento', 'Establecimiento')    
    partner_id = fields.Many2one('res.partner', 'Cliente')
    #vinoteca_product_ids = fields.One2many('product.template', 'vinoteca_id', 'Productos de Vinoteca')
    
vinoteca()
'''
'''
Modelo para establecimiento de otro tipo
Hereda del modelo comun turismo.establecimiento

class otro(models.Model):
    _name = 'turismo.otro'
    _rec_name = 'nombre'
    _inherits = {'turismo.establecimiento':'establecimiento_id'}
    #_inherit = 'turismo.establecimiento'    
    
    establecimiento_id = fields.Many2one('turismo.establecimiento', 'Establecimiento')
    partner_id = fields.Many2one('res.partner', 'Cliente')
    #otro_product_ids = fields.One2many('product.template', 'otro	_id', 'Productos del Establecimiento')
    
otro()
'''
'''
Modelo extension de res.partner que registra fields Many2one a los posibles
establecimientos definidos con anterioridad
'''
class res_partner_turismo(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
      
    #fields
    '''
    Relacionales para los establecimientos del Cliente
    
    bodega_ids = fields.One2many('turismo.bodega', 'partner_id', 'Bodegas')
    restaurante_ids = fields.One2many('turismo.restaurante', 'partner_id', 'Restaurantes')
    hospedaje_ids = fields.One2many('turismo.hospedaje', 'partner_id', 'Hospedajes')
    cultural_ids = fields.One2many('turismo.cultural', 'partner_id', 'Arte y Cultura')
    vinoteca_ids = fields.One2many('turismo.vinoteca', 'partner_id', 'Vinotecas')    
    otro_ids = fields.One2many('turismo.otro', 'partner_id', 'Otros')       
''' 
    establecimiento_ids = fields.One2many('turismo.establecimiento', 'res_partner_id', 'Establecimientos')
    product_contratado_cliente_ids = fields.One2many('turismo.producto_contratado_cliente',
                                                     'partner_id', string='Productos Contratados')
    
res_partner_turismo()

#===============================================================================
# '''
# Modelo extension de res.partner que registra fields Many2one a los posibles
# establecimientos definidos con anterioridad
# '''
# class establecimiento(models.Model):
#     _name = 'res.partner'
#     _inherit = 'res.partner'    
#     
#     '''
#     La inicializacion por defecto es necesaria ya que el mecanismo delegate=True
#     requiere que los campos esten definidos
#     '''
#     def _bodega_default(self):
#         bodega_def = self.env['turismo.bodega'].search([('bodega_nombre','=','-')])
#         if not bodega_def:
#             bodega_def = self.env['turismo.bodega'].create({'bodega_nombre':'-'})
#         else:
#             bodega_def = bodega_def[0]
#         return bodega_def
#     
#     def _restaurante_default(self):
#         restaurante_def = self.env['turismo.restaurante'].search([('restaurante_nombre','=','-')])
#         if not restaurante_def:
#             restaurante_def = self.env['turismo.restaurante'].create({'restaurante_nombre':'-'})
#         else:
#             restaurante_def = restaurante_def[0]
#         return restaurante_def
#     
#     def _hospedaje_default(self):
#         hospedaje_def = self.env['turismo.hospedaje'].search([('hospedaje_nombre','=','-')])
#         if not hospedaje_def:
#             hospedaje_def = self.env['turismo.hospedaje'].create({'hospedaje_nombre':'-'})
#         else:
#             hospedaje_def = hospedaje_def[0]
#         return hospedaje_def
#       
#     #fields
#     '''
#     El atributo delegate=True permite acceder a los fields del modelo relacionado directamente desde el
#     modelo actual, sin embargo requiere que los campos de relacion sean definidos
#     '''
#     bodega_id = fields.Many2one('turismo.bodega', 'Bodega', delegate=True, default=_bodega_default)
#     restaurante_id = fields.Many2one('turismo.restaurante', 'Restaurante', delegate=True, default=_restaurante_default)
#     hospedaje_id = fields.Many2one('turismo.hospedaje', 'Hospedaje', delegate=True, default=_hospedaje_default)        
#         
# establecimiento()
#===============================================================================
    
