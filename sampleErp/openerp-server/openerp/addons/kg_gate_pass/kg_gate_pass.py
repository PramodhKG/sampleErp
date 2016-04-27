import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import netsvc

class kg_gate_pass(osv.osv):

	_name = "kg.gate.pass"
	_description = "KG Gate Pass"
	
	_columns = {
		'name': fields.char('Gate Pass No', size=128, readonly=True),
		'dep_id': fields.many2one('kg.depmaster','Department Name', select=True),
		'date': fields.date('Gate Pass Date', readonly="1"),
		'return_date': fields.date('Expected Return Date'),
		'partner_id': fields.many2one('res.partner', 'Supplier'),
		'gate_line': fields.one2many('kg.gate.pass.line', 'gate_id', 'Gate Pass Line'),
		'out_type': fields.many2one('kg.outwardmaster', 'OutwardType'),
		'origin': fields.many2one('kg.service.indent', 'Origin', readonly=True),
		'user_id': fields.many2one('res.users', 'User'),
		'note': fields.text('Remarks')
				
	}
	
	_defaults = {
	
		'date' : fields.date.context_today,
		'name': '/',
		'user_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
		
	}
	
	def create(self, cr, uid, vals, context=None):		
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'kg.gate.pass') or '/'
		order =  super(kg_gate_pass, self).create(cr, uid, vals, context=context)
		return order
		
	def gate_pass_print(self, cr, uid, ids, context=None):
				
		#assert len(ids) == 1, 'This option should only be used for a single id at a time'
		wf_service = netsvc.LocalService("workflow")
		wf_service.trg_validate(uid, 'kg.gate.pass', ids[0], 'send_rfq', cr)
		datas = {
				 'model': 'kg.gate.pass',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}
		return {'type': 'ir.actions.report.xml', 'report_name': 'gate.pass.report', 'datas': datas, 'nodestroy': True}
	
	
kg_gate_pass()

class kg_gate_pass_line(osv.osv):
	
	_name = "kg.gate.pass.line"
	_description = "Gate Pass Line"
	
	
	_columns = {

	'gate_id': fields.many2one('kg.gate.pass', 'Gate Pass', ondelete='cascade'),
	'product_id': fields.many2one('product.product', 'Item Name'),
	'uom': fields.many2one('product.uom', 'UOM'),
	'qty': fields.float('Quantity'),
	'note': fields.text('Remarks')
		
	}
	
	def onchange_uom(self, cr, uid, ids,product_id):
		if product_id:
			pro_rec = self.pool.get('product.product').browse(cr, uid,product_id)
			uom = pro_rec.uom_po_id.id
			return {'value': {'uom': uom}}
		else:
			return {'value': {'uom': False}}
	
kg_gate_pass_line()
