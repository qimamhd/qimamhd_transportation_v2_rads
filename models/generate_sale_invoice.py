# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
 

class xx_generate_sale_mst(models.Model):
    _inherit = 'transp.generate.sale.invoice'

 
    def search_transportations_requests(self):
        for rec in self:

            if rec.branch_id:

                transportation_id = self.env['trnsp.transportation.mst'].search(
                    [('sale_invoice_id','=', False),('order_date', '>=', rec.order_date_from), ('order_date', '<=', rec.order_date_to),
                     ('partner_branch_id', '=', rec.partner_branch_id.id),('branch_id','in', rec.branch_id.ids),
                   
                     ('state','not in',['draft','cancel_order'])
                     ], order='load_date')
            else:
                transportation_id = self.env['trnsp.transportation.mst'].search(
                    [('sale_invoice_id','=', False) ,('order_date', '>=', rec.order_date_from), ('order_date', '<=', rec.order_date_to),
                     ('partner_branch_id', '=', rec.partner_branch_id.id),
                     ('sale_invoice_id', '=', False),('state','!=','draft')
                     ], order='load_date')

            line_ids = ""
            line_ids = self.env['transp.generate.sale.invoice.line'].search([('header_id','=', rec.id)]).unlink()
            if transportation_id:
                # line_ids = self.env['transp.generate.sale.invoice.line'].search([('header_id','=', rec.id)]).unlink()
                for line in transportation_id:
                    # acc_move_line = self.env['account.move.line'].search([('sale_transportation_id','=',line.id)])
                    # if acc_move_line:
                    #     raise ValidationError(
                    #         "تنبيه .. امر الشحن رقم (%s) مرحلة مسبقا للحسابات لذا لا يمكن التكرار .." % line.id)

                    line_ids = self.env['transp.generate.sale.invoice.line'].create({
                        'selected': True,
                        
                        'transportation_id': line.id,
                        'order_date': line.order_date,
                        'partner_branch_id': line.partner_branch_id.id,
                        'transp_path_from':line.transp_path_from.id,
                        'transp_path_to': line.transp_path_to.id,
                        'customer_price': line.customer_price,
                        'customer_stop': line.customer_stop,
                        'stopped_days': line.stopped_days,
                        'transportation_location': line.transportation_location.id,
                        'transp_charge_type': line.transp_charge_type.id,
                        'advanced_amount': line.advanced_amount,
                        'branch_id': line.branch_id.id,
                        'company_id': line.company_id.id,
                        'notes': str(line.notes if line.notes else ''  + ' - ' if line.notes else '') + str(
                            line.abstract_notes if line.abstract_notes else ' '),
                        'invoice_manual': str(line.invoice_manual),
                        'load_date': line.load_date,
                        'header_id': rec.id,
                        'booking_fees': line.booking_fees,
                        'storage_fees': line.storage_fees,
                         'analytic_account_id': line.analytic_account_id.id,

                        
                        })

                line_ids = self.env['transp.generate.sale.invoice.line'].search([('header_id', '=', rec.id)])
              
    @api.onchange('company_id')
    def _get_allowed_branch_ids(self):
        print(self.env.user.sudo().allowed_branch_ids)

        select = [(i['id']) for i in self.env.user.sudo().allowed_branch_ids]
        allows_branches = self.env['custom.branches'].search([('id', 'in', select)])
        return {'domain': {'branch_id': [('id', 'in', select)]}}

   
    def generate_btn(self):
        for rec in self:
                if not rec.lines:
                    raise ValidationError(
                        "تنبيه .. لاتوجد بيانات لتوليد فواتيرها ..")

                if rec.posted_options == 'all_user_branch':
                    inv_line_ids = []
                    for line in rec.lines:
                        if line.selected:
                            transp_invoice_id = self.env['account.move.line'].search([('sale_transportation_id', '=', line.transportation_id.id)])
                            if transp_invoice_id:
                                line.transportation_id.write({'sale_invoice_flag': True})

                                line.transportation_id.write({'sale_invoice_id':transp_invoice_id.move_id.id})
                              
                                # raise ValidationError(
                                #     "تنبيه .. بوليصة الشحن رقم (%s) مرتبطة مسبقا بفاتورة مبيعات رقم (%s) .." % (line.invoice_manual,transp_invoice_id.move_id.name))
                            else:
                                if not line.transp_charge_type.product_id:
                                    raise ValidationError(
                                        "تنبيه .. يجب تحديد الصنف الخدمي المقابل لنوع الشحن من شاشة انواع الشحن ..")
                                transport_line_ids = {
                                    'product_id': line.transp_charge_type.product_id.id,
                                    'name': line.transp_path_from.name + " - " + line.transp_path_to.name,
                                    'quantity': 1,
                                    'product_uom_id': line.transp_charge_type.product_id.uom_id.id,
                                    'discount': False,
                                    'price_unit': line.customer_price + (line.customer_stop * line.stopped_days),
                                    'tax_ids': [(6, 0, line.transp_charge_type.product_id.taxes_id.ids)],
                                    'analytic_account_id': line.analytic_account_id.id,
                                    # 'tax_id': product_mislead_id.taxes_id.id,
                                    'company_id': rec.company_id.id,
                                    'company_currency_id': rec.env.company.currency_id.id,
                                    'sale_transportation_id': line.transportation_id.id,
                                    'note_transportation': str(line.notes if line.notes else ' '),
                                    'invoice_manual': line.invoice_manual if line.invoice_manual else ' ',
                                    'customer_price': line.transportation_id.customer_price,
                                    'customer_stop': line.transportation_id.customer_stop,
                                    'supplier_price': line.transportation_id.supplier_price,
                                    'supplier_stop': line.transportation_id.supplier_stop,
                                    'stopped_days': line.transportation_id.stopped_days,

                                }

                                inv_line_ids.append((0, 0, transport_line_ids))
                                
                                if line.booking_fees:
                                    transport_line_ids = {
                                    'product_id': line.transp_charge_type.product_id.id,
                                    'name': line.transp_path_from.name + " - " + line.transp_path_to.name + "( رسوم حجز موعد )",
                                    'quantity': 1,
                                    'product_uom_id': line.transp_charge_type.product_id.uom_id.id,
                                    'discount': False,
                                    'price_unit': line.booking_fees,
                                    'tax_ids': [(6, 0, line.transp_charge_type.product_id.taxes_id.ids)],
                                    'analytic_account_id': line.analytic_account_id.id,
                                    # 'tax_id': product_mislead_id.taxes_id.id,
                                    'company_id': rec.company_id.id,
                                    'company_currency_id': rec.env.company.currency_id.id,
                                    'sale_transportation_id': line.transportation_id.id,
                                    'invoice_manual': line.invoice_manual if line.invoice_manual else ' ',
                                    }

                                    inv_line_ids.append((0, 0, transport_line_ids))
                                
                                if line.storage_fees:
                                    transport_line_ids = {
                                    'product_id': line.transp_charge_type.product_id.id,
                                    'name': line.transp_path_from.name + " - " + line.transp_path_to.name + "( رسوم ساحة- تخزين)",
                                    'quantity': 1,
                                    'product_uom_id': line.transp_charge_type.product_id.uom_id.id,
                                    'discount': False,
                                    'price_unit': line.storage_fees,
                                    'tax_ids': [(6, 0, line.transp_charge_type.product_id.taxes_id.ids)],
                                    'analytic_account_id': line.analytic_account_id.id,
                                    # 'tax_id': product_mislead_id.taxes_id.id,
                                    'company_id': rec.company_id.id,
                                    'company_currency_id': rec.env.company.currency_id.id,
                                    'sale_transportation_id': line.transportation_id.id,
                                    'invoice_manual': line.invoice_manual if line.invoice_manual else ' ',
                                    }

                                    inv_line_ids.append((0, 0, transport_line_ids))


                    if inv_line_ids:
                        journal_id = self.env['account.journal'].search(
                            [('branch_id', '=', self.env.user.branch_id.id), ('type', '=', 'sale')], limit=1)
                        journal_sale = ""
                        if journal_id:
                            journal_sale = journal_id.id
                        else:
                            journal_id = self.env['account.journal'].search(
                                [('type', '=', 'sale')], limit=1)

                            journal_sale = journal_id.id
                        move1 = self.env['account.move'].search([('generate_sale_id', '=', rec.id)])

                        if not move1:
                            invoice = self.env['account.move'].create({
                                'type': 'out_invoice',
                                'journal_id': journal_sale,
                                'partner_branch_id': rec.partner_branch_id.id,
                                'partner_id': rec.partner_branch_id.partner_id.id,
                                'commercial_partner_id': rec.partner_branch_id.partner_id.id,
                                'invoice_date': rec.invoice_date,
                                'date': rec.invoice_date,
                                'currency_id': self.env.company.currency_id.id,
                                'state': 'draft',
                                'company_id': rec.company_id.id,
                                'invoice_user_id':  self.env.uid,
                                'invoice_payment_state': 'not_paid',
                                'invoice_date_due': rec.invoice_date,
                                'invoice_partner_display_name': rec.partner_branch_id.name,
                                'purchase_transportation_id': False,
                                'branch_id': rec.branch_id.id,
                                'invoice_line_ids': inv_line_ids,
                                'generate_sale_id': rec.id,
                            })



                            for t in rec.lines:
                                if t.selected:
                                    
                                    transp_id = self.env['trnsp.transportation.mst'].search(
                                        [('id', '=', t.transportation_id.id)
                                        ])
                                    if transp_id:
                                        transp_id.write({'sale_invoice_flag': True})

                                        transp_id.write({'sale_invoice_id': invoice.id})
                                        if transp_id.purchase_invoice_id.state == 'posted' and transp_id.sale_invoice_id.state == 'posted':
                                            transp_id.write({'state': 'posted'})


                            rec.write({'state': 'posted'})

                            action = self.env.ref('account.action_move_out_invoice_type')
                            result = action.read()[0]
                            result.pop('id', None)
                            result['context'] = {}
                            result['domain'] = [('generate_sale_id', '=', rec.id)]

                            # if invoice:
                            #     res = self.env.ref('account.view_move_form', False)
                            #     result['views'] = [(res and res.id or False, 'form')]
                            #     result['res_id'] = invoice.id or False

                            return result
                        else:

                            
                            if move1:
                                move1.write({
                                    'type': 'out_invoice',
                                    'journal_id': journal_sale,
                                    'partner_branch_id': rec.partner_branch_id.id,
                                    'partner_id': rec.partner_branch_id.partner_id.id,
                                    'commercial_partner_id': rec.partner_branch_id.partner_id.id,
                                    'invoice_date': rec.invoice_date,
                                    'date': rec.invoice_date,
                                    'currency_id': self.env.company.currency_id.id,
                                    'state': 'draft',
                                    'company_id': rec.company_id.id,
                                    'invoice_user_id':  self.env.uid,
                                    'invoice_payment_state': 'not_paid',
                                    'invoice_date_due': rec.invoice_date,
                                    'invoice_partner_display_name': rec.partner_branch_id.name,
                                    'purchase_transportation_id': False,
                                    'branch_id': rec.branch_id.id,
                                    'invoice_line_ids': inv_line_ids,
                                    'generate_sale_id': rec.id,
                                })



                                for t in rec.lines:
                                    if t.selected:
                                        
                                        transp_id = self.env['trnsp.transportation.mst'].search(
                                            [('id', '=', t.transportation_id.id)
                                            ])
                                        if transp_id:
                                            transp_id.write({'sale_invoice_flag': True})

                                            transp_id.write({'sale_invoice_id': move1.id})
                                            if transp_id.purchase_invoice_id.state == 'posted' and transp_id.sale_invoice_id.state == 'posted':
                                                transp_id.write({'state': 'posted'})


                                rec.write({'state': 'posted'})

                                action = self.env.ref('account.action_move_out_invoice_type')
                                result = action.read()[0]
                                result.pop('id', None)
                                result['context'] = {}
                                result['domain'] = [('generate_sale_id', '=', rec.id)]

                                # if invoice:
                                #     res = self.env.ref('account.view_move_form', False)
                                #     result['views'] = [(res and res.id or False, 'form')]
                                #     result['res_id'] = invoice.id or False

                                return result
                elif  rec.posted_options == 'detail':
                    inv_line_ids = []
                    for line in rec.lines:
                        inv_line_ids = []

                        if line.selected:
                            transp_invoice_id = self.env['account.move.line'].search([('sale_transportation_id', '=', line.transportation_id.id)])
                            if transp_invoice_id:
                                line.transportation_id.write({'sale_invoice_flag': True})

                                line.transportation_id.write({'sale_invoice_id':transp_invoice_id.move_id.id})
                               
                              
                                # raise ValidationError(
                                #     "تنبيه .. بوليصة الشحن رقم (%s) مرتبطة مسبقا بفاتورة مبيعات رقم (%s) .." % (line.invoice_manual,transp_invoice_id.move_id.name))
                            else:
                                if not line.transp_charge_type.product_id:
                                    raise ValidationError(
                                        "تنبيه .. يجب تحديد الصنف الخدمي المقابل لنوع الشحن من شاشة انواع الشحن ..")
                                transport_line_ids = {
                                    'product_id': line.transp_charge_type.product_id.id,
                                    'name': line.transp_path_from.name + " - " + line.transp_path_to.name,
                                    'quantity': 1,
                                    'product_uom_id': line.transp_charge_type.product_id.uom_id.id,
                                    'discount': False,
                                    'price_unit': line.customer_price + (line.customer_stop * line.stopped_days),
                                    'tax_ids': [(6, 0, line.transp_charge_type.product_id.taxes_id.ids)],
                                    'analytic_account_id': line.analytic_account_id.id,
                                    # 'tax_id': product_mislead_id.taxes_id.id,
                                    'company_id': rec.company_id.id,
                                    'company_currency_id': rec.env.company.currency_id.id,
                                    'sale_transportation_id': line.transportation_id.id,
                                    'note_transportation': str(line.notes if line.notes else ' '),
                                    'invoice_manual': line.invoice_manual if line.invoice_manual else ' ',
                                    'customer_price': line.transportation_id.customer_price,
                                    'customer_stop': line.transportation_id.customer_stop,
                                    'supplier_price': line.transportation_id.supplier_price,
                                    'supplier_stop': line.transportation_id.supplier_stop,
                                    'stopped_days': line.transportation_id.stopped_days,

                                }

                                inv_line_ids.append((0, 0, transport_line_ids))
                                if line.booking_fees:
                                    transport_line_ids = {
                                    'product_id': line.transp_charge_type.product_id.id,
                                    'name': line.transp_path_from.name + " - " + line.transp_path_to.name + "( رسوم حجز موعد )",
                                    'quantity': 1,
                                    'product_uom_id': line.transp_charge_type.product_id.uom_id.id,
                                    'discount': False,
                                    'price_unit': line.booking_fees,
                                    'tax_ids': [(6, 0, line.transp_charge_type.product_id.taxes_id.ids)],
                                    'analytic_account_id': line.analytic_account_id.id,
                                    # 'tax_id': product_mislead_id.taxes_id.id,
                                    'company_id': rec.company_id.id,
                                    'company_currency_id': rec.env.company.currency_id.id,
                                    'sale_transportation_id': line.transportation_id.id,
                                    'invoice_manual': line.invoice_manual if line.invoice_manual else ' ',
                                    }

                                    inv_line_ids.append((0, 0, transport_line_ids))
                                
                                if line.storage_fees:
                                    transport_line_ids = {
                                    'product_id': line.transp_charge_type.product_id.id,
                                    'name': line.transp_path_from.name + " - " + line.transp_path_to.name + "( رسوم ساحة- تخزين)",
                                    'quantity': 1,
                                    'product_uom_id': line.transp_charge_type.product_id.uom_id.id,
                                    'discount': False,
                                    'price_unit': line.storage_fees,
                                    'tax_ids': [(6, 0, line.transp_charge_type.product_id.taxes_id.ids)],
                                    'analytic_account_id': line.analytic_account_id.id,
                                    # 'tax_id': product_mislead_id.taxes_id.id,
                                    'company_id': rec.company_id.id,
                                    'company_currency_id': rec.env.company.currency_id.id,
                                    'sale_transportation_id': line.transportation_id.id,
                                    'invoice_manual': line.invoice_manual if line.invoice_manual else ' ',
                                    }

                                    inv_line_ids.append((0, 0, transport_line_ids))



                                if inv_line_ids:
                                    journal_id = self.env['account.journal'].search(
                                        [('branch_id', '=', self.env.user.branch_id.id), ('type', '=', 'sale')], limit=1)
                                    journal_sale = ""
                                    if journal_id:
                                        journal_sale = journal_id.id
                                    else:
                                        journal_id = self.env['account.journal'].search(
                                            [('type', '=', 'sale')], limit=1)

                                        journal_sale = journal_id.id
                                    move1 = self.env['account.move.line'].search([('sale_transportation_id', '=', line.transportation_id.id)])

                                    if not move1:
                                        invoice = self.env['account.move'].create({
                                            'type': 'out_invoice',
                                            'journal_id': journal_sale,
                                            'partner_branch_id': rec.partner_branch_id.id,
                                            'partner_id': rec.partner_branch_id.partner_id.id,
                                            'commercial_partner_id': rec.partner_branch_id.partner_id.id,
                                            'invoice_date': rec.invoice_date,
                                            'date': rec.invoice_date,
                                            'currency_id': self.env.company.currency_id.id,
                                            'state': 'draft',
                                            'company_id': rec.company_id.id,
                                            'invoice_user_id':  self.env.uid,
                                            'invoice_payment_state': 'not_paid',
                                            'invoice_date_due': rec.invoice_date,
                                            'invoice_partner_display_name': rec.partner_branch_id.name,
                                            'purchase_transportation_id': False,
                                            'branch_id': rec.branch_id.id,
                                            'invoice_line_ids': inv_line_ids,
                                            'generate_sale_id': rec.id,
                                        })



                                    
                                    
                                        line.transportation_id.write({'sale_invoice_flag': True})

                                        line.transportation_id.write({'sale_invoice_id': invoice.id})
                                        if line.transportation_id.purchase_invoice_id.state == 'posted' and line.transportation_id.sale_invoice_id.state == 'posted':
                                            line.transportation_id.write({'state': 'posted'})

                                        
                                        rec.write({'state': 'posted'})

                                    
                                
                                    elif move1:
                                            move1.write({
                                                'type': 'out_invoice',
                                                'journal_id': journal_sale,
                                                'partner_branch_id': rec.partner_branch_id.id,
                                                'partner_id': rec.partner_branch_id.partner_id.id,
                                                'commercial_partner_id': rec.partner_branch_id.partner_id.id,
                                                'invoice_date': rec.invoice_date,
                                                'date': rec.invoice_date,
                                                'currency_id': self.env.company.currency_id.id,
                                                'state': 'draft',
                                                'company_id': rec.company_id.id,
                                                'invoice_user_id':  self.env.uid,
                                                'invoice_payment_state': 'not_paid',
                                                'invoice_date_due': rec.invoice_date,
                                                'invoice_partner_display_name': rec.partner_branch_id.name,
                                                'purchase_transportation_id': False,
                                                'branch_id': rec.branch_id.id,
                                                'invoice_line_ids': inv_line_ids,
                                                'generate_sale_id': rec.id,
                                            })



                                            
                                            line.transportation_id.write({'sale_invoice_flag': True})

                                            line.transportation_id.write({'sale_invoice_id': move1.id})
                                            if line.transportation_id.purchase_invoice_id.state == 'posted' and line.transportation_id.sale_invoice_id.state == 'posted':
                                                line.transportation_id.write({'state': 'posted'})

                                           
                                            rec.write({'state': 'posted'})

                    action = self.env.ref('account.action_move_out_invoice_type')
                    result = action.read()[0]
                    result.pop('id', None)
                    result['context'] = {}
                    result['domain'] = [('generate_sale_id', '=', rec.id)]

                    
                    return result






class xx_generate_sale_line(models.Model):
    _inherit = 'transp.generate.sale.invoice.line'

    booking_fees = fields.Float(string="رسوم حجز موعد")
    
    storage_fees = fields.Float(string="رسوم ساحة(تخزين)")
 
 