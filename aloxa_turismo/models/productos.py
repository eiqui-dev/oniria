# -*- coding: utf-8 -*-
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
from openerp import models, fields, api, exceptions
from openerp.addons.product import product as prodm
from openerp.addons.mail import mail_thread
from datetime import datetime
from openerp.osv import osv
from comun import crop_image
from PIL import Image

#import pydevd

class uva_tag(models.Model):
    _name='turismo.uva.tag'
    _rec_name='nombre'
    
    #Fields
    nombre = fields.Char('Nombre', size=80)
    
uva_tag()

class vino_tag(models.Model):
    _name='turismo.vino.tag'
    _rec_name='nombre'
    
    #Fields
    nombre = fields.Char('Nombre', size=80)
    
vino_tag()

class vinagre_tag(models.Model):
    _name='turismo.vinagre.tag'
    _rec_name='nombre'
    
    #Fields
    nombre = fields.Char('Nombre', size=80)
    
vinagre_tag()

class premio_tag(models.Model):
    _name='turismo.premio.tag'
    _rec_name='nombre'
    
    #Fields
    nombre = fields.Char('Nombre', size=80)
    
premio_tag()

'''
Modelo de la tabla de relacion many2many entre Clientes y productos turisticos
'''
class producto_contratado_cliente(models.Model):
    _name = 'turismo.producto_contratado_cliente'
        
    @api.one
    @api.depends('product_tur_id')
    def get_categoria_publica(self):
        if self.product_tur_id and self.product_tur_id.public_categ_ids:
            self.public_category_id = self.product_tur_id.public_categ_ids[0]
    
       
    '''
    Metodo que genera una factura borrado asociada al producto contratado y al cliente
    '''
    @api.one
    def generar_factura_servicio(self):        
        ai_model = self.env['account.invoice']
        ail_model = self.env['account.invoice.line']
        #pydevd.settrace("192.168.3.1")
        #Para cada tarea del proyecto creamos una linea de factura
        if self.partner_id:
            partner = self.partner_id
            oo = self.env['turismo.opciones'].search([('nombre','=','Default')])            
            if oo and oo.account_id and oo.journal_id:                    
                company = self.env.user.company_id
                currency = self.env.user.company_id.currency_id
                ai = ai_model.create({'partner_id':partner.id,
                                      'account_id':oo.account_id.id,
                                      'company_id':company.id,
                                      'currency_id':currency.id,
                                      'journal_id':oo.journal_id.id, #Diario de Ventas
                                      'reference_type':'none'})
                lines = []
                #dias a facturar
                if self.fecha_inicio and self.fecha_fin and self.product_id:
                    dias = (datetime.strptime(str(self.fecha_fin), '%Y-%m-%d') -
                            datetime.strptime(str(self.fecha_inicio), '%Y-%m-%d')).days
                    line = ail_model.create({'account_id':ai.account_id.id,
                                             'name':self.product_id.name,
                                             'product_id':self.product_id.id,
                                             'price_unit':self.product_id.list_price,
                                             'quantity':dias})
                    lines.append(line.id)
                     
                    ai.invoice_line = lines
                self.factura_id = ai.id
            else:
                raise osv.except_osv(('Falta información'), ('Faltan Opciones de Contabilidad en Configuración'))
        else:
            raise osv.except_osv(('Falta información'), ('No ha especificado Cliente para el Proyecto...'))


    # Computed Fields
    @api.one
    @api.depends('imagen')
    def _get_image_thumb(self):
        for record in self:
            if record.imagen:
                record.image_thumb = crop_image(
                    record.imagen, ratio=(2,1), thumbnail_ratio=4, type='center')
            else:
                record.image_thumb = False
                
    @api.one
    @api.constrains('imagen')
    def _check_imagen(self):
        image_stream = StringIO.StringIO(self.imagen.decode('base64'))
        image = Image.open(image_stream)
        if int(image.size[0]) < 256 or int(image.size[1]) < 256:
            raise exceptions.ValidationError("Image width & height need be bigger than 256 pixels")
    
    
    #fields
    partner_id = fields.Many2one('res.partner', 'Cliente', required=True)
    product_id = fields.Many2one('product.template', 'Servicio', required=True)
    product_tur_id = fields.Many2one('product.template', 'Producto')
    establecimiento_id = fields.Many2one('turismo.establecimiento', 'Establecimiento')
    imagen = fields.Binary('Imagen')
    image_thumb = fields.Binary('Thumbnail', compute="_get_image_thumb", store=True)
    url = fields.Char('Enlace', size=50)
    fecha_inicio = fields.Date('Inicio')
    fecha_fin = fields.Date('Fin')
    publicado = fields.Boolean('Publicado')
    public_category_id = fields.Many2one('product.public.category', 'Categoría', compute=get_categoria_publica)
    publicado = fields.Boolean('Publicado')
    factura_id = fields.Many2one('account.invoice', 'Factura')
    
