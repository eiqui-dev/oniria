# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP SA (http://www.openerp.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import datetime
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from operator import itemgetter

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare
from openerp.tools.translate import _
import pytz

class establishment_calendar_attendance(osv.osv):
    _name = "establishment.calendar.attendance"
    _description = "Work Detail"

    _columns = {
        'name' : fields.char("Name", required=True, translate=True),
        'dayofweek': fields.selection([('0','Monday'),('1','Tuesday'),('2','Wednesday'),('3','Thursday'),('4','Friday'),('5','Saturday'),('6','Sunday')], 'Day of Week', required=True, select=True),
        'date_from' : fields.date('Starting Date'),
        'hour_from' : fields.float('Work from', required=True, help="Start and End time of working.", select=True),
        'hour_to' : fields.float("Work to", required=True),
        'establishment_id' : fields.many2one("turismo.establishment", "calendario", help="If empty, this is a generic holiday for the company. If a establishment is set, the holiday/leave is only for this establishment"),
    }

    _order = 'dayofweek, hour_from'

    _defaults = {
        'dayofweek' : '0'
    }

def hours_time_string(hours):
    """ convert a number of hours (float) into a string with format '%H:%M' """
    minutes = int(round(hours * 60))
    return "%02d:%02d" % divmod(minutes, 60)