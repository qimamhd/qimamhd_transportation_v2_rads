from datetime import datetime, time
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class transportaion_driver_report(models.TransientModel):
    _name = 'tranp.driver.report'


    date_start = fields.Date(required=True, default=fields.Date.today)
    date_end = fields.Date(required=True, default=fields.Date.today)
    partner_branch_id = fields.Many2many('res.partner.branches', string=" العميل", )
    report_type = fields.Selection([('detail', 'تفصيلي'),
                                     ('summary', 'إجمالي') 
                                     ], string='نوع التقرير', required=True,
                                    default='detail')
    posted_invoices = fields.Boolean(string="الفواتير المرحلة فقط", default=False)
    company_car_flag = fields.Boolean(string="سائقي الشركة فقط", default=True)
 
    company_ids1 = fields.Many2many(comodel_name="res.company", string="الشركة", required=True,
                                    default=lambda self: self.env.user.company_ids.ids)
    branch_id = fields.Many2many('custom.branches', string="الفرع", required=True, default=lambda self: self.env.user.allowed_branch_ids.ids)
    driver_id = fields.Many2many('hr.employee', string="السائق")

 
    @api.onchange('company_ids1')
    def _get_allowed_branch_ids(self):
        print(self.env.user.sudo().allowed_branch_ids)
        select = [(i['id']) for i in self.env.user.sudo().allowed_branch_ids]
        return {'domain': {'branch_id': [('id', 'in', select)]}}

    def get_report(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'partner_branch_id': [(i['id']) for i in self.partner_branch_id],
                'company_ids1': [(i['id']) for i in self.company_ids1],
                'branch_id': [(i['id']) for i in self.branch_id],
                'driver_id': [(i['id']) for i in self.driver_id],
                'posted_invoices': self.posted_invoices,
                'report_type': self.report_type,
                'company_car_flag': self.company_car_flag,


            },
        }

       
        return self.env.ref('qimamhd_transportation_v2_rads.transp_driver_report').report_action(self, data=data)

class ReportAttendanceRecap(models.AbstractModel):
    _name = 'report.qimamhd_transportation_v2_rads.transp_driver_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        l_partner_branch_id = data['form']['partner_branch_id']
        l_company_ids1 = data['form']['company_ids1']
        l_branch_id = data['form']['branch_id']
        l_driver_id = data['form']['driver_id']
        l_posted_invoices = data['form']['posted_invoices']
        l_report_type = data['form']['report_type']
        l_company_car_flag = data['form']['company_car_flag']
     
        domain_compelete = []
       

        domain_compelete = [('order_date', '>=', date_start), ('order_date', '<=', date_end)]
      
   

        if l_company_ids1:
            domain_compelete.append(('company_id', 'in', l_company_ids1))
           

        if l_branch_id:
            domain_compelete.append(('branch_id', 'in', l_branch_id))
         

        if l_partner_branch_id:
            domain_compelete.append(('partner_branch_id', 'in', l_partner_branch_id))
             
 
        if l_posted_invoices:
            domain_compelete.append(('sale_invoice_id', '!=',False))
            domain_compelete.append(('state', 'in', ['confirmed','posted','draft']))
        else:
            domain_compelete.append(('state', 'in', ['posted','draft','confirmed']))
        if l_company_car_flag:
            if l_driver_id:
                domain_compelete.append(('company_driver_id', 'in', l_driver_id))
              
        
        print(domain_compelete)
        request_compelete = self.env['trnsp.transportation.mst'].search(domain_compelete)
         
        if request_compelete:

            l_companys = self.env['res.company'].search([('id', 'in', l_company_ids1)])
            l_branchs = self.env['custom.branches'].search([('id', 'in', l_branch_id)])
            l_partner = self.env['res.partner.branches'].search([('id', 'in', request_compelete.partner_branch_id.ids)])
            l_company_car_driver = self.env['hr.employee'].search([('id', 'in',request_compelete.company_driver_id.ids)])
 
            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'date_start': date_start,
                'date_end': date_end,
                'companys': l_companys,
                'branchs': l_branchs,
                'customers': l_partner,
                'company_car_driver': l_company_car_driver,
                 'report_type': l_report_type,
                'docs_compelete': request_compelete,
            }
        else:
            raise ValidationError(
                "لا توجد بيانات")