producto_contratado_cliente()

'''
Modelo que extiende product.public.category para agregar un campo booleano indicando
si la categoria esta asociada a links
Este modelo permite organizar los productos en la zona publica
'''
class product_public_category(models.Model):
    _name='product.public.category'
    _inherit='product.public.category'
    
    #Fields
    link = fields.Boolean('Es link')
    
product_public_category()

'''
Modelos construidos mediante herencia de product.template
Tiene referencias many2one a las entidades de estructuras de producto turistico
'''
class producto_turismo(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    
    #===========================================================================
    # '''
    # La inicializacion por defecto es necesaria ya que el mecanismo delegate=True
    # requiere que los campos esten definidos
    # '''
    # def _visita_default(self):
    #     visita_def = self.env['turismo.visita'].search([('id','=',99999)])
    #     if not visita_def:
    #         visita_def = self.env['turismo.visita'].create({'id':'99999'})
    #     else:
    #         visita_def = visita_def[0]
    #     return visita_def        
    #   
    # def _vino_default(self):
    #     vino_def = self.env['turismo.vino'].search([('id','=',99999)])
    #     if not vino_def:
    #         vino_def = self.env['turismo.vino'].create({'id':'99999'})
    #     else:
    #         vino_def = vino_def[0]
    #     return vino_def
    #   
    # def _menu_default(self):
    #     menu_def = self.env['turismo.menu'].search([('id','=',99999)])
    #     if not menu_def:
    #         menu_def = self.env['turismo.menu'].create({'id':'99999'})
    #     else:
    #         menu_def = menu_def[0]
    #     return menu_def
    #   
    # def _habitacion_default(self):
    #     habitacion_def = self.env['turismo.habitacion'].search([('id','=',0)])
    #     if not habitacion_def:
    #         habitacion_def = self.env['turismo.habitacion'].create({'id':'0'})
    #     else:
    #         habitacion_def = habitacion_def[0]
    #     return habitacion_def
    #===========================================================================
    
    '''
    Metodo default_get para en funcion del valor en el contexto se establecen valores de campos
    por defecto. En este caso si estan activados filtros de busqueda se preselecciona el tipo
    de producto
    '''
    @api.model
    def default_get(self, fields):
        #pydevd.settrace("192.168.3.1")
        data = super(producto_turismo, self).default_get(fields)
        if 'search_default_tipo_vino' in self.env.context:            
            data['tipo_producto'] = ('vino','Vino')
        elif 'search_default_tipo_vinagre' in self.env.context:
            data['tipo_producto'] = ('vinagre','Vinagre')            
        return data
    
    def is_seller_by(self, partner_id):
        ModelSupplierInfo = self.env['product.supplierinfo']
        for record in self:
            supplierinfo_id = ModelSupplierInfo.search([('name','=',partner_id),('product_tmpl_id','=',record.id)])
            return True if supplierinfo_id else False
        
    
    #fields

    servicio = fields.Boolean('Link')
    link_size = fields.Selection([('S','S'),('M','M')], 'Tamaño del Link')
    link_position = fields.Selection([('Portada','Portada'),('Directorio','Directorio')],
                                     'Ubicación del Link')    
    
    tipo_producto = fields.Selection([('vino','Vino'), ('vinagre','Vinagre')],
                                     'Tipo de Producto Turistico')    

    '''
    El atributo delegate=True permite acceder a los fields del modelo relacionado directamente desde el
    modelo actual, sin embargo requiere que los campos de relacion sean definidos
    '''
    uva = fields.Many2one('turismo.uva.tag', string='Uva')
    tipovino = fields.Many2one('turismo.vino.tag', string='Tipo')
    tipovinagre = fields.Many2one('turismo.vinagre.tag', string='Tipo')
    anho = fields.Char('Añada', size=30)
    premios = fields.Many2many('turismo.premio.tag', string='Premios')
    establecimiento_id = fields.Many2one('turismo.establecimiento', 'Bodega', domain="[('tipo', '=', 'bodega')]")


producto_turismo()
