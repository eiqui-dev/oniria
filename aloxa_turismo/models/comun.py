# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Solucións Aloxa S.L. <info@aloxa.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
#===============================================================================
# # REMOTE DEBUG
#import pydevd
# 
# # ...
# 
# # breakpoint
#pydevd.settrace("10.0.3.1")
#===============================================================================
from openerp import models, fields, api
from PIL import Image
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

class opciones(models.Model):
    _name = 'turismo.opciones'
    _rec_name = 'nombre'
    #Fields
    nombre=fields.Char('Nombre', default=lambda self: "Default",)
    account_id=fields.Many2one('account.account', 'Cuenta Contable para Facturas Automaticas')   
    journal_id=fields.Many2one('account.journal', 'Diario para Facturas Automaticas')
   
opciones()

def crop_image(
        data, type='top', ratio=False,
        thumbnail_ratio=None, image_format="PNG"):
    """ Used for cropping image and create thumbnail
        :param data: base64 data of image.
        :param type: Used for cropping position possible
            Possible Values : 'top', 'center', 'bottom'
        :param ratio: Cropping ratio
            e.g for (4,3), (16,9), (16,10) etc
            send ratio(1,1) to generate square image
        :param thumbnail_ratio: It is size reduce ratio for thumbnail
            e.g. thumbnail_ratio=2 will reduce your 500x500 image converted
            in to 250x250
        :param image_format: return image format PNG,JPEG etc
    """
    if not data:
        return False
    image_stream = Image.open(StringIO.StringIO(data.decode('base64')))
    output_stream = StringIO.StringIO()
    w, h = image_stream.size
    new_h = h
    new_w = w

    if ratio:
        w_ratio, h_ratio = ratio
        new_h = (w * h_ratio) / w_ratio
        new_w = w
        if new_h > h:
            new_h = h
            new_w = (h * w_ratio) / h_ratio

    if type == "top":
        cropped_image = image_stream.crop((0, 0, new_w, new_h))
        cropped_image.save(output_stream, format=image_format)
    elif type == "center":
        cropped_image = image_stream.crop(
            ((w - new_w) / 2, (h - new_h) / 2, (w + new_w) / 2,
             (h + new_h) / 2))
        cropped_image.save(output_stream, format=image_format)
    elif type == "bottom":
        cropped_image = image_stream.crop((0, h - new_h, new_w, h))
        cropped_image.save(output_stream, format=image_format)
    else:
        raise ValueError('ERROR: invalid value for crop_type')
    # TDE FIXME: should not have a ratio, makes no sense ->
    # should have maximum width (std: 64; 256 px)
    if thumbnail_ratio:
        thumb_image = Image.open(StringIO.StringIO(output_stream.getvalue()))
        thumb_image.thumbnail(
            (new_w / thumbnail_ratio, new_h / thumbnail_ratio),
            Image.ANTIALIAS)
        thumb_image.save(output_stream, image_format)
    return output_stream.getvalue().encode('base64')