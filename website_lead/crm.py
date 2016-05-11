# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015- Vertel AB (<http://www.vertel.se>).
#
#    This progrupdateam is free software: you can redistribute it and/or modify
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

from openerp import models, fields, api, _
import openerp.tools
import xmlrpclib
from openerp.exceptions import Warning
import os, string
import logging
_logger = logging.getLogger(__name__)


class hr(models.Model):
    _inherit = 'hr.employee'


   

from openerp import http
from openerp.http import request

class website_crm(http.Controller):

    @http.route(['/consultants'], type='http', auth="public", website=True)
    def consultants(self, **post):
        return request.website.render("website_hr_cv.consultants_view", 
            {'employee_ids': request.env['hr.employee'].sudo().search([],order="name")})

    @http.route(['/consultant/<model("hr.employee"):employee>'], type='http', auth="public", website=True)
    def consultant(self, employee,**post):
        return request.website.render("website_hr_cv.employee_view", {'employee': request.env['hr.employee'].sudo().browse(employee.id)})
        
