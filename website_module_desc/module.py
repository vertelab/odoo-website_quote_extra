# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
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
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from datetime import datetime
import werkzeug
import pytz

class website_module_desc(http.Controller):
        
#    @http.route(['/quote/module/<string:module>',], type='http', auth="user", website=True)
    @http.route(['/quote/<model("sale.order"):order>/module','/quote/<model("sale.order"):order>/module/<string:module>','/quote/<model("sale.order"):order>/module/<string:module>/anchor/<string:anchor>','/quote/module/<string:module>',], type='http', auth="public", website=True)
    #@http.route(['/quote/<model("sale.order"):order>/module/<string:module>','/quote/module/<string:module>',], type='http', auth="public", website=True)
    def module_description(self, order=False, module=False, anchor=False, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        if module:
            module_obj = request.env['ir.module.module'].search([('name','=',module)])[0]
            return request.website.render("website_module_desc.desc", {
                'module': module_obj,
                'anchor': anchor,
                'self': self,
                'sale_order': order,
            })
        return 


class product_template(models.Model):
    _inherit = 'product.template'
    
    quote_module_id = fields.Many2one('ir.module.module', string='Module')
