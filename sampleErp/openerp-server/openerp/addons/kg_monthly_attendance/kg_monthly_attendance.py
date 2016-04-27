# Monthly Attendance Entry Module

from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import datetime
import calendar
#from dateutil.relativedelta import relativedelta

class kg_monthly_attendance(osv.osv):

	_name = "kg.monthly.attendance"
	_description = "Monthly Attendance"
	_order = "date desc"
	
	_columns = {
		
		'employee_id':fields.many2one('hr.employee', 'Employee Name', required=False,
				readonly=True, states={'open':[('readonly',False)]}),
		'employee_name': fields.char('Employee Code', size=128, readonly=True),
		'start_date': fields.date('Month Start Date', readonly=False),
		'end_date': fields.date('Month End Date', readonly=False),
		'date': fields.date('Creation Date'),
		'mon_tot_days': fields.float('Total Salary Day Of Month',readonly=True),
		'working_days': fields.float('Working Days Of Month',readonly=True),
		'month_tot_day': fields.float('Total Day Of Month', readonly=True),
		'no_half_day': fields.float('No of Half Days',required=False,readonly=True, states={'open':[('readonly',False)]}),
		'no_leave_day': fields.float('No of Late Days',required=False,readonly=True, states={'open':[('readonly',False)]}),
		'active': fields.boolean('Active',readonly=True, states={'open':[('readonly',False)]}),
		'state': fields.selection([('confirm','Confirmed'),('open','Draft'),('cancel','Cancelled')], 'State', readonly=False),
		'punch': fields.float('No.Of.Punch Days',readonly=True, states={'open':[('readonly',False)]}),
		'worked': fields.float('No.Of.Worked Days', required=False,
				readonly=True, states={'open':[('readonly',False)]}),
		'arrear': fields.float('No.Of.Arrear Days', required=False, readonly=True, states={'open':[('readonly',False)]}),
		'ot': fields.float('No.Of.OT Days', required=False,
				readonly=True, states={'open':[('readonly',False)]}),
		'applicable_ot':fields.boolean('aplicable OT'),
		'on_duty': fields.float('No.Of.OnDuty Days', required=False,
				readonly=True, states={'open':[('readonly',False)]}),
		'leave': fields.float('No.Of.Leave Days', required=False,
				readonly=True, states={'open':[('readonly',False)]}),
		'absent': fields.float('No.Of.Absent Days', required=False,
				readonly=True, states={'open':[('readonly',False)]}),
				'cl': fields.float('Casual leave Days', required=False,
				readonly=True, states={'open':[('readonly',False)]}),
		'sickleave': fields.float('Festival Leave Days', required=False,
				readonly=True, states={'open':[('readonly',False)]}),
		'el': fields.float('Earned Leave Days', required=False,
				readonly=True, states={'open':[('readonly',False)]}),
		'user_id' : fields.many2one('res.users', 'User', readonly=False,select=True),
		
	}
	def _applicable_ot(self,cr,uid,ids,context = None):
		mon_obj = self.browse(cr,uid,ids[0])
		print "mon_obj....................",mon_obj.employee_id.id
		cont_search = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',mon_obj.employee_id.id)])
		print "cont_search...............................",cont_search
		if cont_search:
			cont_rec = self.pool.get('hr.contract').browse(cr,uid,cont_search[0])
			print "cont_rec..................................",cont_rec.ot
			print "cont_rec..................................",mon_obj.ot
			if (cont_rec.ot == False) and not (mon_obj.ot >= 0.00):
				return True
			elif (cont_rec.ot == False) and (mon_obj.ot > 0.00):
				raise osv.except_osv(_('OT Days Error'),_('OT is not applicable for this employee!!'))
				return False
			elif (cont_rec.ot == True ) and (mon_obj.ot >= 0.00):
				return True
		else:
			return True
		
	def onchange_employee_code(self, cr, uid, ids, employee_id,employee_name, context=None):
		value = {'employee_name': ''}
		if employee_id:
			emp = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
			value = {'employee_name': emp.emp_code}
		return {'value': value}

	def onchange_leave_days(self, cr, uid,ids,worked,on_duty,month_tot_day,leave, context=None):
		value = {'leave': ''}
		if worked <= month_tot_day:
			print "worked..................",worked
			print "on_duty.................",on_duty
			tot_day = worked + on_duty
			leave_day = month_tot_day - tot_day
			print "leave_day------------------",leave_day
			value = {'leave': leave_day}
		else:
			raise osv.except_osv(_('Worked Days Error'),_('System not allow to enter worked days more than total month days !!'))
		return {'value': value}

	def onchange_tot_workdays(self, cr, uid,ids,worked,ot,on_duty,cl,sickleave,el,arrear,leave,absent,mon_tot_days, context=None):
		print "Worked days on changhe called.............", worked, ot, on_duty,cl, sickleave, el,arrear, leave
		value = {'mon_tot_days': ''}
		print"********ot",ot
		print"cl********",cl
		print "sl******",sickleave
		tot_days = worked + ot + on_duty + cl + sickleave + el + arrear + leave
		print "********total days",tot_days
		if tot_days > 0:
			value = {'mon_tot_days': tot_days}
		else:
			print "No Data........."
		return {'value': value}
  
   
	
	def _check_duplicate_att_entry(self, cr, uid, ids, context=None):
		obj = self.pool.get('kg.monthly.attendance')
		entry = self.browse(cr, uid, ids[0])
		print "entry-----------------", entry
		emp_id = entry.employee_id.id
		start_date = entry.start_date
		end_date = entry.end_date
		dup_ids = obj.search(cr, uid, [( 'start_date','=',start_date),( 'end_date','=',end_date),
									( 'employee_id','=',emp_id)])
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
		
	def _get_working_days(self,cr,uid,context=None):
		# getting previous month start date
		today = datetime.date.today()
		print "today-----------", today
		first = datetime.date(day=1, month=today.month, year=today.year)
		mon = today.month - 1
		if mon == 0:
			mon = 12
		else:
			mon = mon
		tot_days = calendar.monthrange(today.year,mon)[1]
		print "tot_days-------------------------->>>>",tot_days
		test = first - datetime.timedelta(days=tot_days)
		start = test.strftime('%Y-%m-%d')
		print "start---------------",start
		
		last = test - datetime.timedelta(days=1)
		print "yesterday............",last
		# getting previous month end date
		
		today = datetime.date.today()
		pre_last= first - datetime.timedelta(days=1)
		pre_mon_last_date = pre_last.strftime('%Y-%m-%d')
		print "pre_mon...............",pre_mon_last_date
		
		# getting no of working days
		
		daygenerator = (last + timedelta(x + 1) for x in xrange((pre_last - last).days))
		res= sum(1 for day in daygenerator if day.weekday() < 6)
		print "res..........",res
		return res
				
		
	def _month_total_day(self, cr, uid, context=None):
		today = datetime.date.today()
		first = datetime.date(day=1, month=today.month, year=today.year)
		mon = today.month - 1
		if mon == 0:
			mon = 12
		else:
			mon = mon
		res = calendar.monthrange(today.year,mon)[1]
		print "...........................res", res
		return res
		
	def _check_number_of_day(self, cr, uid,ids,context=None):
		obj = self.pool.get('kg.monthly.attendance')
		entry = self.browse(cr, uid, ids[0])
		print "entry-----------------", entry
		tot_day = entry.month_tot_day
		used_day = entry.worked + entry.on_duty + entry.leave + entry.arrear
		if used_day > tot_day:
			return False
		return  True	
		
		
	_constraints = [
		
		(_check_duplicate_att_entry, 'Attendance entry already available for this employee in this month !!',['amount']),		
		#(_check_number_of_day, 'Entered days is greater than month total days !!',['tot_day']),
		#(_applicable_ot,'OT is not aplicable for this employee',['OT Days'])
		] 

	
	_defaults = {
	
	'start_date': _get_last_month_first,
	'end_date': _get_last_month_end,
	'date': fields.date.context_today,
	'month_tot_day': _month_total_day,
	'working_days': _get_working_days,
	'active': True,
	'state': 'open',
	'user_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
	
	}
	
	def confirm_entry(self, cr, uid, ids,context=None):		
		self.write(cr,uid,ids,{'state':'confirm'})
		return True
		
	def cancel_entry(self, cr, uid, ids,context=None):
		slip_obj = self.pool.get('hr.payslip')
		att_ids = slip_obj.search(cr, uid, [('att_id',"=", ids[0]), ('state',"=", 'done')])
		print "att_ids...................", att_ids
		if att_ids:
			raise osv.except_osv(_('Entry Used Already !'),
				_('This attendance entry has used for salary process !!'))
		else:
			self.write(cr,uid,ids,{'state':'cancel'})
		return True
		
	def draft_entry(self, cr, uid, ids,context=None):		
		self.write(cr,uid,ids,{'state':'open'})
		return True
	
	def unlink(self, cr, uid, ids, context=None):
		for att in self.browse(cr, uid, ids, context=context):
			end_date = att.start_date
			today = time.strftime("%Y-%m-%d")
			print "end_date ::::::::", type(end_date)
			print "today ::::::::::", type(today)
			#if end_date < today:
			if att.state != 'open':
				raise osv.except_osv(_('Warning!'),
				_('You cannot delete this Entry which is not in open state !!'))
		return super(kg_monthly_attendance, self).unlink(cr, uid, ids, context)
	
	def active_days_calculation(self, cr, uid, ids,context=None):
		print "active_days_calculation <<<-----ids--------->>>",ids
		att_obj = self.pool.get('hr.attendance')
		emp_obj = self.pool.get('hr.employee')		
		today = date.today()
		d = today - relativedelta(months=1)
		print "today ^^^^^^^^^^^^^^^^", d
		last_start = date(d.year, d.month, 1) 
		print "last_start ^^^^^^^^^^^^^^^^", last_start
		last_end = date(today.year, today.month, 1) - relativedelta(days=1) 
		print "emp_obj ^^^^^^^^^^^^^^^^", emp_obj	
		emp_ids = emp_obj.search(cr, uid,(['active','=',1]))		
		print "emp_ids----------------------------",emp_ids
		
	def attendance_close(self, cr, uid, ids, context=None):
		print "attendance_close --- called----------ids", ids
		rec = self.browse(cr, uid, ids[0])
		today = time.strftime("%Y-%m-%d")
		end_date = rec.end_date
		if end_date < today:
			rec.write({'state' : 'close'})
		else:
			print "state will close soon"
			
	def create(self, cr, uid, vals,context=None):
		print "vals................", vals
		if vals.has_key('employee_id') and vals['employee_id']:
			emp_rec = self.pool.get('hr.employee').browse(cr,uid,vals['employee_id'])
			if emp_rec:
				total = vals['worked'] + vals['ot'] + vals['on_duty'] + vals['leave'] + vals['arrear'] + vals['sickleave'] + vals['el'] + vals['cl']
				print "create........total..........", total
				vals.update({'employee_name':emp_rec.emp_code, 'mon_tot_days': total})		
		order =  super(kg_monthly_attendance, self).create(cr, uid, vals, context=context)
		return order
		
	def write(self, cr, uid,ids, vals, context=None):
		print "write........vals..............", vals, ids
		if vals:
			rec = self.browse(cr, uid, ids[0])
			emp_rec = self.pool.get('hr.employee').browse(cr,uid,rec.employee_id.id)
			print "rec vals.....", rec.worked, rec.ot, rec.on_duty, rec.leave, rec.arrear, rec.sickleave, rec.el, rec.cl
			if vals.has_key('leave'):
				leave = vals['leave']
			else:
				leave = rec.leave
			if vals.has_key('worked'):
				worked = vals['worked']
			else:
				worked = rec.worked
			if vals.has_key('ot'):
				ot = vals['ot']
			else:
				ot = rec.ot
			if vals.has_key('on_duty'):
				on_duty = vals['on_duty']
			else:
				on_duty = rec.on_duty
			if vals.has_key('arrear'):
				arrear = vals['arrear']
			else:
				arrear = rec.arrear
			if vals.has_key('sickleave'):
				sickleave = vals['sickleave']
			else:
				sickleave = rec.sickleave
			if vals.has_key('cl'):
				cl = vals['cl']
			else:
				cl = rec.cl
			if vals.has_key('el'):
				el = vals['el']
			else:
				el = rec.el

			total =  worked + ot + on_duty + leave + arrear + sickleave + cl + el
			print "total.............write.......", total
			vals.update({'employee_name':emp_rec.emp_code, 'mon_tot_days': total})						 
		res = super(kg_monthly_attendance, self).write(cr, uid, ids,vals, context)		
		return res
					
	
kg_monthly_attendance()
