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

class kg_leave_summary_wiz(osv.osv_memory):
	_name = 'kg.leave.summary.wiz'
	_columns = {
		
		'dep_id':fields.many2many('hr.department','kg_lve_sum_muster','dep_id','slip_id','Department Name'),
		'filter': fields.selection([('filter_date', 'Date')], "Filter by", required=True),
		'date_from': fields.date("Start Date"),
		'date_to': fields.date("End Date"),
		'employee': fields.many2one('hr.employee', 'Employee'),
		'leave_type': fields.selection([('sl','Festival Leave'),('cl','Casual Leave'),('el','Earned Leave'),('unpaid','Unpaid')],'Leave Type',required=True),
        
		
	}
	
	_defaults = {
		
		'filter': 'filter_date', 
		'date_from': time.strftime('%Y-%m-%d'),
		'date_to': time.strftime('%Y-%m-%d'),
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
		data['form'].update(self.read(cr, uid, ids[0]))
		if data['form']:
			date_from = str(data['form']['date_from'])
			date_to = str(data['form']['date_to'])
			data['form']['date_from_ind'] = self.date_indian_format(date_from)			
			data['form']['date_to_ind'] = self.date_indian_format(date_to)
			if data['form']['leave_type'] == 'sl':
				data['form']['leave'] = 'Festival '
			elif data['form']['leave_type'] == 'cl':
				data['form']['leave'] = 'Casual '
			elif data['form']['leave_type'] == 'el':
				data['form']['leave'] = 'Earned '
			elif data['form']['leave_type'] == 'unpaid':
				data['form']['leave'] = 'Unpaid ' 
			
			return {'type': 'ir.actions.report.xml', 'report_name': 'kg.leave.summary.rep', 'datas': data}	
kg_leave_summary_wiz()
