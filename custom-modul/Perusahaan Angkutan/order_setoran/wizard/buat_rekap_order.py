from odoo import api, fields, models
from datetime import datetime

class BuatRekapOrder(models.TransientModel):
    _name = 'buat.rekap.order'
    _description = 'Buat Rekap Order'