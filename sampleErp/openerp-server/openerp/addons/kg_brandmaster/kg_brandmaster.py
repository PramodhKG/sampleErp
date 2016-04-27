import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time

import openerp.addons.decimal_precision as dp

class kgbrand_category(osv.osv):

	_name = "kgbrand.category"
	_description = "Brand Category"
	_columns = {
		'code': fields.char('Code', size=64, required=True, translate=True, select=True),
		'name': fields.char('Name', size=64, required=True, translate=True, select=True),
		'date': fields.date('Date'),
		'product_id': fields.many2many('product.product', 'product_brand', 'pro_brandid', 'brand_proid', 'Product'),
		'type': fields.selection([('normal','Normal'), ('misc','Miscellanous')], 'Brand Type'),
	}


	_defaults = {
		'type' : lambda *a : 'normal',
		'date' : fields.date.context_today,
	}
	
	_sql_constraints = [
	 
		('code_uniq', 'unique(code)', 'Brand code must be unique!'),
		('name_uniq', 'unique(name)', 'Brand name must be unique !'),
	]
	

kgbrand_category()
