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

class kg_allocation_leave(osv.osv):

	_name = "kg.allocation.leave"
	_description = "Allocation Request"
		
	_columns = {
		 	
		'state': fields.selection([('draft', 'To Submit'), ('cancel', 'Cancelled'),('confirm', 'To Approve'), ('refuse', 'Refused'), ('validate1', 'Second Approval'), ('validate', 'Approved')],
			'Status', readonly=True, track_visibility='onchange',
			help='The status is set to \'To Submit\', when a holiday request is created.\
			\nThe status is \'To Approve\', when holiday request is confirmed by user.\
			\nThe status is \'Refused\', when holiday request is refused by manager.\
			\nThe status is \'Approved\', when holiday request is approved by manager.'),
		'start_date': fields.date('Valid From', required=True, readonly=False, states={ 'validate':[('readonly',True)]}),
		'end_date': fields.date('Valid To', required=True, readonly=False, states={ 'validate':[('readonly',True)]}),
		'employee_code': fields.char("Employee Code",states={ 'validate':[('readonly',True)]}),
		'employee_id': fields.many2one('hr.employee', "Employee Name", select=True,required=True, states={ 'validate':[('readonly',True)]},
				  domain="[('employee_status','=','confirm')]"),
		'department_id':fields.many2one('hr.department','Department', select=True,states={ 'validate':[('readonly',True)]}),
		'entry_line': fields.one2many('kg.allocation.leave.line', 'entry_id', 'Entry Lines',states={ 'validate':[('readonly',True)]}),
	}

	
	def onchange_employee(self, cr, uid, ids, employee_id):
		result = {'value': {'department_id': False}}
		if employee_id:
			employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
			result['value'] = {'employee_code': employee.emp_code,'department_id': employee.department_id.id}
		return result
		
		
	def _check_entry_line(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		if not entry.entry_line:
			return False
		else:
			for line in entry.entry_line:
				if line.alloc_leave == 0:
					return False
		return True
		
	def unlink(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state not in ['draft']:
				raise osv.except_osv(_('Warning!'),_('You cannot delete a Allocation which is in %s state.')%(rec.state))
		return super(kg_allocation_leave, self).unlink(cr, uid, ids, context)
		
	def write(self, cr, uid, ids, vals, context=None):
		for  holiday in self.browse(cr, uid, ids, context=context):
			if holiday.state in ('validate') and not check_fnct(cr, uid, 'write', raise_exception=False):
				raise osv.except_osv(_('Warning!'),_('You cannot modify a Allocation request that has been approved. Contact a human resource manager.'))
		return super(kg_allocation_leave, self).write(cr, uid, ids, vals, context=context)
		
	def _check_duplicate_entry(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		obj = self.pool.get('kg.allocation.leave')
		
		start_date = entry.start_date
		end_date = entry.end_date
		employee = entry.employee_id.id
		dup_ids = obj.search(cr, uid, [('start_date','=',start_date),('end_date','=',end_date),
									('employee_id','=',employee)])
		print "dup_ids =============>>>", dup_ids
		if len(dup_ids) > 1:
			return False
		return True
		
	def approve_entry(self, cr, uid, ids,context=None):		
		self.write(cr,uid,ids,{'state':'validate'})
		return True
		
	def confirm_entry(self, cr, uid, ids,context=None):
		self.write(cr,uid,ids,{'state':'confirm'})	
		return True
	
	def draft_entry(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'draft'})
		return True
		
	_constraints = [
		
		(_check_entry_line, 'Entry line can not be empty !!',['alloc_leave']),
		(_check_duplicate_entry, 'System not allow to save duplicate entries. Check Month and Type !!',['alloc_leave']),
		
		]
		
	_defaults = {
		'state': 'draft'
	} 
		
	
	
kg_allocation_leave()

class kg_allocation_leave_line(osv.osv):
	
	_name = "kg.allocation.leave.line"
	_description = "Allocation Leave Line"
	
	_columns = {

	'entry_id': fields.many2one('kg.allocation.leave', 'Entry No', required=True, ondelete='cascade'),
	'leave_type': fields.selection([('sl','Sick Leave'),('cl','Casual Leave'),('pl','Paid Leave'),('ml','Maternity Leave'),
				   ('pal','Paternity Leave'),('unpaid','Unpaid Medical Leave'),('sf','Staggered Off'),('others','Others')],'Leave Type',required=True),
	'alloc_leave': fields.float('Allocation Days',required=True),
	'used_leave':fields.float('Used Days',readonly=True),
	'allow_limit': fields.boolean('Allow to Over Limit',required=True),
	
	}
	
	_defaults = {
		'allow_limit':True,
	}
	
	def _check_duplicate_leave(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		obj = self.pool.get('kg.allocation.leave.line')
		entry_id = entry.id
		leave_type = entry.leave_type
		dup_leave = obj.search(cr, uid, [('leave_type','=',leave_type),('leave_type','=',leave_type)])
		print "dup_leave =============>>>", dup_leave
		if len(dup_leave) > 1:
			return False
		return True
		
	"""_constraints = [
		
		(_check_duplicate_leave, 'System not allow to save duplicate entries',['dup_leave']),
		
		]"""
		
	
	
kg_allocation_leave_line()	
