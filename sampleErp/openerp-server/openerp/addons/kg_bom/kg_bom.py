from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
import netsvc
import time
import openerp.exceptions
import datetime
from datetime import date

class kg_bom(osv.osv):
	
	_name = 'mrp.bom'	
	_inherit = 'mrp.bom'
	
	_columns = {
		
		'state':fields.selection([('draft','Draft'),('approve','Approved'),('expiry','Expired'),('movedtoproduction','Moved to Production')],'Status',readonly=True),
		'mrp_bom_line':fields.one2many('mrp.bom.line','bom_id','BOM Line'),
		
		'expiry_date':fields.date('Expiry Date'),
		'remarks':fields.text('Remarks'),
		'creation_date':fields.datetime('Creation Date',readonly=True),
		'active':fields.boolean('Active'),
	
		
	}
	
	_defaults = {
	  
	  'active':'True',
	  'creation_date': lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
	  'state':'draft',
	  
	}

	def bom_confirm(self,cr,uid,ids,context=None):
		
		rec = self.browse(cr,uid,ids[0])
		bom_obj = self.pool.get('mrp.bom')
		bom_id = bom_obj.search(cr, uid, [('product_id','=',rec.product_id.id),('id','!=',rec.id)])
		if bom_id:
			bom_rec = bom_obj.browse(cr, uid, bom_id[0])
			print "bom_rec.....................",bom_rec
			today = datetime.date.today()
			print "bom_rec.....................",today
			bom_rec.write({'state':'expiry','expiry_date':today})
			
		rec.write({'state':'approve'})
		for line in rec.mrp_bom_line:
			line.write({'state':'approve'})
		return True
		
	

	
kg_bom()



class kg_bom_line(osv.osv):
	
	_name = 'mrp.bom.line'
	
	
	_columns = {
		
		
		'bom_id':fields.many2one('mrp.bom','BOM Entry'),
		'product_id': fields.many2one('product.product', 'Product', required=True, domain="[('purchase_ok','=',True)]"),
		'product_qty': fields.float('Product Quantity', required=True, digits_compute=dp.get_precision('Product Unit of Measure')),
		'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True, help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control"),
		'department_id':fields.many2one('kg.depmaster','Department Name',required=True),
		'state':fields.selection([('draft','Draft'),('approve','Approved')],'Status'),
		
		
	}
	
	
	_defaults = {
	
	'state':'draft',
	  
	}
	
	def onchange_uom_id(self, cr, uid, ids, product_id, context=None):
		
		value = {'product_uom': ''}
		if product_id:
			pro_rec = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
			value = {'product_uom': pro_rec.uom_id.id}
			
		return {'value': value}	

	
kg_bom_line()









