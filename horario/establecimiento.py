# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
import re
from fnmatch import translate

class establecimiento(models.Model):
    _name = 'turismo.establecimiento'
    _inherit = 'turismo.establecimiento'
    
    horario = fields.One2many('establecimiento.calendar.attendance', 'establecimiento_id',string='Horario')
    
establecimiento()