import time
from lxml import etree
import openerp.addons.decimal_precision as dp
import openerp.exceptions
from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class kg_ta_advance(osv.osv):
	
	_name = 'kg.ta.advance'
	_description = 'Employee TA Advance'
	
	_columns = {

		'name':fields.char('No',readonly=True),		
		'date':fields.date('Creation Date',readonly=True),		
		'state': fields.selection([('draft','Draft'),('confirm','Confirmed'),('expire','Expired')],'Status',readonly=True),
		'employee_id': fields.many2one('hr.employee', 'Employee Name',required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'ad_amt': fields.float('Advance Amount',required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'repay_amt': fields.float('Repaid Amount',readonly=True, states={'confirm':[('readonly',False)]}),
		'used_amt': fields.float('Used Amount',readonly=False, states={'draft':[('readonly',False)]}),
		'active': fields.boolean('Active'),
		'created_by': fields.many2one('res.users','Created By'),
		'remark': fields.text('Remarks',required=True,readonly=False, states={'draft':[('readonly',False)]}),
		
		
	}

	def _check_duplicate(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		dup_ids = self.search(cr,uid,[('employee_id','=',rec.employee_id.id),('state','=','confirm')])
		print "dup_ids.....................", dup_ids
		#if dup_ids:
			#return False
		if rec.ad_amt <= 0:
			return False
		return True


	_constraints = [        
              
        (_check_duplicate, '---- Error : Already a active advance entry available for this employee. Process that then create new one !!	OR Advance amount should not be Zero',['dup_ids']),
						
        
        ]	
		
		
	
	_defaults = {
	
		'date':fields.date.context_today,
		'state': 'draft',
		'name': '/',
		'active': True,
		
		}

	def create(self, cr, uid, vals,context=None):		
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'kg.ta.advance') or '/'
		order =  super(kg_ta_advance, self).create(cr, uid, vals, context=context)
		return order

	def entry_confirm(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'confirm','created_by': uid })
		return True

	def onchange_repayamt(self,cr,uid,ids,ad_amt,repay_amt,used_amt,context=None):
		value = {'used_amt': ''}
		if ad_amt > 0:			
			used_amt = ad_amt - repay_amt
		else:
			used_amt = 0			
		value = {'used_amt': used_amt}		
		return {'value': value}		

	def unlink(self,cr,uid,ids,context=None):
		raise osv.except_osv(_('Warning!'),
				_('You can not delete any Entry !!'))			
		
		
kg_ta_advance()

