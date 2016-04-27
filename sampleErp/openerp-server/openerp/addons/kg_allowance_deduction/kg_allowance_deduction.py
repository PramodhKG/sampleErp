import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
import netsvc
import datetime
import calendar

class kg_allowance_deduction(osv.osv):

	_name = "kg.allowance.deduction"
	_description = "Monthly Allowance & Deduction Entry"
	_order = "month desc"
		
	_columns = {		
			
		'month': fields.date('Creation Date'),
		'start_date': fields.date('Month Start Date', required=True, readonly=False),
		'end_date': fields.date('Month End Date', required=True, readonly=False),
		'type': fields.selection([('ALW','Allowance'),('DED','Deduction')], 'Select Type', required=True,
				readonly=True, states={'draft':[('readonly',False)]}),
		'pay_type': fields.many2one('hr.salary.rule', 'Select Earning/ Deduction', 
				domain="[('category_id','=',type)]",required=True, readonly=True, states={'draft':[('readonly',False)]}),		
		'entry_line': fields.one2many('kg.allowance.deduction.line', 'entry_id', 'Entry Lines',
				readonly=True, states={'draft':[('readonly',False)]}),
		'state': fields.selection([('draft','Draft'),('confirm','Entry Confirmed'),('cancel','Cancel')], 'Status'),
		'active': fields.boolean('Active', readonly=True, states={'draft':[('readonly',False)]}),
		'payslip': fields.boolean('Payslip')
		
	}
	
	def _check_entry_line(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		if not entry.entry_line:
			return False
		else:
			for line in entry.entry_line:
				if line.amount == 0:
					return False
		return True
		
		
			
	def _check_duplicate_entry(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		obj = self.pool.get('kg.allowance.deduction')
		start_date = entry.start_date
		end_date = entry.end_date
		entry_type = entry.pay_type.id
		dup_ids = obj.search(cr, uid, [('start_date','=',start_date),('end_date','=',end_date),
									('pay_type','=',entry_type)])
		print "dup_ids =============>>>", dup_ids
		if len(dup_ids) > 1:
			return False
		return True		
		
	def _get_last_month_first(self, cr, uid, context=None):
		today = datetime.date.today()
		print "today-----------", today
		first = datetime.date(day=1, month=today.month, year=today.year)
		mon = today.month - 1
		if mon == 0:
			mon = 12
		else:
			mon = mon
		tot_days = calendar.monthrange(today.year,mon)[1]
		test = first - datetime.timedelta(days=tot_days)
		res = test.strftime('%Y-%m-%d')
		print "---------------",res
		return res
		
	def _get_last_month_end(self, cr, uid, context=None):
		today = datetime.date.today()
		first = datetime.date(day=1, month=today.month, year=today.year)
		last = first - datetime.timedelta(days=1)
		res = last.strftime('%Y-%m-%d')
		return res		
	
	_constraints = [
		
		(_check_entry_line, 'Entry line and amount can not be empty !!',['amount']),
		# (_check_ot_applicable, 'Entry ot !!',['amount']),
		(_check_duplicate_entry, 'System not allow to save duplicate entries. Check Month and Type !!',['amount']),
		
		]		
		
	_defaults = {
	
		'month' : fields.date.context_today,
		'start_date': _get_last_month_first,
		'end_date': _get_last_month_end,
		'state': 'draft',
		'active': True,

	}	
	
	def confirm_entry(self, cr, uid, ids,context=None):		
		self.write(cr,uid,ids,{'state':'confirm'})
		return True
		
	def cancel_entry(self, cr, uid, ids,context=None):
		record = self.browse(cr, uid, ids[0])		
		#if record.payslip == False:
		self.write(cr,uid,ids,{'state':'cancel'})
		"""else:
			raise osv.except_osv(_
				('Entry Used Already !'), 
				_('This entry has used already for salary process!!'))"""
		return True

	def draft_entry(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'draft'})
		return True
		
	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		entry = self.read(cr, uid, ids, ['state'], context=context)
		unlink_ids = []
		for t in entry:
			if t['state'] in ('draft','cancel'):
				unlink_ids.append(t['id'])
			else:
				raise osv.except_osv(_('Invalid action !'), _('System not allow to delete a Confirmed state Entry !!'))
		entry_lines_to_del = self.pool.get('kg.allowance.deduction.line').search(cr, uid, [('entry_id','in',unlink_ids)])
		self.pool.get('kg.allowance.deduction.line').unlink(cr, uid, entry_lines_to_del)
		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
		return True			
	
kg_allowance_deduction()


class kg_allowance_deduction_line(osv.osv):
	
	_name = "kg.allowance.deduction.line"
	_description = "Monthly Allowance & Deduction Entry Line"	
	
	_columns = {

	'entry_id': fields.many2one('kg.allowance.deduction', 'Entry No', required=True, ondelete='cascade'),
	'employee_id': fields.many2one('hr.employee', 'Employee Name', required=True),	
	'emp_name': fields.char('Employee Code', size=128, readonly=True),
	'amount': fields.float('Amount', required=True),
	
	}
	
	def _duplicate_entry(self, cr, uid, ids, context=None):
		obj = self.pool.get('kg.allowance.deduction.line')
		record = self.browse(cr, uid, ids[0])
		emp_id = record.employee_id.id
		dup_ids = obj.search(cr, uid,[('employee_id','=',emp_id)])
		print "dup_ids =======================>>>>", dup_ids
		if len(dup_ids) > 1:
			return False
		return True
	
	def onchange_employee_code(self, cr, uid, ids, employee_id,emp_name, context=None):
		value = {'emp_name': ''}
		if employee_id:
			emp = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
			value = {'emp_name': emp.emp_code}
		return {'value': value}
		
	def create(self, cr, uid, vals,context=None):
		if vals.has_key('employee_id') and vals['employee_id']:
			emp_rec = self.pool.get('hr.employee').browse(cr,uid,vals['employee_id'])
			if emp_rec:
				vals.update({'emp_name':emp_rec.emp_code})		
		order =  super(kg_allowance_deduction_line, self).create(cr, uid, vals, context=context)
		return order
		
	def write(self, cr, uid,ids, vals, context=None):
		if vals.has_key('employee_id') and vals['employee_id']:
			emp_rec = self.pool.get('hr.employee').browse(cr,uid,vals['employee_id'])
			if emp_rec:
				vals.update({'emp_name':emp_rec.name})						 
		res = super(kg_allowance_deduction_line, self).write(cr, uid, ids,vals, context)		
		return res
	
	_constraints = [
		
		(_duplicate_entry, 'System not allowed to enter employee name more than one time!!',['Duplication']),
		
		]
	
kg_allowance_deduction_line()	
