import time
from lxml import etree
from osv import fields, osv
from tools.translate import _
import pooler
import logging
import netsvc
import datetime as lastdate
import datetime
import calendar

logger = logging.getLogger('server')

class kg_monthly_attendance_rpt(osv.osv_memory):
	_name = 'kg.monthly.attendance.rpt'
	_columns = {
		
		'dep_id':fields.many2many('hr.department','kg_monthly_dept_atten','monthly_atten_id','monthly_dept_id','Department Name'),
		'emp_name':fields.many2one('hr.employee','Employee Name'),
		'filter': fields.selection([('filter_month', 'Month'),('filter_emp','Employee')], "Filter by", required=True),
		'month': fields.selection([('1','Jan'),('2','Feb'),('3','March'),('4','Apr'),
									('5','May'),('6','June'),('7','July'),('8','Aug'),
									('9','Sep'),('10','Oct'),('11','Nov'),('12','Dec')],'Month', required=True),
		'year':fields.integer('Year',size = 4,required=True),
		#'date_from': fields.date("Start Date"),
		#'date_to': fields.date("End Date"),
		'company_id': fields.many2one('res.company', 'Company')
		
	}
	_defaults = {
		'filter':'filter_month',
		'month':'1',
		'year' :2015,
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg.monthly.attendance.rpt', context=c),
	}
	def _build_contexts(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
		result = {}
		result['month'] = 'month' in data['form'] and data['form']['month'] or False
		result['year'] = 'year' in data['form'] and data['form']['year'] or False
		#result['date_to'] = 'date_to' in data['form'] and data['form']['date_to'] or False
		if data['form']['filter'] == 'filter_month':
			result['month'] = data['form']['month']
			result['year'] = data['form']['year']
		return result
	  
	def check_report(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		data = {}
		data['ids'] = context.get('active_ids', [])
		data['model'] = context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(cr, uid, ids, [])[0]
		used_context = self._build_contexts(cr, uid, ids, data, context=context)
		data['form']['used_context'] = used_context
		return self._print_report(cr, uid, ids, data, context=context)
		
	def pre_print_report(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
		data['form'].update(self.read(cr, uid, ids, [], context=context)[0])
		return data
		
		
	def _print_report(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
		data = self.pre_print_report(cr, uid, ids, data, context=context)
		data['form'].update(self.read(cr, uid, ids)[0])
		if data['form']:
			month = data['form']['month']
			month = (datetime.datetime.strptime(month,'%m'))
			data['form']['start_month'] = month.strftime('%B')
			year = data['form']['year']
			year = str(year)
			year = (datetime.datetime.strptime(year,'%Y'))
			data['form']['year'] = year.strftime('%Y')
			print data['form']['company_id']
			company_id = data['form']['company_id']
			print company_id
			com_rec = self.pool.get('res.company').browse(cr,uid, company_id)			
			data['form']['company'] = com_rec.name	
			return {'type': 'ir.actions.report.xml', 'report_name': 'kg.monthly.attend.rpt', 'datas': data}

kg_monthly_attendance_rpt()
	
