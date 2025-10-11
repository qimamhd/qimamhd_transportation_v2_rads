from datetime import datetime, time
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class mntns_commission_report(models.TransientModel):
    _inherit = 'mntns.commission.report.module'

 
    def get_report_excel(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'partner_id': [(i['id']) for i in self.partner_id],
                'company_ids1': [(i['id']) for i in self.company_ids1],
                'branch_id': [(i['id']) for i in self.branch_id],
                'sale_man_id': [(i['id']) for i in self.sale_man_id],
                'service_type_id': [(i['id']) for i in self.service_type_id],
                'posted_invoices': self.posted_invoices,
                'report_type': self.report_type,


            },
        }

       
        return self.env.ref('qimamhd_car_checkup_13.mntns_commission_report_xlsx').report_action(self, data=data)

class ReportAttendanceRecap(models.AbstractModel):
    _name = 'report.qimamhd_car_checkup_13.mntns_commission_report_xlsx_view'
    _inherit = 'report.odoo_report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, partners):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        l_partner_id = data['form']['partner_id']
        l_company_ids1 = data['form']['company_ids1']
        l_branch_id = data['form']['branch_id']
        l_sale_man_id = data['form']['sale_man_id']
        l_service_type_id = data['form']['service_type_id']
      

        
        l_posted_invoices = data['form']['posted_invoices']
        l_report_type = data['form']['report_type']
     
        domain_compelete = []
       

        domain_compelete = [('date', '>=', date_start), ('date', '<=', date_end), ('type', 'in', ['out_invoice','out_refund'])]
      
        domain_compelete.append(('checkup_order_id', '!=', False))
  

        if l_company_ids1:
            domain_compelete.append(('company_id', 'in', l_company_ids1))
           

        if l_branch_id:
            domain_compelete.append(('branch_id', 'in', l_branch_id))
         

        if l_partner_id:
            domain_compelete.append(('partner_id', 'in', l_partner_id))
             
 
        if l_posted_invoices:
            domain_compelete.append(('state', '=', 'posted'))
        else:
            domain_compelete.append(('state', 'in', ['posted','draft']))

        if l_sale_man_id:
            domain_compelete.append(('checkup_order_id.sale_man_id', 'in', l_sale_man_id))
        
        if l_service_type_id:
            domain_compelete.append(('checkup_order_id.service_type_id', 'in', l_service_type_id))
        
        docs_compelete = self.env['account.move'].search(domain_compelete)
         
        if docs_compelete:
            l_companys = self.env['res.company'].search([('id', 'in', l_company_ids1)])
            l_branchs = self.env['custom.branches'].search([('id', 'in', l_branch_id)])
            l_partner = self.env['res.partner'].search([('id', 'in', docs_compelete.partner_id.ids)])
            l_services = self.env['mntns.services.types'].search([('id', 'in', docs_compelete.checkup_order_id.service_type_id.ids)])
            l_sale_mans = self.env['mntns.sales.man'].search([('id', 'in',docs_compelete.checkup_order_id.sale_man_id.ids)])
 
       

            for account in l_companys:
                
                sheet = workbook.add_worksheet('تقرير عمولات المندوبين')
                sheet.right_to_left()
                format_company = workbook.add_format(
                    {'bold': True, 'align': 'center', 'font': 'Arial', 'font_size': 20})

                format_header = workbook.add_format(
                    {'bold': True, 'align': 'center', 'font': 'Arial', 'font_size': 14})
                format_header.set_bg_color('gray')

                format_address = workbook.add_format(
                    {'bold': True, 'align': 'center', 'bg_color': 'yellow', 'font': 'Arial', 'font_size': 12})
                format_totally_row = workbook.add_format(
                    {'bold': True, 'align': 'center', "num_format": u"#,##0.00", 'font': 'Arial', 'font_size': 10})
                format_date = workbook.add_format(
                    {'num_format': 'dd-mm-yyyy', 'align': 'center', 'font': 'Arial', 'font_size': 10})
                format_num = workbook.add_format(
                    {"num_format": u"#,##0.00", 'align': 'center', 'font': 'Arial', 'font_size': 10})
                format_string = workbook.add_format(
                    {'align': 'center', 'font': 'Arial', 'font_size': 10})

                company_col = 1
                company_row = 1
                sheet.merge_range(company_row, company_col, company_row, company_col + 2, 'الاسم', format_company)
                sheet.merge_range(company_row + 1, company_col, company_row + 1, company_col + 2, 'العنوان',
                                    format_company)
                sheet.merge_range(company_row + 2, company_col, company_row + 2, company_col + 2, 'الجوال',
                                    format_company)
                sheet.merge_range(company_row + 3, company_col, company_row + 3, company_col + 2, 'رقم الضريبي',
                                    format_company)
                sheet.merge_range(company_row + 4, company_col, company_row + 4, company_col + 2, 'سجل المؤسسة',
                                    format_company)

                sheet.merge_range(company_row, company_col + 3, company_row, company_col + 4, account.name,
                                    format_company)
                sheet.merge_range(company_row + 1, company_col + 3, company_row + 1, company_col + 4,
                                    account.street, format_company)
                sheet.merge_range(company_row + 2, company_col + 3, company_row + 2, company_col + 4, account.phone,
                                    format_company)
                sheet.merge_range(company_row + 3, company_col + 3, company_row + 3, company_col + 4, account.vat,
                                    format_company)
                sheet.merge_range(company_row + 4, company_col + 3, company_row + 4, company_col + 4,
                                    account.company_registry, format_company)

                header_col = 1
                header_row = 8
             
                if l_report_type == 'detail':
                    sheet.merge_range(header_row, header_col, header_row, header_col + 3,
                                            'تقرير عمولات المندوبين تحليلي',
                                            format_header)

                else:
                    sheet.merge_range(header_row, header_col, header_row, header_col + 3,
                                            'تقرير عمولات المندوبين إجمالي',
                                            format_header)
                date_row = 10
                date_col = 1

                sheet.merge_range(date_row , date_col, date_row, date_col + 1,
                            date_start + ' من تاريخ ',
                                format_header)
                date_col +=1
                sheet.merge_range(date_row , date_col+1, date_row, date_col + 2,
                                    date_end + ' الى تاريخ ',
                                    format_header)
                address_col = 1
                address_row = 12

                sheet.set_column('C:C', 30)
                sheet.set_column('D:D', 20)
                sheet.set_column('E:E', 20)
                sheet.set_column('F:F', 20)
                sheet.set_column('G:G', 20)
                sheet.set_column('H:H', 20)
                sheet.set_column('I:I', 20)
                sheet.set_column('J:J', 20)
                sheet.set_column('K:K', 20)
                sheet.set_column('L:L', 20)

                if l_report_type == 'summary':
                    sheet.write(address_row, address_col, '#', format_address)
                    sheet.write(address_row, address_col + 1, 'المندوب', format_address)
                    sheet.write(address_row, address_col + 2, 'المبيعات قبل الضريبة', format_address)
                    sheet.write(address_row, address_col + 3, 'اجمالي الضريبة', format_address)
                    sheet.write(address_row, address_col + 4, 'المبيعات شامل الضريبة', format_address)
                    sheet.write(address_row, address_col + 5, 'اجمالي العمولة', format_address)
                  
                    l_amount_total_all = 0
                    l_amount_tax_all = 0
                    l_amount_untaxed_all = 0
                    l_commission_amount_all = 0

                    address_row += 1
                    l_cnt = 0
                    for rec in l_sale_mans:
                        l_amount_total = sum(l.amount_total if l.type == 'out_invoice' else l.amount_total * -1 for l in docs_compelete.filtered(lambda x: x.checkup_order_id.sale_man_id.id == rec.id))
                        l_amount_tax = sum(l.amount_tax if l.type == 'out_invoice' else l.amount_tax *-1 for l in docs_compelete.filtered(lambda x: x.checkup_order_id.sale_man_id.id == rec.id))
                        l_amount_untaxed = sum(l.amount_untaxed if l.type == 'out_invoice' else l.amount_untaxed * -1 for l in docs_compelete.filtered(lambda x: x.checkup_order_id.sale_man_id.id == rec.id))
                        l_commission_amount = sum(l.checkup_order_id.commission_amount if l.type == 'out_invoice' else l.checkup_order_id.commission_amount * -1 for l in docs_compelete.filtered(lambda x: x.checkup_order_id.sale_man_id.id == rec.id))
                       
                        l_amount_total_all += l_amount_total
                        l_amount_tax_all += l_amount_tax
                        l_amount_untaxed_all += l_amount_untaxed
                        l_commission_amount_all += l_commission_amount


                        address_row += 1
                        l_cnt +=1
                        # sheet.write_datetime(address_row, address_col, rec.date,format_date)
                        sheet.write(address_row, address_col, l_cnt,format_string)
                        
                        sheet.write(address_row, address_col + 1,rec.name, format_string)
                        
                        sheet.write(address_row, address_col + 2, l_amount_untaxed , format_num)
                        sheet.write(address_row, address_col + 3, l_amount_tax,format_num)
                        sheet.write(address_row, address_col + 4, l_amount_total,format_num)
                        sheet.write(address_row, address_col + 5, round(l_commission_amount,2) , format_num)
                        
                        

                    address_row += 2
                    sheet.merge_range(address_row , address_col, address_row, address_col +1, "الاجماليات",  format_totally_row)
                    sheet.write(address_row, address_col + 2, l_amount_untaxed_all, format_totally_row)
                    sheet.write(address_row, address_col + 3, l_amount_tax_all, format_totally_row)
                    sheet.write(address_row, address_col + 4, round(l_amount_total_all,2), format_totally_row)
                    sheet.write(address_row, address_col + 5, round(l_commission_amount_all,2) , format_totally_row)
                    
                        

                else:
                    l_amount_total_all = 0
                    l_commisiion_total_all = 0
                  
                    address_row += 1
                  
                    for rec in l_sale_mans:
                        l_amount_total = 0
                        l_commission_total =0
                        l_cnt = 0
 
                        address_row += 1
                        sheet.merge_range(address_row, header_col, address_row, header_col +12, rec.name,format_header)
                        address_row += 1
                        sheet.write(address_row, address_col, '#', format_address)
                        sheet.write(address_row, address_col + 1, 'رقم الطلب', format_address)
                        sheet.write(address_row, address_col + 2, 'تاريخ الطلب', format_address)
                        sheet.write(address_row, address_col + 3, 'رقم الفاتورة', format_address)
                        sheet.write(address_row, address_col + 4, 'الاجمالي شامل الضريبة', format_address)
                        sheet.write(address_row, address_col + 5, 'نسبة العمولة', format_address)
                        
                        sheet.write(address_row, address_col + 6, 'مبلغ العمولة', format_address)
                        sheet.write(address_row, address_col + 7, 'نوع السيارة', format_address)
                        sheet.write(address_row, address_col + 8, 'لوحة السيارة', format_address)
                        sheet.write(address_row, address_col + 9, 'العميل', format_address)
                        # sheet.write(address_row, address_col + 10, 'الحالة', format_address)
                        sheet.write(address_row, address_col + 10, 'نوع الخدمة', format_address)
                        sheet.write(address_row, address_col + 11, 'الفرع', format_address)
                        address_row += 1
                        l_cnt = 0
                       
                        l_cust_amount_total = 0
                        l_supplier_amount_total = 0
                        for line in docs_compelete.filtered(lambda x: x.checkup_order_id.sale_man_id.id ==rec.id):
                            l_cnt +=1
                            invoice_amount =0
                            comm_amount =0

                            if line.type == 'out_invoice':

                                invoice_amount = line.amount_total
                                comm_amount = line.checkup_order_id.commission_amount

                                l_amount_total = invoice_amount + l_amount_total
                                l_commission_total = comm_amount + l_commission_total

                                l_amount_total_all = invoice_amount + l_amount_total_all
                                l_commisiion_total_all = comm_amount + l_commisiion_total_all
                            if line.type == 'out_refund':
                                
                                invoice_amount = line.amount_total * -1
                                comm_amount = line.checkup_order_id.commission_amount *-1

                                l_amount_total = invoice_amount + l_amount_total
                                l_commission_total = comm_amount + l_commission_total

                                l_amount_total_all = invoice_amount + l_amount_total_all
                                l_commisiion_total_all = comm_amount + l_commisiion_total_all



                            address_row += 1

                            sheet.write(address_row, address_col, l_cnt,format_string)
                            sheet.write(address_row, address_col+ 1, line.checkup_order_id.seq,)
                            sheet.write_datetime(address_row, address_col + 2,line.date,format_date)
                            sheet.write(address_row, address_col + 3, line.name , format_string)
                            sheet.write(address_row, address_col + 4,round(invoice_amount,2),format_num)
                            sheet.write(address_row, address_col + 5,line.checkup_order_id.commission , format_num)
                            sheet.write(address_row, address_col + 6,comm_amount, format_num)
                        
                            sheet.write(address_row, address_col + 7,line.checkup_order_id.car_type_id.name, format_string)
                            sheet.write(address_row, address_col + 8,line.checkup_order_id.car_panel_no, format_string)
                            sheet.write(address_row, address_col + 9, line.partner_id.name , format_string)
                            # sheet.write(address_row, address_col + 10, line.state , format_string)
                            
                            sheet.write(address_row, address_col + 10, line.checkup_order_id.service_type_id.name, format_string)
                            sheet.write(address_row, address_col + 11, line.branch_id.name , format_string)

                        address_row += 1
                        sheet.merge_range(address_row , address_col, address_row, address_col + 3,
                            "الاجمالي",
                                format_totally_row)
                    
                        sheet.write(address_row, address_col + 4, l_amount_total, format_totally_row)
                        sheet.write(address_row, address_col + 5, '', format_totally_row)
                
                        sheet.write(address_row, address_col + 6, l_commission_total, format_totally_row)
                        
                        
                    address_row += 2
                    sheet.merge_range(address_row , address_col, address_row, address_col + 3,  "الاجمالي العام", format_totally_row)
                   
                    sheet.write(address_row, address_col + 4, l_amount_total_all, format_totally_row)
                    sheet.write(address_row, address_col + 4, '', format_totally_row)
            
                    sheet.write(address_row, address_col + 6, l_commisiion_total_all, format_totally_row)
                   
        
        else:
            raise ValidationError(
                "لا توجد بيانات")
