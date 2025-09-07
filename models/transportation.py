# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class transportation(models.Model):
    _inherit = 'trnsp.transportation.mst'

    
    driver_btrip_selection = fields.Selection(
        [('percentage', 'نسبة'), ('amount', 'مبلغ')], string='Status',
         copy=False, index=True, tracking=3, default='percentage',required=True)
         
    driver_btrip_amount = fields.Float(string="عمولة السائق")

    booking_fees = fields.Float(string="رسوم حجز موعد")
    
    storage_fees = fields.Float(string="رسوم ساحة(تخزين)")
 
    
    @api.onchange('driver_btrip_selection')
    def reset_value_btrip(self):
        for rec in self:
            rec.driver_btrip_amount = 0
            rec.company_driver_perc = 0