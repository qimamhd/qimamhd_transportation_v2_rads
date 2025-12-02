# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class transportation(models.Model):
    _inherit = 'trnsp.transportation.mst'

    
    driver_btrip_selection = fields.Selection(
        [('percentage', 'نسبة'), ('amount', 'مبلغ')], string='العمولة للسائق',
         copy=False, index=True, tracking=3, default='amount',required=True)
         
    driver_btrip_amount = fields.Float(string="عمولة السائق")

    booking_fees = fields.Float(string="رسوم حجز موعد")
    
    storage_fees = fields.Float(string="رسوم ساحة(تخزين)")
 
    expense_driver_entry_id = fields.Many2one('account.move', string="سند اثبات للسائق", readonly=True, copy=False)

    @api.onchange('driver_btrip_selection')
    def reset_value_btrip(self):
        for rec in self:
            rec.driver_btrip_amount = 0
            rec.company_driver_perc = 0
    
    def create_purchase_btn(self):
        
        res = super(transportation,self).create_purchase_btn()
        for rec in self:

            if not rec.company_id.driver_expense_account_id:
                raise ValidationError("تنبيه .. يجب تحديد حساب مصروف ردود السائقين في التهيئة")
           
            if rec.company_car_flag:
                if not rec.company_driver_id:
                        raise ValidationError("تنبيه .. يجب تحديد سائق الشركة")
            
            if rec.company_car_flag:
                if not rec.company_driver_id:
                    raise ValidationError("تنبيه .. يجب تحديد سائق الشركة")
         
            if rec.driver_btrip_amount and rec.company_driver_id and not rec.company_driver_id.employee_account_id:
                raise ValidationError("تنبيه .. يجب تحديد حساب راتب السائق في شاشة الموظفين")


            if rec.driver_btrip_amount and rec.company_driver_id.employee_account_id and rec.company_id.driver_expense_account_id:
                description = 'رقم البوليصة: ' + str(rec.invoice_manual) + ' - الوجهة: [من ' +  str(rec.transp_path_from.name) + ' - الى ' + str(rec.transp_path_to.name) + '] ' + ' - تاريخ التحميل : ' + str(rec.load_date) if rec.load_date else ''  + ' - العميل: ' + str(rec.partner_branch_id.name),
                line_ids = []

                debit_vals = (0, 0, {
                                'name':description,
                                'amount_currency': 0.0,

                                'company_currency_id':rec.company_id.currency_id.id,
                                'debit': rec.driver_btrip_amount,
                                'credit': 0.0,
                                # 'balance': -(line.l_local_amount) if payment.check_multi_currency else -(line.l_payment_amount),
                                'date': rec.order_date,
                                'date_maturity': rec.order_date,
                                'account_id': rec.company_id.driver_expense_account_id.id,
                                'account_internal_type': rec.company_id.driver_expense_account_id.internal_type,
                                'analytic_account_id': rec.analytic_account_id.id if rec.company_id.driver_expense_account_id.internal_group == 'expense' else False,

                                # 'parent_state': 'posted',
                                'ref': 'الصرف للشحنة  : ' + str(rec.invoice_manual)  ,
                               'journal_id': rec.company_id.driver_journal_id.id,
                                'company_id':rec.company_id.id,
                                'quantity': 1,

                            })

                line_ids.append(debit_vals, )
                    
                credit_vals = (0, 0, {
                                'name': description,
                                'amount_currency': 0.0,

                                'company_currency_id': rec.company_id.currency_id.id,
                                'debit': 0.0,
                                'credit':  rec.driver_btrip_amount,
                                # 'balance': payment.local_amount if payment.check_multi_currency else payment.payment_amount,
                                'date': rec.order_date,
                                'date_maturity': rec.order_date,
                                'account_id': rec.company_driver_id.employee_account_id.id,
                                'account_internal_type':rec.company_driver_id.employee_account_id.internal_type,
                                # 'parent_state': 'posted',
                                'ref': 'الصرف للشحنة  : ' + str(rec.invoice_manual)  ,
                                'journal_id': rec.company_id.driver_journal_id.id,
                                'company_id': rec.company_id.id,
                                'quantity': 1,

                            })
                line_ids.append(credit_vals)

                    
                if line_ids:
                        mov_vals = {
                            'date': rec.order_date,
                            # 'ref': description,
                         
                            # 'state': 'posted',
                            'type': 'entry',
                             'journal_id': rec.company_id.driver_journal_id.id,
                            'company_id': rec.company_id.id,
                            'currency_id': rec.company_id.currency_id.id,
                            'purchase_transportation_id': rec.id,
                             'note_transportation': str(rec.notes if rec.notes else ' ') + ' - ' + str(
                            rec.abstract_notes if rec.abstract_notes else ' '),
                               'invoice_user_id': self.env.uid,
                            'line_ids': line_ids,
                        }

                        print(mov_vals)
                        if not rec.expense_driver_entry_id:
                            invoice = self.env['account.move'].create(mov_vals)
                            rec.purchase_invoice_flag = True

                            rec.write({'expense_driver_entry_id': invoice.id})
                           
                            action = self.env.ref('account.action_move_journal_line')
                            result = action.read()[0]
                            result.pop('id', None)
                            result['context'] = {}
                            result['domain'] = [('purchase_transportation_id', '=', rec.id)]

                            if invoice:
                                res = self.env.ref('account.view_move_form', False)
                                result['views'] = [(res and res.id or False, 'form')]
                                result['res_id'] = invoice.id or False

                            return result
                        if rec.expense_driver_entry_id:
                            mov_vals = {
                            'date': rec.order_date,
                            # 'ref': description,
                         
                            # 'state': 'posted',
                            'type': 'entry',
                            'journal_id': rec.company_id.driver_journal_id.id,
                            'company_id': rec.company_id.id,
                            'currency_id': rec.company_id.currency_id.id,
                            'purchase_transportation_id': rec.id,
                             'note_transportation': str(rec.notes if rec.notes else ' ') + ' - ' + str(
                                rec.abstract_notes if rec.abstract_notes else ' '),
                            'invoice_user_id': self.env.uid,
                            'line_ids': line_ids,
                                     }
    
    def call_purchase_invoice(self):
        for rec in self:

            action = self.env.ref('account.action_move_journal_line')
            result = action.read()[0]
            result.pop('id', None)
            result['context'] = {}
            result['domain'] = [('purchase_transportation_id', '=', rec.id)]
           
            return result