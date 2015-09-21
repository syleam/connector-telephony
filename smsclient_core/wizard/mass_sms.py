##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>)
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import re


class WizardSendSms(models.TransientModel):
    _name = 'wizard.send.sms'

    @api.model
    def _default_get_gateway(self):
        sms_client_obj = self.env['sms.smsclient']
        gateway_ids = sms_client_obj.search([], limit=1)
        return gateway_ids and gateway_ids[0] or False

    @api.onchange('gateway_id')
    def onchange_gateway_mass(self):
        for key in ['validity', 'classes', 'deferred', 'priority',
                    'coding', 'tag', 'nostop']:
            print key, self.gateway_id[key]
            self[key] = self.gateway_id[key]

    @api.model
    def _prepare_sms_vals(self, partner):
        return {
            'gateway_id': self.gateway_id.id,
            'state': 'draft',
            'message': self.message,
            'validity': self.validity,
            'classes': self.classes,
            'deferred': self.deferred,
            'priority': self.priority,
            'coding': self.coding,
            'tag': self.tag,
            'nostop': self.nostop,
            'partner_id': partner.id,
            'mobile': partner.mobile,
        }

    @api.multi
    def sms_mass_send(self):
        sms_obj = self.env['sms.sms']
        partner_obj = self.env['res.partner']
        for partner in partner_obj.browse(self._context.get('active_ids')):
            vals = self._prepare_sms_vals(partner)
            sms_obj.create(vals)

    gateway_id = fields.Many2one(
        'sms.smsclient',
        required=True,
        default=_default_get_gateway)
    message = fields.Text(required=True)
    validity = fields.Integer(
        help='The maximum time -in minute(s)- before the message is dropped')
    classes = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit'),
        ], help='The sms class: flash(0),phone display(1),SIM(2),toolkit(3)')
    deferred = fields.Integer(
        help='The time -in minute(s)- to wait before sending the message')
    priority = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
        ], help='The priority of the message')
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
        ], help='The sms coding: 1 for 7 bit or 2 for unicode')
    tag = fields.Char(size=256, help='An optional tag')
    nostop = fields.Boolean(
        help='Do not display STOP clause in the message, this requires that '
             'this is not an advertising message')