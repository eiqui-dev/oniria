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

class grape_tag(models.Model):
    _name='turismo.grape.tag'
    _rec_name='name'
    
    #Fields
    name = fields.Char('Name', size=80, translate=True)
    
grape_tag()

class wine_tag(models.Model):
    _name='turismo.wine.tag'
    _rec_name='name'
    
    #Fields
    name = fields.Char('Name', size=80, translate=True)
    
wine_tag()

class vinagre_tag(models.Model):
    _name='turismo.vinagre.tag'
    _rec_name='name'
    
    #Fields
    name = fields.Char('Name', size=80, translate=True)
    
vinagre_tag()

class award_tag(models.Model):
    _name='turismo.award.tag'
    _rec_name='name'
    
    #Fields
    name = fields.Char('Name', size=80, translate=True)
    
award_tag()

'''
Modelo de la tabla de relacion many2many entre Customers y products turisticos
'''
class contract_product_customer(models.Model):
    _name = 'turismo.contract_product_customer'
        
    @api.one
    @api.depends('product_tur_id')
    def get_categoria_publica(self):
        if self.product_tur_id and self.product_tur_id.public_categ_ids:
            self.public_category_id = self.product_tur_id.public_categ_ids[0]
    
       
    '''
    Metodo que genera una factura borrado asociada al product contratado y al customer
    '''
    @api.one
    def generar_factura_service(self):        
        ai_model = self.env['account.invoice']
        ail_model = self.env['account.invoice.line']
        #pydevd.settrace("192.168.3.1")
        #Para cada tarea del proyecto creamos una linea de factura
        if self.partner_id:
            partner = self.partner_id
            oo = self.env['turismo.opciones'].search([('name','=','Default')])            
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
            raise osv.except_osv(('Falta información'), ('No ha especificado Customer para el Proyecto...'))


    # Computed Fields
    @api.one
    @api.depends('image')
    def _get_image_thumb(self):
        for record in self:
            if record.image:
                record.image_thumb = crop_image(
                    record.image, ratio=(2,1), thumbnail_ratio=4, type='center')
            elif record.product_tur_id:
                record.image_thumb = crop_image(
                    record.product_tur_id.image, ratio=(2,1), thumbnail_ratio=4, type='center')
            else:
                record.image_thumb = False
                
    #@api.one
    #@api.constrains('image')
    #def _check_image(self):
    #    image_stream = StringIO.StringIO(self.image.decode('base64'))
    #    image = Image.open(image_stream)
    #    if int(image.size[0]) < 256 or int(image.size[1]) < 256:
    #        raise exceptions.ValidationError("Image width & height need be bigger than 256 pixels")
    
    
    #fields
    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    product_id = fields.Many2one('product.template', 'Service', required=True)
    product_tur_id = fields.Many2one('product.template', 'Product')
    establishment_id = fields.Many2one('turismo.establishment', 'establishment')
    image = fields.Binary('Image')
    image_thumb = fields.Binary('Thumbnail', compute="_get_image_thumb", store=True)
    url = fields.Char('Enlace', size=50)
    fecha_inicio = fields.Date('Init')
    fecha_fin = fields.Date('End')
    publicado = fields.Boolean('Published')
    public_category_id = fields.Many2one('product.public.category', 'Category', compute=get_categoria_publica)
    factura_id = fields.Many2one('account.invoice', 'Invoice')
    
contract_product_customer()

'''
Modelo que extiende product.public.category para agregar un campo booleano indicando
si la categoria esta asociada a links
Este modelo permite organizar los products en la zona publica
'''
class product_public_category(models.Model):
    _name='product.public.category'
    _inherit='product.public.category'
    
    #Fields
    link = fields.Boolean('Is link')
    
product_public_category()

'''
Modelos construidos mediante herencia de product.template
Tiene referencias many2one a las entidades de estructuras de product turistico
'''
class product_turismo(models.Model):
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
    # def _wine_default(self):
    #     wine_def = self.env['turismo.wine'].search([('id','=',99999)])
    #     if not wine_def:
    #         wine_def = self.env['turismo.wine'].create({'id':'99999'})
    #     else:
    #         wine_def = wine_def[0]
    #     return wine_def
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
    por defecto. En este caso si estan activados filtros de busqueda se preselecciona el type
    de product
    '''
    @api.model
    def default_get(self, fields):
        #pydevd.settrace("192.168.3.1")
        data = super(product_turismo, self).default_get(fields)
        if 'search_default_type_wine' in self.env.context:            
            data['type_product'] = ('wine','Wine')
        elif 'search_default_type_vinagre' in self.env.context:
            data['type_product'] = ('vinagre','Vinagre')            
        return data
    
    def is_seller_by(self, partner_id):
        ModelSupplierInfo = self.env['product.supplierinfo']
        for record in self:
            supplierinfo_id = ModelSupplierInfo.search([('name','=',partner_id),('product_tmpl_id','=',record.id)])
            return True if supplierinfo_id else False
        
    
    #fields

    service = fields.Boolean('Link')
    link_size = fields.Selection([('S','S'),('M','M'),('H','H'),('V','V'),('XV','XV')], 'Link Size')
    link_position = fields.Selection([('Portada','Home'),('Directorio','Wines')],
                                     'Ubicación del Link')    
    
    type_product = fields.Selection([('wine','Wine'), ('vinagre','Vinagre')],
                                     'Product Turistic type')    

    '''
    El atributo delegate=True permite acceder a los fields del modelo relacionado directamente desde el
    modelo actual, sin embargo requiere que los campos de relacion sean definidos
    '''
    grape = fields.Many2one('turismo.grape.tag', string='Grape')
    typewine = fields.Many2one('turismo.wine.tag', string='Type')
    typevinagre = fields.Many2one('turismo.vinagre.tag', string='Type')
    anho = fields.Char('Year', size=30)
    awards = fields.Many2many('turismo.award.tag', string='Awards')
    establishment_id = fields.Many2one('turismo.establishment', 'Winecellar', domain="[('type', '=', 'winecellar')]")


product_turismo()
