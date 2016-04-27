from osv import fields, osv
from datetime import datetime
from tools.translate import _
import time
import logging
import netsvc
logger = logging.getLogger('server')
class kg_ir_sequence(osv.osv):
	
	_name = "ir.sequence"
	_inherit = "ir.sequence"	
	
	def _process(self,cr,uid,s):
		logger.info('[KG ERP] Class: kg_ir_sequence, Method: _process called...')
		"""
		Overwrite:To add fiscal year
		"""	 
		fiscal_obj = self.pool.get('account.fiscalyear')   
		date = datetime.now().strftime('%Y-%m-%d')
		f_ids = fiscal_obj.search(cr,uid,[('state','=','draft'),('date_start','<=',date),('date_stop','>=',date)])
		code = ''
		if f_ids:
			code = fiscal_obj.browse(cr,uid,f_ids[0]).code
		return (s or '') % {
			'year':time.strftime('%Y'),
			'month': time.strftime('%m'),
			'day':time.strftime('%d'),
			'y': time.strftime('%y'),
			'doy': time.strftime('%j'),
			'woy': time.strftime('%W'),
			'weekday': time.strftime('%w'),
			'h24': time.strftime('%H'),
			'h12': time.strftime('%I'),
			'min': time.strftime('%M'),
			'sec': time.strftime('%S'),
			'f': code,
		}
	
	
	
	def kg_get_id(self, cr, uid, sequence_id, test='id', context=None):
		logger.info('[KG ERP] Class: kg_ir_sequence, Method: kg_get_id called...')
		"""
		Overwrite:To switch auto increment functionality
		"""
		assert test in ('code','id')
		company_id = self.pool.get('res.users').read(cr, uid, uid, ['company_id'], context=context)['company_id'][0] or None
		cr.execute('''SELECT id, number_next, prefix, suffix, padding
					  FROM ir_sequence
					  WHERE %s=%%s
					   AND active=true
					   AND (company_id = %%s or company_id is NULL)
					  ORDER BY company_id, id
					  FOR UPDATE NOWAIT''' % test,
					  (sequence_id, company_id))
		res = cr.dictfetchone()
		print "res ====================>>>", res
		if res:
			if context and 'noupdate' in context and context['noupdate']:
				print "Not updating sequence",context
				#cr.execute('UPDATE ir_sequence SET number_next=number_next+number_increment WHERE id=%s AND active=true', (res['id'],))
				
			else:
				print "elselllllllllllllllll block" ,res['id']
				cr.execute('UPDATE ir_sequence SET number_next=number_next+number_increment WHERE id=%s AND active=true', (res['id'],))
			if res['number_next']:
				return self._process(cr,uid,res['prefix']) + '%%0%sd' % res['padding'] % res['number_next'] + self._process(cr,uid,res['suffix'])
			else:
				return self._process(cr,uid,res['prefix']) + self._process(cr,uid,res['suffix'])
		return False
		
kg_ir_sequence()
