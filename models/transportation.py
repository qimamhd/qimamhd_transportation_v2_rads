# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class transportation(models.Model):
    _inherit = 'trnsp.transportation.mst'

       
    booking_fees = fields.Float(string="رسوم حجز موعد")
    
    storage_fees = fields.Float(string="رسوم ساحة(تخزين)")
 
 