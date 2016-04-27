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
	
class kg_baask_sal_muster(osv.osv_memory):
		
	_name = 'kg.baask.sal.muster'
	
	_columns = {
		
		'dep_id':fields.many2many('hr.department','kg_sal_muster','dep_id','slip_id','Department Name'),
		'slip_id': fields.many2many('hr.payslip', 'kg_sal_muster_slip','wiz_id','slip_id',
					'Payslip Number', domain="[('state','=','done')]"),
		'pay_sch': fields.selection([('5th','5th Pay Day'),('7th','7th Pay Day')], 'PaySchedule Selection', required=True),
		'filter': fields.selection([('filter_date', 'Date')], "Filter by", required=True),
		'date_from': fields.date("Start Date"),
		'date_to': fields.date("End Date"),
		'company_id': fields.many2one('res.company', 'Company')
		
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
		'date_from': _get_last_month_first,
		'date_to': _get_last_month_end,
		'pay_sch': '7th',
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg.baask.sal.muster', context=c),
	}

	def _date_validation_check(self, cr, uid, ids, context=None):
		for val_date in self.browse(cr, uid, ids, context=context):
			if val_date.date_from <= val_date.date_to:
				return True
		return False
 
	_constraints = [
		(_date_validation_check, 'You must select an correct Start Date and End Date !!', ['Valid_date']),
	  ]
	  
	  
	def _build_contexts(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
		result = {}
		result['date_from'] = 'date_from' in data['form'] and data['form']['date_from'] or False
		result['date_to'] = 'date_to' in data['form'] and data['form']['date_to'] or False
		if data['form']['filter'] == 'filter_date':
			result['date_from'] = data['form']['date_from']
			result['date_to'] = data['form']['date_to']
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
			date_from = data['form']['date_from']
			date_from = (datetime.datetime.strptime(date_from, '%Y-%m-%d'))
			data['form']['month'] = date_from.strftime('%B-%Y')
			company_id = data['form']['company_id'][0]
			com_rec = self.pool.get('res.company').browse(cr,uid, company_id)			
			data['form']['company'] = com_rec.name			
			if data['form']['pay_sch'] == '5th':
				data['form']['pay'] = '5th Pay Day'
			else:
				data['form']['pay'] = '7th Pay Day'
								
			return {'type': 'ir.actions.report.xml', 'report_name': 'kg.baask.sal.muster', 'datas': data}


kg_baask_sal_muster()

