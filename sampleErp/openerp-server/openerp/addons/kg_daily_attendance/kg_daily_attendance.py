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
import openerp
#from dateutil.relativedelta import relativedelta

class kg_daily_attendance(osv.osv):

	_name = "kg.daily.attendance"
	_description = "Daily Attendance"
	_order = "date desc"
	
	_columns = {
		
		'creation_date':fields.datetime('Creation Date',readonly=True,),
		'created_by' : fields.many2one('res.users', 'Created By', readonly = True,select=True),
		'date': fields.date('Date',required = True,states={'approve': [('readonly', True)]}),
		'state': fields.selection([('approve','Confirmed'),('draft','Draft'),('load','Load')], 'State',readonly = True),
		'entry_id': fields.one2many('kg.daily.attendance.line','entry_line','Entry Id',states={'approve': [('readonly', True)]}),
		'present_count': fields.integer('Present Count'),
		'absent_count': fields.integer('Absent Count'),
		'on_duty_count': fields.integer('On Duty Count'),
		'half_day_count': fields.integer('Half-Day Count'),
		'late_count': fields.integer('Late Count'),
		'tot_count':fields.integer('Total Count')
		
	}
	
	_defaults = {
	
	'state': 'draft',
	'creation_date': lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
	'created_by': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
	'date':  fields.date.context_today,

	
	}
	
	def onchange_employee_code(self, cr, uid, ids, employee_id,employee_code,context=None):
		value = {'employee_code':''}
		if employee_id:
			emp = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
			print emp.join_date
			
			value = {
					'employee_code': emp.emp_code,
					}
		return {'value': value}
	
	def create(self, cr, uid, vals,context=None):
		if vals.has_key('employee_id') and vals['employee_id']:
			emp_rec = self.pool.get('hr.employee').browse(cr,uid,vals['employee_id'])
			if emp_rec:
				vals.update({
						
							'employee_code':emp_rec.emp_code,
							
							})						  
		order =  super(kg_daily_attendance, self).create(cr, uid, vals, context=context)
		return order
	
	def load_employee_attandance(self,cr,uid,ids,context = None):
		entry = self.browse(cr,uid,ids[0])
		line_obj = self.pool.get('kg.daily.attendance.line')
		emp_sql = """	select res.id as id,emp.emp_code as employee_code,dept.name as dept_name
						from resource_resource res
						left join hr_employee emp on (emp.id = res.id)
						left join hr_department dept on (emp.department_id = dept.id)
						where res.active = 't' and res.id != 1 and emp.status = 'in_service'  """
		cr.execute(emp_sql)
		data = cr.dictfetchall()
		print "data...........",data
		for item in data:
			emp_rec = self.pool.get('hr.employee').browse(cr,uid,item['id'])
			print emp_rec.department_id
			print emp_rec.id
			print emp_rec.emp_code
			vals = {
						'employee_id': emp_rec.id,
						'employee_code': emp_rec.emp_code,
						'dept_name': emp_rec.department_id.id,
						'emp_status': 'present',
					}	
			form_vals = self.write(cr,uid,entry.id,{'entry_id':[(0,0,vals)]})	
		self.write(cr,uid,entry.id,{'state':'load'})
		return True
		
		
	def confirm_entry(self, cr, uid, ids,context=None):		
		entry = self.browse(cr,uid,ids[0])
		if not entry.entry_id :
			raise openerp.exceptions.Warning(_(' Line Details Should not be empty !!. Please Enter The Value'))
			return False
		else:
			for line in entry.entry_id:
				if line.employee_id == '' or line.employee_code == '' or line.dept_name == '' or line.emp_status == '':
					raise openerp.exceptions.Warning(_('Line Details Should not be empty !!. Please Enter The Value'))
					return False
		self.employee_attendance_count(cr,uid,ids,context = context)
		vals = self.employee_attendance_count(cr,uid,ids,context = context)
		self.write(cr,uid,ids,{'state':'approve','present_count':vals['pre_count'],'tot_count':vals['tot_count'],
								'absent_count':vals['abs_count'],'on_duty_count':vals['od_count'],
								'half_day_count':vals['half_day_count'],'late_count':vals['late_count']})
		return True
		
		
	def employee_attendance_count(self,cr,uid,ids,context = None):
		line_ids = self.pool.get('kg.daily.attendance.line').search(cr,uid,[('entry_line','=',ids[0])])
		print "line_ids   ",line_ids
		pre_count = 0
		abs_count = 0
		half_day_count = 0
		od_count = 0
		tot_count = 0
		late_count = 0
		ids = 0
		while(ids < len(line_ids)):
			line_rec = self.pool.get('kg.daily.attendance.line').browse(cr,uid,line_ids[ids])
			if line_rec.emp_status == 'present':
				pre_count += 1
				
			if line_rec.emp_status == 'absent':
				abs_count += 1
			
			if line_rec.emp_status == 'od':
				od_count += 1
			
			if line_rec.emp_status == 'half_day':
				half_day_count += 1
				
			if line_rec.emp_status == 'late':
				late_count += 1
			ids += 1
		tot_count = half_day_count	+ pre_count	+ abs_count + od_count +late_count
		print "half_day_count",half_day_count
		print "pre_count",pre_count
		print "abs_count",abs_count
		print "od_count",od_count
		print "od_count",late_count
		print "tot_count",tot_count
		vals = {'pre_count':pre_count,'half_day_count':half_day_count,'abs_count':abs_count,'od_count':od_count,
						'tot_count':tot_count,'late_count':late_count}
		return vals
	
	def _get_last_month_first(self, cr, uid,ids, context=None):
		res = {'srt_date':''}
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
		res['srt_date']= test.strftime('%Y-%m-%d')
		print "---------------",res
		return res
		
	def _get_last_month_end(self, cr, uid,ids,context=None):
		res = {'lst_date':''}
		today = datetime.date.today()
		first = datetime.date(day=1, month=today.month, year=today.year)
		last = first - datetime.timedelta(days=1)
		res['lst_date'] = last.strftime('%Y-%m-%d')
		return res
	
	def lst_month_daily_attendance(self,cr,uid,ids,context=None):
		
		self._get_last_month_first(self, cr, uid,ids)
		self._get_last_month_end(self, cr, uid,ids)
		srt_date = self._get_last_month_first(self, cr, uid, ids)
		lst_date = self._get_last_month_end(self, cr, uid,ids)
		srt_date = "'"+srt_date['srt_date']+"'"
		lst_date = "'"+lst_date['lst_date']+"'"
		daily_att_ids = []
		atten_sql = """	select id from kg_daily_attendance where date >= %s and date <= %s
						and state = 'approve'"""%(srt_date,lst_date)
		cr.execute(atten_sql)
		data = cr.dictfetchall()
		print "data...........",data
		
		if data:
			for emp_id in data:	
				daily_att_ids.append(emp_id['id'])
			print daily_att_ids
		daily_att_ids = tuple(daily_att_ids)
		print "daily_att_ids and type",daily_att_ids,type(daily_att_ids)
			
			
		emp_ids_sql = """ select id from hr_employee where status='in_service' and id != 1 """
		cr.execute(emp_ids_sql)
		emp_ids = cr.dictfetchall()
		print "emp_ids...........",emp_ids
		
	
		for ids in emp_ids:
			pre_sql = """select count(id) as pre_count from kg_daily_attendance_line where employee_id= %s and 
							emp_status='present' and entry_line in %s """%(ids['id'],daily_att_ids)
			cr.execute(pre_sql)
			pre_count = cr.dictfetchall()
			emp_rec = self.pool.get('hr.employee').browse(cr,uid,ids['id'])
			print "pre_count",pre_count,emp_rec.id
			
			absent_sql = """select count(id) as abs_count from kg_daily_attendance_line where employee_id= %s and 
							emp_status='absent' and entry_line in %s """%(ids['id'],daily_att_ids)
			cr.execute(absent_sql)
			abs_count = cr.dictfetchall()
			print "abs_count",abs_count
			
			late_sql = """select count(id) as late_count from kg_daily_attendance_line where employee_id= %s and 
							emp_status='late' and entry_line in %s """%(ids['id'],daily_att_ids)
			cr.execute(late_sql)
			late_count = cr.dictfetchall()
			print "late_count",late_count
			
			half_day_sql = """select count(id) as half_day_count from kg_daily_attendance_line where employee_id= %s and 
							emp_status='half_day' and entry_line in %s """%(ids['id'],daily_att_ids)
			cr.execute(half_day_sql)
			half_day_count = cr.dictfetchall()
			print "half_day_count",half_day_count
			
			od_sql = """select count(id) as od_count from kg_daily_attendance_line where employee_id= %s and 
							emp_status='od' and entry_line in %s """%(ids['id'],daily_att_ids)
			cr.execute(od_sql)
			od_count = cr.dictfetchall()
			print "od_count",od_count
			
			cl = 0
			tot_days = 0
			
			if abs_count[0]['abs_count'] == 1:
				abs_count[0]['abs_count'] = 0
				cl = 1
				tot_days += cl
			elif abs_count[0]['abs_count'] >= 1:
				abs_count[0]['abs_count'] = (abs_count[0]['abs_count'] - 1)
				cl = 1
				tot_days += (cl+abs_count[0]['abs_count'] )
				
			if  (cl == 0.00) and (late_count[0]['late_count'] <= 2.00):
				pre_count[0]['pre_count'] += late_count[0]['late_count'] 
				cl = late_count[0]['late_count'] * 0.5
			elif (cl == 0.00) and (late_count[0]['late_count'] >= 2.00) :
				c1 = 1
				pre_count[0]['pre_count'] += (late_count[0]['late_count'] -2)* 0.5
			elif (cl == 1.00) and (late_count[0]['late_count'] > 0.00):
				pre_count[0]['pre_count'] += late_count[0]['late_count'] * 0.5
			
			if half_day_count[0]['half_day_count'] :
				pre_count[0]['pre_count'] += (half_day_count[0]['half_day_count']) * 0.5
				tot_days += (half_day_count[0]['half_day_count']) * 0.5
				
			
			vals = {
							'ot': 0,
							'employee_id':emp_rec.id,
							'worked':pre_count[0]['pre_count'] or 0,
							'no_half_day':half_day_count[0]['half_day_count'] or 0,
							'on_duty':od_count[0]['od_count'] or 0,
							'absent':abs_count[0]['abs_count'] or 0,
							'no_late_day':late_count[0]['late_count'] or 0,
							'leave': 0,
							'arrear':0,
							'sickleave':0,
							'el':0,
							'state':'confirm',
							'cl':cl,
							}
			print "vals",vals
			monthly_att_obj = self.pool.get('kg.monthly.attendance')
			month_attendance = monthly_att_obj.create(cr,uid,vals)
		return vals
			
			
	
	
	def _attendance_duplicate(self, cr, uid, ids, context=None):
		obj = self.pool.get('kg.daily.attendance')
		record = self.browse(cr, uid, ids[0])
		dup_ids = obj.search(cr, uid,[('date','=',record.date)])
		print "dup_ids =======================>>>>", dup_ids
		if len(dup_ids) > 1:
			raise openerp.exceptions.Warning(_('Attendance Alredy Generated for this date!!.'))
			return False
		return True
		
	"""def unlink(self, cr, uid, ids, context=None):
		for att in self.browse(cr, uid, ids, context=context):
			if att.state != 'open':
				raise osv.except_osv(_('Warning!'),
				_('You cannot delete this Entry which is not in open state !!'))
		return super(kg_daily_attendance, self).unlink(cr, uid, ids, context)"""
	
	
	_constraints = [
		
		(_attendance_duplicate, 'Attendance For the is already entred!!',['Line Entry']),
		#(_check_entry_line, 'Entry Lines should not be empty !!',['Line Entry']),
				
		]
	
kg_daily_attendance()


class kg_daliy_attendance_line(osv.osv):
	
	_name = "kg.daily.attendance.line"
	_order = "dept_name"
	
	
	_columns = {
	
			'entry_line':fields.many2one('kg.daily.attendance','Entry Line'),
			'employee_id':fields.many2one('hr.employee','Employee Name',required=True),
			'employee_code':fields.char('Employee Code'),
			'dept_name':fields.many2one('hr.department','Department Name'),
			'emp_status':fields.selection([('present','Present'),('absent','Absent'),('late','Late'),('od','On Duty'),('half_day','Half Day Leave')], 'Status')
		}
		
	
	
		
kg_daliy_attendance_line()
