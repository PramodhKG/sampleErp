import time
from lxml import etree
from osv import fields, osv
from tools.translate import _
import pooler
import logging
import netsvc
import datetime as lastdate
import calendar
import datetime

logger = logging.getLogger('server')
	
class kg_allowance(osv.osv_memory):
		
	_name = 'kg.allowance'
	
	_columns = {
		
		'filter': fields.selection([('filter_date', 'Date')], "Filter by", required=True),
		'month': fields.selection([('1','Jan'),('2','Feb'),('3','March'),('4','Apr'),
									('5','May'),('6','June'),('7','July'),('8','Aug'),
									('9','Sep'),('10','Oct'),('11','Nov'),('12','Dec')],'Month', required=True),
		'year':fields.integer('Year',size = 4),
		'company_id': fields.many2one('res.company', 'Company'),
		'type': fields.selection([('ALW','Allowance'),('DED','Deduction')],'Select Earning/ Deduction',required=True),
		'pay_type': fields.many2many('hr.salary.rule','rule_id','wiz_id', 'ear_ded_report', 
					'Select Earning/ Deduction', domain="[('category_id','=',type)]"),
		
	}
	
	def _get_last_month_first(self, cr, uid, context=None):
		
		today = lastdate.date.today()
		first = lastdate.date(day=1, month=today.month, year=today.year)
		mon = today.month - 1
		if mon == 0:
			mon = 12
		else:
			mon = mon
		tot_days = calendar.monthrange(today.year,mon)[1]
		test = first - lastdate.timedelta(days=tot_days)
		res = test.strftime('%Y-%m-%d')
		return res
		
	def _get_last_month_end(self, cr, uid, context=None):
		today = lastdate.date.today()
		first = lastdate.date(day=1, month=today.month, year=today.year)
		last = first - lastdate.timedelta(days=1)
		res = last.strftime('%Y-%m-%d')
		return res
	
	_defaults = {
		
		'filter': 'filter_date', 
		'month': '1',
		'year': 2014,
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg.allowance', context=c),
	}

	def _date_validation_check(self, cr, uid, ids, context=None):
		for val_date in self.browse(cr, uid, ids, context=context):
			if val_date.date_from <= val_date.date_to:
				return True
		return False
 
	_constraints = [
		#(_date_validation_check, 'You must select an correct Start Date and End Date !!', ['Valid_date']),
	  ]
	  
	  
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
		
	def date_indian_format(self,date_pyformat):
		date_contents = date_pyformat.split("-")
		date_indian = date_contents[2]+"/"+date_contents[1]+"/"+date_contents[0]
		return date_indian
	  
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
			company_id = data['form']['company_id'][0]
			com_rec = self.pool.get('res.company').browse(cr,uid, company_id)			
			data['form']['company'] = com_rec.name
			type_name = data['form']['type'][-1]
			data['form']['head_type'] = type_name
			return {'type': 'ir.actions.report.xml', 'report_name': 'kg.allowance.report', 'datas': data}


kg_allowance()

