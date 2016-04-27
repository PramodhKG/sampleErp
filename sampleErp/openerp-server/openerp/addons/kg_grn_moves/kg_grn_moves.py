import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp

class kg_grn_moves(osv.osv):

	_name = "kg.grn.moves"
	_description = "GRN Moves"
	
	_columns = {
	
		'name': fields.char('GRN NO', size=64),
		'date':fields.date('Date'),
		'product_id':fields.many2one('product.product', 'Product'),
		'product_uom':fields.many2one('product.uom', 'UOM'),
		'product_qty':fields.float('Quantity'),
		'pending_qty':fields.float('Pending Qty'),
		'state': fields.selection([('done', 'Done'),('cancel','Cancel')], 'Status', track_visibility='onchange')
		
	}

	_defaults = {
		
		'date' : fields.date.context_today,
		
	}
	
		
		
	def done(self, cr, uid, ids,context=None):
		
		self.write(cr,uid,ids,{'state':'done'})
		return True
		
	def cancel(self, cr, uid, ids,context=None):
		
		self.write(cr,uid,ids,{'state':'cancel'})
		return True
			

kg_grn_moves()

