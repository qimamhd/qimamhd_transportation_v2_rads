# -*- coding: utf-8 -*-
from odoo import models, fields, api, _,tools
from odoo.exceptions import ValidationError
from datetime import datetime

class xx_partner(models.Model):
    _inherit = 'res.partner'
    
    preventing_credit_inv = fields.Boolean(default=lambda self: self._default_preventing_credit_inv_flag(),
                                         compute="_get_preventing_credit_inv_flag")
    
    
    def _get_preventing_credit_inv_flag(self):

        params = self.env['ir.config_parameter'].sudo()
        l_preventing_credit_inv = params.get_param('preventing_credit_inv',
                                             default=False)
 
        for rec in self:
            rec.preventing_credit_inv = l_preventing_credit_inv

    def _default_preventing_credit_inv_flag(self):

        params = self.env['ir.config_parameter'].sudo()
        l_preventing_credit_inv = params.get_param('preventing_credit_inv',
                                             default=False)
 
        return l_preventing_credit_inv
    
    user_preventing_credit_inv = fields.Boolean(default=lambda self: self._default_user_preventing_credit_inv_flag(),
                                         compute="_get_user_preventing_credit_inv_flag")
   
    def _get_user_preventing_credit_inv_flag(self):  

        for rec in self:
            print("comp_user_preventing_credit_inv",self.user_has_groups('qimamhd_preventing_credit_inv.group_allow_partner_types_priv'))
            rec.user_preventing_credit_inv =  self.user_has_groups('qimamhd_preventing_credit_inv.group_allow_partner_types_priv')
    
    @api.model
    def _default_user_preventing_credit_inv_flag(self):
        print("ini_user_preventing_credit_inv",self.user_has_groups('qimamhd_preventing_credit_inv.group_allow_partner_types_priv'))

        return self.user_has_groups('qimamhd_preventing_credit_inv.group_allow_partner_types_priv')

    partner_dealing_invoice = fields.Selection([('cash','نقدي'),
                                     ('credit','اجل'),
                                     ], string="طبيعة التعامل مع العميل"
                                    )
    