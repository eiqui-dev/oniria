# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
import re
from fnmatch import translate

class establishment(models.Model):
    _name = 'turismo.establishment'
    _inherit = 'turismo.establishment'
    
    schedule = fields.One2many('establishment.calendar.attendance', 'establishment_id',string='Schedule')
    
establishment()