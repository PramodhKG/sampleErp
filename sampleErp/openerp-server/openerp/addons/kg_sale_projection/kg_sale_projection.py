import time
from lxml import etree
import openerp.addons.decimal_precision as dp
import openerp.exceptions

from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from datetime import date
from itertools import groupby
import collections
from datetime import datetime, timedelta

class kg_sale_projection(osv.osv):
	
	_name = 'kg.sale.projection'
	_description = 'Sale Projection'
	
	_columns = {

		'name': fields.char('Projection No',readonly=True),
		
		'created_by': fields.many2one('res.users','Created By',readonly=True),
		
		'date': fields.datetime('Creation Date',readonly=True),
		'state': fields.selection([('draft','Draft'),('confirm','Waiting for Approval'),('approve','Approved')],'Status',readonly=True),
		'line_ids': fields.one2many('kg.sale.projection.line','entry_id','Sale Projection Line',readonly=True, states={'draft':[('readonly',False)]}),
		'remarks':fields.text('Remarks'),	
	}

	

	_defaults = {
	
		'date': lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'state': 'draft',
		
		'created_by': lambda obj, cr, uid, context: uid,
		}
		
	def create(self, cr, uid, vals,context=None):
		print "vals..............................",vals	
		if vals.get('name',False)==False:
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'kg.sale.projection') or False
		sale =  super(kg_sale_projection, self).create(cr, uid, vals, context=context)
		return sale	
		
	def entry_confirm(self, cr, uid, ids, context=None):
		sale = self.browse(cr, uid, ids[0])
		product_obj = self.pool.get('product.product')
		bom_obj = self.pool.get('mrp.bom')
		print "line_ids.........................",sale.line_ids
		product_name = []
		product_ids = []
		for line in sale.line_ids:
			product_name.append(line.product_id.name)
			product_ids.append(line.product_id.id)
			
			print "product_name......................",product_name
			print "product_ids......................",product_ids
			dup_ids = [x for x, y in collections.Counter(product_name).items() if y > 1]
			if dup_ids:
				raise osv.except_osv(
						_('Duplicate Error'),
						_('You can not create projection for same item %s'%(dup_ids[0])))
						
			today = date.today()
			print "today................", type(today), today		
			delivery_date = datetime.strptime(line.delivery_date,'%Y-%m-%d').date()
			print "rec.delivery_date...........", type(delivery_date), delivery_date
			if delivery_date < today:
				raise osv.except_osv(
						_('Duplicate Error'),
						_('Delivery date should not less than current date '))
						
			if line.quantity <= 0:
				raise osv.except_osv(
						_('Duplicate Error'),
						_('You can not save Projection with 0 qty'))

			for pro_id in product_ids:
				bom_id = bom_obj.search(cr, uid, [('product_id','=',pro_id),('state','!=','expiry'),('state','=','approve')])
				product_rec = product_obj.browse(cr, uid, pro_id)
				if not bom_id:
					raise osv.except_osv(
						_('Duplicate Error'),
						_('There is no BoM for item %s'%(product_rec.name_template)))
						
			else:
				self.write(cr, uid, ids, {'state': 'confirm'})
				
					
		   
		return True	
	

	def entry_approve(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'approve'})
		bom_obj = self.pool.get('mrp.bom')
		bom_line_obj = self.pool.get('mrp.bom.line')
		indent_obj = self.pool.get('kg.depindent')
		indent_line_obj = self.pool.get('kg.depindent.line')
		sale_rec = self .browse(cr, uid, ids[0])
	
		product_ids = []
		for line in sale_rec.line_ids:
			print "lines............................",line.id
			sale_product_id = line.product_id.id
			print "sale_product_id............................",sale_product_id
			product_ids.append(sale_product_id)
			sale_pro_ids = tuple(product_ids)
			print "sale_pro_ids............................",sale_pro_ids
			bom_id = bom_obj.search(cr, uid, [('product_id','in',sale_pro_ids),('state','!=','expiry'),('state','=','approve')])
			if bom_id:
				print "bom_id....................................",bom_id
				bom_ids = tuple(bom_id)
				print "bom_ids.....................",bom_ids
				if len(bom_id) > 1:
					sql = """ select department_id from mrp_bom_line where bom_id in %s group by department_id """%(str(bom_ids))
				else:
					sql = """ select department_id from mrp_bom_line where bom_id = %s group by department_id """%(bom_id[0])
				
				cr.execute(sql)
				dep_data = cr.dictfetchall()
				print "dep_data........................",dep_data
				
				for dep_id in dep_data:
					print "dep_id...............",dep_id['department_id']
					bom_line_ids = bom_line_obj.search(cr, uid, [('bom_id','in',bom_ids),('department_id','=',dep_id['department_id'])]) 
					print "bom_line_ids.........................",bom_line_ids
					dep_id = dep_id['department_id']
					dep_rec = self.pool.get('kg.depmaster').browse(cr, uid, dep_id)
					src_loc_id = dep_rec.main_location.id
					dest_loc_id = dep_rec.stock_location.id
					
					
					indent_obj.create(cr, uid, {
						'bom_line_dep_id':dep_id,
						'dep_name':dep_id,
						'type':'from_bom',
						'src_location_id':src_loc_id,
						'dest_location_id':dest_loc_id,
						'projection_id':sale_rec.id,
						
					   })
					   
					for bom_line in bom_line_ids:
						print "bom_line...............................",bom_line
						bom_line_rec = bom_line_obj.browse(cr, uid, bom_line)
						indent_id = indent_obj.search(cr, uid, [('projection_id','=',sale_rec.id),('dep_name','=',dep_id)])
						print "indent_id.............................",indent_id
						indent_qty = line.quantity * bom_line_rec.product_qty
						indent_line_obj.create(cr, uid, {
							
							'indent_id':indent_id[0],
							'product_id':bom_line_rec.product_id.id,
							'uom':bom_line_rec.product_uom.id,
							'po_uom':bom_line_rec.product_uom.id,
							'qty':indent_qty,
							'po_qty':indent_qty,
							'pending_qty':indent_qty,
							'issue_pending_qty':indent_qty,
							'dep_id':dep_id
						})
				
			return True		

	def unlink(self,cr,uid,ids,context=None):
		raise osv.except_osv(_('Warning!'),
				_('You can not delete any Entry !!'))
				
				
	def check_projection_line(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		if not entry.line_ids:
			return False
		else:
			return True
		
	_constraints = [
		
		(check_projection_line, 'Projection Line entry can not be empty !!',['Line Entry']),
				
		]

kg_sale_projection()


class kg_sale_projection_line(osv.osv):

	_name = 'kg.sale.projection.line'
	_description = 'sale Line'
	
	_columns = {

		'entry_id':fields.many2one('kg.sale.projection','Entry Line'),
		'category_id': fields.many2one('product.category','Product Category', required=True),
		'product_id':fields.many2one('product.product','Product Name', domain="[('sale_ok','=',True), '&', ('categ_id','=',category_id)]",required=True),
		
		'quantity': fields.float('Quantity', required=True),
		'uom_id': fields.many2one('product.uom','Unit of Measure', required=True),
		'delivery_date': fields.date('Delivery Date',required=True),
		
	}
	
	def onchange_product_id(self, cr, uid, ids, product_id, context=None):
		value = {'uom_id': ''}
		if product_id:
			prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
			value = {'uom_id': prod.uom_id.id}
		return {'value': value}
		 
	
	
	
	
kg_sale_projection_line()
