# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
import re
from fnmatch import translate
from comun import crop_image
#import pydevd

class establishment_images(models.Model):
    _name = 'establishment.images'
    _description="Add Multiple Image in establishment"

    name = fields.Char('Label')
    image = fields.Binary('Image')
    sequence = fields.Integer('Sort Order')
    establishment_tmpl_id = fields.Many2one('turismo.establishment', 'establishment')
    more_view_exclude = fields.Boolean("More View Exclude")
    
establishment_images()

class establishment_services(models.Model):
    _name = 'establishment.services'
    _description = "Services available"
    
    name = fields.Char('Name')
    description = fields.Char('Description')
    icon = fields.Char('Awesome Icon')
    
    _sql_constraints = [
        ('icon', 'unique(icon)', 'Please enter Unique Icon'),
    ]

'''
Modelo comun con campos comunes a establishments
'''
class establishment(models.Model):
    _name = 'turismo.establishment'
    _inherits = {'res.partner': 'partner_id'}
    
    def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
        """ Wrapper on the user.partner onchange_address, because some calls to the
            partner form view applied to the user may trigger the
            partner.onchange_type method, but applied to the user object.
        """
    #    partner_ids = [establishment.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
    #    return self.pool['res.partner'].onchange_address(cr, uid, partner_ids, use_parent_address, parent_id, context=context)

    def _check_company(self, cr, uid, ids, context=None):
        return all(((this.company_id in this.company_ids) or not this.company_ids) for this in self.browse(cr, uid, ids, context))

    _constraints = [
        (_check_company, 'The chosen company is not in the allowed companies for this user', ['company_id', 'company_ids']),
    ]

    #_sql_constraints = [
    #    ('login_key', 'UNIQUE (login)',  'You can not have two users with the same login !')
    #]

    def _get_company(self,cr, uid, context=None, uid2=False):
        if not uid2:
            uid2 = uid
        # Use read() to compute default company, and pass load=_classic_write to
        # avoid useless name_get() calls. This will avoid prefetching fields
        # while computing default values for new db columns, as the
        # db backend may not be fully initialized yet.
        user_data = self.pool['turismo.establishment'].read(cr, uid, uid2, ['company_id'],
                                                context=context, load='_classic_write')
        comp_id = user_data['company_id']
        return comp_id or False
    
    @api.multi
    def onchange_state(self, state_id):
        if state_id:
            state = self.env['res.country.state'].browse(state_id)
            return {'value': {'country_id': state.country_id.id}}
        return {}
    
    def default_image(self):        
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
    
    def default_email(self):        
        if 'res_partner_id' in self.env.context:
            partner = self.env['res.partner'].search([('id','=',self.env.context['res_partner_id'])])
            return partner.email
        return ''
    
    def default_phone(self):        
        if 'res_partner_id' in self.env.context:
            partner = self.env['res.partner'].search([('id','=',self.env.context['res_partner_id'])])
            return partner.phone
        return ''
    
    @api.onchange('res_partner_id')
    def onchange_res_partner_id(self):
        self.parent_id = self.res_partner_id
    
    # Public Methods
    def get_tripadvisor_id(self):
        matchObj = re.match('^https?://.+-d([0-9]+).+\.html$', self.tripadvisor_url, re.IGNORECASE)
        return int(matchObj.group(1)) if matchObj else -1
    
    # Constraints
    @api.one
    @api.constrains('tripadvisor_url')
    def _check_tripadvisor_url(self):
        if self.tripadvisor_url and not re.match('^https?://.+-d[0-9]+.+\.html$', 
                                                 self.tripadvisor_url, re.IGNORECASE):
            raise exceptions.ValidationError("Url de TripAdvisor Incorrecta")
        
    # Computed Fields
    @api.one
    @api.depends('image')
    def _get_image_thumb(self):
        for record in self:
            if record.image:
                record.image_thumb = crop_image(
                    record.image, ratio=(2,1), thumbnail_ratio=4, type='center')
            else:
                record.image_thumb = False
    
    #fields
    partner_id = fields.Many2one('res.partner')
    res_partner_id = fields.Many2one('res.partner', 'Customer', required=True ,default=default_res_partner_id)   
    latitude = fields.Float('Latitude', digits=(6,3))
    longitude = fields.Float('Longitude', digits=(6,3))
    image = fields.Binary('Image', default=default_image)
    image_thumb = fields.Binary('Thumbnail', compute="_get_image_thumb", store=True)
    description = fields.Text(string='Description', translate=True)   
    #direccion = fields.Char(string='Dirección', size=120, default=default_direccion, translate=True)
    #locality = fields.Char(string='locality', size=120, default=default_locality, translate=True)
    schedule = fields.Char(string='Schedule', size=120)
    res_partner_id = fields.Many2one('res.partner', 'Customer', default=default_res_partner_id)   
    tripadvisor_url = fields.Char(string="TripAdvisor Url", size=255)
    languages = fields.Many2many('turismo.language.tag', string='Languages')
    region = fields.Many2many('turismo.region.tag', string='Region')
    type_s = fields.Selection([('winecellar','Winecellar'), ('restaurant','Restaurant'),('lodging','Lodging'),('cultural','Art and Culture'),('winebar','Winebar'), ('vineyard','Vineyard'),('other','Other')],'Establishment Type', translate=True, required=True)    
    web = fields.Char(string="Web", size=255, default=default_web)
    website_published = fields.Boolean('WebSite Published', copy=False)
    images = fields.One2many('establishment.images', 'establishment_tmpl_id',string='Images')
    services = fields.Many2many('establishment.services',string='Services')
    email = fields.Char(string="Email", default=default_email)
    phone = fields.Char(string="Phone", default=default_phone)
    
