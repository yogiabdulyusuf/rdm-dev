from odoo import api, fields, models, tools


class RdmCustomerReport(models.Model):
    _name = "report.rdm.customer"
    _description = "RDM Report"
    _auto = False
    _order = 'date desc'

    date = fields.Datetime(string='Date', readonly=True)
    zone_id = fields.Many2one('rdm.customer.zone', string='Zone', readonly=True)
    gender_id = fields.Many2one('rdm.customer.gender', string='Gender', readonly=True)
    ethnic_id = fields.Many2one('rdm.customer.ethnic', string='Ethnic', readonly=True)
    city_id = fields.Many2one('rdm.city', string='City', readonly=True)
    total_amount = fields.Float(string='RDM Transaction', readonly=True)

    def _select(self):
        return """
            SELECT 
                MIN(rt.id) AS id, rcz.id AS zone_id, rcg.id AS gender_id, rce.id AS ethnic_id, rcty.id AS city_id, rt.trans_date AS date, SUM(rt.total_amount) AS total_amount
        """

    def _from(self):
        return """
            FROM rdm_trans AS rt 
                LEFT JOIN rdm_customer rc ON (rc.id=rt.customer_id)
                LEFT JOIN rdm_customer_zone rcz ON (rc.zone=rcz.id)
                LEFT JOIN rdm_customer_gender rcg ON (rc.gender=rcg.id)
                LEFT JOIN rdm_customer_ethnic rce ON (rc.ethnic=rc.id)
                LEFT JOIN rdm_city rcty ON (rc.city=rcty.id)
        """

    def _group_by(self):
        return """
            GROUP BY 
                rt.id, rcz.id, rcg.id, rce.id, rcty.id, rt.trans_date
        """

    def _having(self):
        return """
        """

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._group_by(),self._having())
        )