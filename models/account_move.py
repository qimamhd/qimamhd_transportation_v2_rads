# -*- coding: utf-8 -*-
from odoo import models, fields, api, _,tools
from odoo.exceptions import ValidationError
from datetime import datetime

class xx_account_move(models.Model):
    _inherit = 'account.move'

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

    def post(self):
        for rec in self:
            if rec.type == 'out_invoice':
                print("preventing_credit_inv",self.user_has_groups('qimamhd_preventing_credit_inv.group_allow_credit_inv_priv'))
                if rec.preventing_credit_inv and not self.user_has_groups('qimamhd_preventing_credit_inv.group_allow_credit_inv_priv') and  rec.partner_id.partner_dealing_invoice != 'credit':
                    partner_balance = rec.validation_customer_balance(rec.partner_id)
                    if partner_balance >= 0:
                        raise ValidationError( " تنبيه .. لا يمكن البيع بالاجل للعميل يجب اضافة دفع للعميل"
                                 )
                    if partner_balance < 0 and abs(partner_balance) < rec.amount_total:
                        raise ValidationError( " تنبيه .. لا يمكن البيع بالاجل للعميل المدفوعات [%s] اقل من قيمة الفاتورة" %  abs(partner_balance)
                                 )
        
        invoice = super(xx_account_move, self).post()
        return invoice
    
    def validation_customer_balance(self,p_id):
        partner = self.env['res.partner'].search([])
        select = []

        for p_receivable in partner.property_account_receivable_id:
            select.append(p_receivable.id)
        for p_payable in partner.property_account_payable_id:

            select.append(p_payable.id)

        account_ids = self.env['account.move.line'].search([('account_internal_type', 'in',['receivable','payable'])])
        for m in account_ids.account_id:
            select.append(m.id)
         
            account_move = self.env['account.move.line'].search(
                [('partner_id', '=', p_id.id), ('account_id', 'in', select),
                 ('move_id.state', 'in', ['posted'])])
        balance = sum(l.balance for l in account_move)
        return balance