establishment()
    

'''
Modelo para tags de languages
'''
class region_tag(models.Model):
    _name='turismo.region.tag'
    _rec_name='name'
    
    #Fields
    name = fields.Char('Name', size=80, translate=True)
    
region_tag()

'''
Modelo para tags de languages
'''
class language_tag(models.Model):
    _name='turismo.language.tag'
    _rec_name='name'
    
    #Fields
    name = fields.Char('Name', size=80, translate=True)
    
language_tag()


'''
Modelo para Winecellars
Hereda del modelo comun turismo.establishment

class winecellar(models.Model):
    _name = 'turismo.winecellar'
    _rec_name = 'name'
    _inherits = {'turismo.establishment':'establishment_id'}   
    #_inherit = 'turismo.establishment'
    
    # Metodo requerido en el directorio de establishments cuando se filtra por winecellar
    def get_tripadvisor_id(self):
        matchObj = re.match('^https?://.+-d([0-9]+).+\.html$', self.tripadvisor_url, re.IGNORECASE)
        return int(matchObj.group(1)) if matchObj else -1
    
    establishment_id = fields.Many2one('turismo.establishment', 'establishment')
    partner_id = fields.Many2one('res.partner', 'Customer')
    winecellar_product_ids = fields.One2many('product.template', 'winecellar_id', 'Products de la Winecellar')
    
winecellar()
'''
'''
Modelo para Restaurants
Hereda del modelo comun turismo.establishment

class restaurant(models.Model):
    _name = 'turismo.restaurant'
    _rec_name = 'name'
    _inherits = {'turismo.establishment':'establishment_id'}
    #_inherit = 'turismo.establishment'    
 
    establishment_id = fields.Many2one('turismo.establishment', 'establishment')
    partner_id = fields.Many2one('res.partner', 'Customer')
    #restaurant_product_ids = fields.One2many('product.template', 'restaurant_id', 'Products del Restaurant')
    
restaurant()
'''
'''
Modelo para Lodgings
Hereda del modelo comun turismo.establishment

class lodging(models.Model):
    _name = 'turismo.lodging'
    _rec_name = 'name'
    _inherits = {'turismo.establishment':'establishment_id'}
    #_inherit = 'turismo.establishment'    

    establishment_id = fields.Many2one('turismo.establishment', 'establishment')    
    partner_id = fields.Many2one('res.partner', 'Customer')
    #lodging_product_ids = fields.One2many('product.template', 'lodging_id', 'Products del Lodging')
    
lodging()
'''
'''
Modelo para establishment de Art and Culture
Hereda del modelo comun turismo.establishment

class cultural(models.Model):
    _name = 'turismo.cultural'
    _rec_name = 'name'
    _inherits = {'turismo.establishment':'establishment_id'}
    #_inherit = 'turismo.establishment'    
    
    establishment_id = fields.Many2one('turismo.establishment', 'establishment')
    partner_id = fields.Many2one('res.partner', 'Customer')
    #cultural_product_ids = fields.One2many('product.template', 'cultural_id', 'Products de Art and Culture')
    
cultural()
'''
'''
Modelo para winebars
Hereda del modelo comun turismo.establishment

class winebar(models.Model):
    _name = 'turismo.winebar'
    _rec_name = 'name'
    _inherits = {'turismo.establishment':'establishment_id'}
    #_inherit = 'turismo.establishment'    

    establishment_id = fields.Many2one('turismo.establishment', 'establishment')    
    partner_id = fields.Many2one('res.partner', 'Customer')
    #winebar_product_ids = fields.One2many('product.template', 'winebar_id', 'Products de winebar')
    
winebar()
'''
'''
Modelo para establishment de other type
Hereda del modelo comun turismo.establishment

class other(models.Model):
    _name = 'turismo.other'
    _rec_name = 'name'
    _inherits = {'turismo.establishment':'establishment_id'}
    #_inherit = 'turismo.establishment'    
    
    establishment_id = fields.Many2one('turismo.establishment', 'establishment')
    partner_id = fields.Many2one('res.partner', 'Customer')
    #other_product_ids = fields.One2many('product.template', 'other	_id', 'Products del establishment')
    
other()
'''
'''
Modelo extension de res.partner que registra fields Many2one a los posibles
establishments definidos con anterioridad
'''
class res_partner_turismo(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
      
    #fields
    '''
    Relacionales para los establishments del Customer
    
    winecellar_ids = fields.One2many('turismo.winecellar', 'partner_id', 'Winecellars')
    restaurant_ids = fields.One2many('turismo.restaurant', 'partner_id', 'Restaurants')
    lodging_ids = fields.One2many('turismo.lodging', 'partner_id', 'Lodgings')
    cultural_ids = fields.One2many('turismo.cultural', 'partner_id', 'Art and Culture')
    winebar_ids = fields.One2many('turismo.winebar', 'partner_id', 'winebars')    
    other_ids = fields.One2many('turismo.other', 'partner_id', 'Others')       
''' 
    establishment_ids = fields.One2many('turismo.establishment', 'res_partner_id', 'establishments')
    contract_product_customer_ids = fields.One2many('turismo.contract_product_customer',
                                                     'partner_id', string='Contract Products')
    
res_partner_turismo()

#===============================================================================
# '''
# Modelo extension de res.partner que registra fields Many2one a los posibles
# establishments definidos con anterioridad
# '''
# class establishment(models.Model):
#     _name = 'res.partner'
#     _inherit = 'res.partner'    
#     
#     '''
#     La inicializacion por defecto es necesaria ya que el mecanismo delegate=True
#     requiere que los campos esten definidos
#     '''
#     def _winecellar_default(self):
#         winecellar_def = self.env['turismo.winecellar'].search([('winecellar_name','=','-')])
#         if not winecellar_def:
#             winecellar_def = self.env['turismo.winecellar'].create({'winecellar_name':'-'})
#         else:
#             winecellar_def = winecellar_def[0]
#         return winecellar_def
#     
#     def _restaurant_default(self):
#         restaurant_def = self.env['turismo.restaurant'].search([('restaurant_name','=','-')])
#         if not restaurant_def:
#             restaurant_def = self.env['turismo.restaurant'].create({'restaurant_name':'-'})
#         else:
#             restaurant_def = restaurant_def[0]
#         return restaurant_def
#     
#     def _lodging_default(self):
#         lodging_def = self.env['turismo.lodging'].search([('lodging_name','=','-')])
#         if not lodging_def:
#             lodging_def = self.env['turismo.lodging'].create({'lodging_name':'-'})
#         else:
#             lodging_def = lodging_def[0]
#         return lodging_def
#       
#     #fields
#     '''
#     El atributo delegate=True permite acceder a los fields del modelo relacionado directamente desde el
#     modelo actual, sin embargo requiere que los campos de relacion sean definidos
#     '''
#     winecellar_id = fields.Many2one('turismo.winecellar', 'Winecellar', delegate=True, default=_winecellar_default)
#     restaurant_id = fields.Many2one('turismo.restaurant', 'Restaurant', delegate=True, default=_restaurant_default)
#     lodging_id = fields.Many2one('turismo.lodging', 'Lodging', delegate=True, default=_lodging_default)        
#         
# establishment()
#===============================================================================
