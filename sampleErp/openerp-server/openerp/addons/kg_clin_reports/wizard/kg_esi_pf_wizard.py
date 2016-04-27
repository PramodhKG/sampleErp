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

class kg_esi_pf_wizard(osv.osv_memory):
	_name = 'kg.esi.pf.wizard'
	_columns = {
		
		'dep_id':fields.many2many('hr.department','esi_pf','esi_pf_id','depart_id','Department Name'),
		'branch':fields.many2many('kg.branch','branch_id','branch_id','emp_id','Branch Name'),
		'filter': fields.selection([('pf', 'PF Employee'),('esi','ESI Employee'),('both','Both'),('not_both','Not In Both')], "Filter by", required=True),
		'company_id': fields.many2one('res.company', 'Company')
		
		
	}
	_defaults = {
		'filter':'filter_month',
		'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'kg.esi.pf.wizard', context=c),

	}
	def _build_contexts(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
		result = {}
		result['month'] = 'month' in data['form'] and data['form']['month'] or False
		#result['date_to'] = 'date_to' in data['form'] and data['form']['date_to'] or False
		if data['form']['filter'] == 'filter_month':
			result['month'] = data['form']['month']
			#result['date_to'] = data['form']['date_to']
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
			"""month = data['form']['month']
			month = (datetime.datetime.strptime(month,'%m'))
			data['form']['start_month'] = month.strftime('%B')
			data['form']['year'] =month.strftime('%Y')
			date_to = data['form']['date_to']
			date_to = (datetime.datetime.strptime(date_to,'%Y-%m-%d'))
			data['form']['end_month'] = date_to.strftime('%d-%b-%y')
			data['form']['e_month'] = date_to.strftime('%b-%y')"""
			print data['form']['company_id']
			company_id = data['form']['company_id']
			print data['form']['filter']
			print company_id
			com_rec = self.pool.get('res.company').browse(cr,uid, company_id)			
			data['form']['company'] = com_rec.name	
			return {'type': 'ir.actions.report.xml', 'report_name': 'kg.esi.pf.report', 'datas': data}

	
kg_esi_pf_wizard()
	
