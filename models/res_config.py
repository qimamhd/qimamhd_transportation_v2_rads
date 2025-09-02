from odoo import fields, models, _,api
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    preventing_credit_inv = fields.Boolean('منع البيع بالاجل')
 

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        l_preventing_credit_inv = params.get_param('preventing_credit_inv',
                                             default=False)
      

        res.update(preventing_credit_inv=l_preventing_credit_inv)
       
        return res

    def set_values(self):
          super(ResConfigSettings, self).set_values()
          self.env['ir.config_parameter'].sudo().set_param(
                "preventing_credit_inv",
                self.preventing_credit_inv)

          