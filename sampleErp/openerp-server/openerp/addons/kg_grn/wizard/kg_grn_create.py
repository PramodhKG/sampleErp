from osv import fields, osv
import calendar
from datetime import date
from datetime import datetime
from datetime import timedelta
from tools.translate import _

from itertools import groupby
import time
import mx.DateTime as dt
from itertools import groupby
import logging
import netsvc

class grn_wo_wizard(osv.osv_memory):

    _name = "kg.purchase.order.wo.wizard"
    _description = "Stock Invoice Onshipping"

    _columns = {
    
    'po_id'
                
    }
    
    
grn_wo_wizard()
