import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
import netsvc
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import calendar
today = datetime.now()

class kg_partners(osv.osv):
	
	_name = 'res.partner'	
	_inherit = 'res.partner'
	
	_columns = {
	
	'contact_person': fields.char('Contact Person', size=128),
	'sp_size': fields.char('Spindles Size', size=128),
	'sale_type': fields.char('Type Of Sale', size=128),
	'capacity': fields.char('Capacity Spindlage', size=128),
	'range': fields.char('Product Range/Selling', size=128),
	'agent': fields.char('Direct Agent', size=128),
	'trade': fields.char('Trader Consumer', size=128),
	'abc': fields.char('ABC', size=128),
	'vat': fields.char('VAT-TIN', size=128),
	'cst': fields.char('CST-TIN No', size=128),
	'gst': fields.char('CST/GST No', size=128),
	'ecc': fields.char('ECC No', size=128),
	'ecc_range': fields.char('Range', size=128),
	'division': fields.char('Division', size=128),
	'count_grade_id':fields.one2many('kg.count.grade', 'partner_id', 'Count Wise Seller List'),
	
	
	}	
	
kg_partners()


class kg_count_grade(osv.osv):
	
	_name = "kg.count.grade"
	_description = "KG Count Grade Mapping"
	
	_columns = {
		
		'partner_id': fields.many2one('res.partner', 'Account Owner',ondelete='cascade', select=True),		
		'product_id': fields.many2one('product.product', 'Count Name', required=True),
		'grade_id': fields.many2one('kg.grade','Grade Name', required=True),
		
		
	}		
	
kg_count_grade()


