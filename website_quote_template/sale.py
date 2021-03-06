# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, api, models, _

import logging
_logger = logging.getLogger(__name__)

class sale_quote_template(models.Model):
    _inherit = 'sale.quote.template'

    detail_description = fields.Html('Detail Description')
    reference = fields.Html('Reference')


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    view_on_quote = fields.Boolean(string="Q",help="View on quotation")
    @api.one
    @api.depends('product_id.lst_price', 'price_unit', 'discount')
    def _given_discount(self):
        if self.product_id.lst_price > 1: # not individual price
            #~ self.given_discount = (1 - self.discounted_price / self.price_unit) * 100
            self.given_discount = (1 - self.price_unit  / self.product_id.lst_price) * 100
            if self.discount != 0:
                self.given_discount = (1- self.given_discount / 100) * self.discount
    given_discount = fields.Float(compute='_given_discount')

    @api.multi
    def product_id_change(self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):
        result = super(sale_order_line, self).product_id_change(pricelist, product, qty, uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag)
        product = self.env['product.product'].with_context(lang=self.order_id.partner_id.lang).browse(product)
        result['value']['price_unit'] = product.list_price
        if product and pricelist:
            pricelist = self.env['product.pricelist'].browse(pricelist)
            result['value']['discount'] = (1 - pricelist.price_get(product.id, qty, partner_id)[pricelist.id] / result['value']['price_unit']) * 100
            # need round price_subtotal
        return result


class sale_order_option(models.Model):
    _inherit = 'sale.order.option'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        super(sale_order_option, self)._onchange_product_id()
        product = self.product_id.with_context(lang=self.order_id.partner_id.lang)
        self.price_unit = product.list_price
        if product and self.order_id.pricelist_id:
            partner_id = self.order_id.partner_id.id
            pricelist = self.order_id.pricelist_id.id
            discounted_price = self.order_id.pricelist_id.price_get(product.id, self.quantity, partner_id)[pricelist]
            self.discount = (1 - discounted_price / self.price_unit) * 100


class sale_order(models.Model):
    _inherit='sale.order'

    @api.one
    @api.depends('order_line')
    def _compute_order_line_monthly(self):
        month = self.env.ref('website_quote_template.product_uom_month')
        self.order_line_monthly = self.order_line.filtered(lambda x: x.product_id and x.product_id.uom_id == month)

    @api.one
    @api.depends('order_line_monthly')
    def _compute_order_line_monthly_untaxed(self):
        tot = 0.0
        for line in self.order_line_monthly:
            tot += line.price_subtotal
        self.order_line_monthly_untaxed = tot

    @api.one
    @api.depends('order_line_monthly')
    def _compute_order_line_monthly_tax(self):
        tot = 0.0
        for line in self.order_line_monthly:
            tot += self._amount_line_tax(line)
        self.order_line_monthly_tax = tot

    @api.one
    @api.depends('order_line_monthly_untaxed', 'order_line_monthly_tax')
    def _compute_order_line_monthly_total(self):
        self.order_line_monthly_total = self.order_line_monthly_untaxed + self.order_line_monthly_tax

    @api.one
    @api.depends('order_line')
    def _compute_order_line_normal(self):
        month = self.env.ref('website_quote_template.product_uom_month')
        self.order_line_normal = self.order_line.filtered(lambda x: not (x.product_id and x.product_id.uom_id == month))

    @api.one
    @api.depends('order_line_normal')
    def _compute_order_line_normal_untaxed(self):
        tot = 0.0
        for line in self.order_line_normal:
            tot += line.price_subtotal
        self.order_line_normal_untaxed = tot

    @api.one
    @api.depends('order_line_normal')
    def _compute_order_line_normal_tax(self):
        tot = 0.0
        for line in self.order_line_normal:
            tot += self._amount_line_tax(line)
        self.order_line_normal_tax = tot

    @api.one
    @api.depends('order_line_normal_untaxed', 'order_line_normal_tax')
    def _compute_order_line_normal_total(self):
        self.order_line_normal_total = self.order_line_normal_untaxed + self.order_line_normal_tax

    @api.one
    @api.depends('order_line_normal', 'order_line_normal_tax')
    def _compute_order_line_normal_undiscounted(self):
        total = 0.0
        for line in self.order_line_normal:
            total += line.price_subtotal + line.price_unit * ((line.discount or 0.0) / 100.0) * line.product_uom_qty
        self.order_line_normal_undiscounted = total

    @api.one
    @api.depends('order_line_monthly', 'order_line_monthly_tax')
    def _compute_order_line_monthly_undiscounted(self):
        total = 0.0
        for line in self.order_line_monthly:
            total += line.price_subtotal + line.price_unit * ((line.discount or 0.0) / 100.0) * line.product_uom_qty
        self.order_line_monthly_undiscounted = total

    order_line_normal = fields.One2many('sale.order.line', compute='_compute_order_line_normal')
    order_line_normal_untaxed = fields.Float(compute='_compute_order_line_normal_untaxed')
    order_line_normal_tax = fields.Float(compute='_compute_order_line_normal_tax')
    order_line_normal_total = fields.Float(compute='_compute_order_line_normal_total')
    order_line_normal_undiscounted = fields.Float(compute='_compute_order_line_normal_undiscounted')

    order_line_monthly = fields.One2many('sale.order.line', compute='_compute_order_line_monthly')
    order_line_monthly_untaxed = fields.Float(compute='_compute_order_line_monthly_untaxed')
    order_line_monthly_tax = fields.Float(compute='_compute_order_line_monthly_tax')
    order_line_monthly_total = fields.Float(compute='_compute_order_line_monthly_total')
    order_line_monthly_undiscounted = fields.Float(compute='_compute_order_line_monthly_undiscounted')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
