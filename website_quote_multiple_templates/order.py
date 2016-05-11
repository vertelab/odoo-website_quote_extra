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

from openerp import models, fields, api, _, tools
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import http
from openerp.http import request
import datetime
import time


import openerp

import logging
_logger = logging.getLogger(__name__)

class sale_quote_template(models.Model):
    _inherit = "sale.quote.template"

    def _def_qweb_id(self):
        return self.env.ref('website_quote.so_template').id
    qweb_id = fields.Many2one(string="Qweb template",comodel_name="ir.ui.view",domain="[('type','=','qweb'),('mode','=','primary')]",default=_def_qweb_id)

class sale_quote(openerp.addons.website_quote.controllers.main.sale_quote):
    @http.route([
        "/quote/<int:order_id>",
        "/quote/<int:order_id>/<token>"
    ], type='http', auth="public", website=True)
    def view(self, order_id, token=None, message=False, **post):
        # use SUPERUSER_ID allow to access/view order for public user
        # only if he knows the private token
        order = request.registry.get('sale.order').browse(request.cr, token and SUPERUSER_ID or request.uid, order_id, request.context)
        now = time.strftime('%Y-%m-%d')
        if token:
            if token != order.access_token:
                return request.website.render('website.404')
            # Log only once a day
            if request.session.get('view_quote',False)!=now:
                request.session['view_quote'] = now
                body=_('Quotation viewed by customer')
                self.__message_post(body, order_id, type='comment')
        days = 0
        if order.validity_date:
            days = (datetime.datetime.strptime(order.validity_date, '%Y-%m-%d') - datetime.datetime.now()).days + 1
        values = {
            'quotation': order,
            'message': message and int(message) or False,
            'option': bool(filter(lambda x: not x.line_id, order.options)),
            'order_valid': (not order.validity_date) or (now <= order.validity_date),
            'days_valid': days,
        }
        _logger.warn('Template %s' % order.template_id.qweb_id and order.template_id.qweb_id.xml_id or 'website_quote.so_quotation')
        return request.website.render(order.template_id.qweb_id and order.template_id.qweb_id.xml_id or 'website_quote.so_quotation', values)
