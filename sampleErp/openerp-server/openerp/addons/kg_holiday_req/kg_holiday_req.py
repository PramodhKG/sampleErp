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

class kg_holiday_req(osv.osv):

	_name = "kg.holiday.req"
	_description = "Leave Request"
	
	def _employee_get(self, cr, uid, context=None):
		ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
		if ids:
			return ids[0]
		return False
		
	
	
	_columns = {
			
		'state': fields.selection([('draft', 'To Submit'),('cancel','Cancel'),('confirm', 'To Approve'),('validate','Approved')],
			'Status', readonly=True, track_visibility='onchange'),
		'user_id':fields.related('employee_id', 'user_id', type='many2one', relation='res.users', string='User', store=True),
		'date_from': fields.datetime('Month Start Date', required=True, readonly=True, states={ 'draft':[('readonly',False)]}),
		'date_to': fields.datetime('Month End Date', required=True,readonly=True, states={ 'draft':[('readonly',False)]}),
		'employee_code': fields.char("Employee Code",readonly=True, states={ 'draft':[('readonly',False)]}),
		'employee_id': fields.many2one('hr.employee', "Employee Name", select=True,required=True, readonly=True, states={ 'draft':[('readonly',False)]}),
		'leave_type': fields.selection([('sl','Sick Leave'),('cl','Casual Leave'),('pl','Paid Leave'),('ml','Maternity Leave'),
				   ('pal','Paternity Leave'),('unpaid','Unpaid Medical Leave'),('sf','Staggered Off'),('others','Others')],'Leave Type',required=True,
				   readonly=True, states={ 'draft':[('readonly',False)]}),
		'no_of_days':fields.float('Duration',readonly=True, states={ 'draft':[('readonly',False)]}),
		'approved_days':fields.float('Approved Days',states={'confirm':[('readonly',True)]}),
		'reason':fields.text('Reason',required=True,readonly=True, states={ 'draft':[('readonly',False)]}),
		'department_id':fields.many2one('hr.department','Department', select=True,readonly=True, states={ 'draft':[('readonly',False)]}),
		
	}

	
	def onchange_employee(self, cr, uid, ids, employee_id):
		result = {'value': {'department_id': False}}
		if employee_id:
			employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
			result['value'] = {'employee_code': employee.emp_code,'department_id': employee.department_id.id}
		return result
		
	def unlink(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state not in ['draft']:
				raise osv.except_osv(_('Warning!'),_('You cannot delete a Leave Request which is in %s state.')%(rec.state))
		return super(kg_holiday_req, self).unlink(cr, uid, ids, context)
		
	def write(self, cr, uid, ids, vals, context=None):
		for  holiday in self.browse(cr, uid, ids, context=context):
			if holiday.state in ('validate') and not check_fnct(cr, uid, 'write', raise_exception=False):
				raise osv.except_osv(_('Warning!'),_('You cannot modify a Allocation request that has been approved. Contact a human resource manager.'))
		return super(kg_holiday_req, self).write(cr, uid, ids, vals, context=context)
		
	def approve_entry(self, cr, uid, ids,context=None):	
		
		leave_rec = self.browse(cr,uid,ids[0])
		if leave_rec.no_of_days > 0:			
			emp_name=leave_rec.employee_id.id
			alloc_obj=self.pool.get('kg.allocation.leave')
			alloc_id=alloc_obj.search(cr,uid,[('employee_id','=',emp_name)])
			print "alloc_id..................",alloc_id
			line_obj=self.pool.get('kg.allocation.leave.line')
			line_id = line_obj.search(cr,uid,[('leave_type','=',leave_rec.leave_type),
								('entry_id','=',alloc_id)])
			print "line_id.......................", line_id
			line_rec = line_obj.browse(cr,uid,line_id[0])
			old_used_leave = line_rec.used_leave
			cur_leave = leave_rec.approved_days
			new_user_leave = old_used_leave + cur_leave
			now = datetime.datetime.now()
			print "month",now.month
			cur_month = now.month
			allocated_days = line_rec.alloc_leave
			cur_month_days = allocated_days/12
			mon_days = cur_month * cur_month_days
			print "mon_days..........",mon_days
			tot_mon_days = mon_days - old_used_leave
			print ",,,,,,,,,,,,,,,,,,,,",tot_mon_days
			if leave_rec.approved_days <= tot_mon_days:
				line_rec.write({'used_leave':new_user_leave})
				self.write(cr,uid,ids,{'state':'validate'})
			else:
				raise osv.except_osv(_
				('Number of Days is greater than Allocated Days  !'), 
				_(' Please give Number of Days below allocated days!!'))
		else:
			raise osv.except_osv(_
				('Number of Days is less than 0 !'), 
				_('Leave Request entry is not allowed with less than 0!!'))
		return True
	
	def cancel_entry(self, cr, uid, ids,context=None):
		self.write(cr, uid, ids, {'state':'cancel'})
		return True
		
	def confirm_entry(self, cr, uid, ids,context=None):
		leave_rec = self.browse(cr,uid,ids[0])
		emp_name=leave_rec.employee_id.id
		alloc_obj=self.pool.get('kg.allocation.leave')
		alloc_id=alloc_obj.search(cr,uid,[('employee_id','=',emp_name)])
		print "alloc_id..................",alloc_id
		line_obj=self.pool.get('kg.allocation.leave.line')
		line_id = line_obj.search(cr,uid,[('leave_type','=',leave_rec.leave_type),
							('entry_id','=',alloc_id)])
		print "line_id.......................", line_id
		if line_id:
			line_rec = line_obj.browse(cr,uid,line_id[0])
			
			
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
			prev_start_date = test.strftime('%Y-%m-%d')
			print "---------------",prev_start_date
			
			last = first - datetime.timedelta(days=1)
			prev_end_date = last.strftime('%Y-%m-%d')
			print "---------------",prev_end_date
			if leave_rec.no_of_days > line_rec.alloc_leave:
				raise osv.except_osv(_
					('Number of Days is less than Allocated days !'), 
					_('Please check the allocated leave days for this employee!!'))
			elif leave_rec.date_from >= prev_start_date and leave_rec.date_from <= prev_end_date:
				raise osv.except_osv(_
					('Start Date and End Date is wrong !'), 
					_('System not allows leave request for previous month!!'))
			else:
				self.write(cr,uid,ids,{'state':'confirm'})
				
		else:
			raise osv.except_osv(_('Warning!'),_('Specified leave is not allocated for this employee'))
			
		return True
	
	def _get_number_of_days(self, date_from, date_to):
		"""Returns a float equals to the timedelta between two dates given as string."""

		DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
		from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
		to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
		timedelta = to_dt - from_dt
		diff_day = timedelta.days + float(timedelta.seconds) / 86400
		return diff_day

	

	def onchange_date_from(self, cr, uid, ids, date_to, date_from):
		"""
		If there are no date set for date_to, automatically set one 8 hours later than
		the date_from.
		Also update the number_of_days.
		"""
		# date_to has to be greater than date_from
		if (date_from and date_to) and (date_from > date_to):
			raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

		result = {'value': {}}

		# No date_to set so far: automatically compute one 8 hours later
		if date_from and not date_to:
			date_to_with_delta = datetime.datetime.strptime(date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=8)
			result['value']['date_to'] = str(date_to_with_delta)

		# Compute and update the number of days
		if (date_to and date_from) and (date_from <= date_to):
			diff_day = self._get_number_of_days(date_from, date_to)
			result['value']['no_of_days'] = round(math.floor(diff_day))+1
			result['value']['approved_days'] = round(math.floor(diff_day))+1
		else:
			result['value']['no_of_days'] = 0
			result['value']['approved_days'] = 0

		return result

	def onchange_date_to(self, cr, uid, ids, date_to, date_from):
		"""
		Update the number_of_days.
		"""

		# date_to has to be greater than date_from
		if (date_from and date_to) and (date_from > date_to):
			raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

		result = {'value': {}}

		# Compute and update the number of days
		if (date_to and date_from) and (date_from <= date_to):
			diff_day = self._get_number_of_days(date_from, date_to)
			result['value']['no_of_days'] = round(math.floor(diff_day))+1
			result['value']['approved_days'] = round(math.floor(diff_day))+1
		else:
			result['value']['approved_days'] = 0

		return result
		
		
	_defaults = {
		'employee_id': _employee_get,
		'state': 'draft',
		'user_id': lambda obj, cr, uid, context: uid,
		
	} 
		
	
	
kg_holiday_req()

