import time
from report import report_sxw
from osv import osv
from tools import number_to_text_convert_india
from reportlab.pdfbase.pdfmetrics import stringWidth
from operator import itemgetter
import tools
from osv import fields, osv
import time, datetime
from datetime import *
import logging
import locale
import netsvc
logger = logging.getLogger('server')

class grn_to_issue(report_sxw.rml_parse):
	
	_name = 'grn.to.issue'
	_inherit='stock.picking'
	
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(grn_to_issue, self).__init__(cr, uid, name, context=context)
		self.query = ""
		self.period_sql = ""
		self.localcontext.update( {
			'time': time,
			'get_filter': self._get_filter,
			'get_start_date':self._get_start_date,
			'get_end_date':self._get_end_date,
			'get_data':self.get_data,
			'locale':locale,
		
		})
		self.context = context

	def get_data(self,form):
		res = {}
		where_sql = []		
		
		if form['product_id']:
			for ids1 in form['product_id']:
				where_sql.append("sm.product_id = %s"%(ids1))			
				
		if where_sql:
			where_sql = 'and ('+' or '.join(where_sql)
			where_sql =  where_sql+')'
		else:
			where_sql = ''
		
				
		self.cr.execute('''
				SELECT
				distinct on (sm.id)
				sp.id AS sp_id,
				sp.name AS issue_no,
				to_char(sp.date, 'mm/dd/yyyy') AS issue_date,
				sp.date AS sp_date,
				sm.po_to_stock_qty AS issue_qty,
				pt.name AS pro_name,
				uom.name AS uom,
				smsp.name AS grn_no,
				to_char(smsp.date, 'mm/dd/yyyy') AS grn_date,
				smsp.date AS ta_grn_date,
				smp.po_to_stock_qty AS grn_qty
				
				
				FROM  stock_picking sp
				
				JOIN stock_move sm ON (sm.picking_id=sp.id and sm.move_type='out')
				JOIN product_uom uom ON (uom.id=sm.product_uom)
				JOIN product_product prd ON (prd.id=sm.product_id)								
				JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
				JOIN kg_out_grn_lines grn_out ON (grn_out.grn_id=sm.id)
				JOIN stock_production_lot lot ON(lot.id=grn_out.lot_id)
				JOIN stock_move smp ON (smp.id=lot.grn_move and smp.move_type='in' and smp.product_id = sm.product_id)
				JOIN stock_picking smsp ON(smsp.id=smp.picking_id and smsp.type='in')
				
				where sp.state=%s and sp.type=%s and sp.date >=%s and sp.date <=%s  '''+ where_sql + '''
				order by sm.id''',('done','out',form['date_from'],form['date_to'])) 
				
		data = self.cr.dictfetchall()
		print "data =============>>>>>>>>>>>>>...........", data
		po_obj = self.pool.get('purchase.order')
		for sp in data:
			grn_date = sp['ta_grn_date']
			issue_date = sp['sp_date']
			fmt = '%Y-%m-%d'
			from_date = grn_date    
			to_date = issue_date
			print "from_date ::::::::::", from_date, "to_date  :::::::::", to_date
			d1 = datetime.strptime(from_date, fmt)
			d2 = datetime.strptime(to_date, fmt)
			daysDiff = str((d2-d1).days)
			print "daysDiff--------------->>", daysDiff
			sp['tat_days'] = daysDiff
		
			
		return data
	
	def _get_filter(self, data):
		if data.get('form', False) and data['form'].get('filter', False):
			if data['form']['filter'] == 'filter_date':
				return _('Date')
		return _('No Filter')
		
	def _get_start_date(self, data):
		if data['form']['filter'] == 'filter_date':
			if data.get('form', False) and data['form'].get('date_from', False):
				return data['form']['date_from']
		else:
			return False
		
	def _get_end_date(self, data):
		if data['form']['filter'] == 'filter_date':
			if data.get('form', False) and data['form'].get('date_to', False):
				return data['form']['date_to']
		else:
			return False
		
	def _get_currency_data(self,data):
		cur_browse = self.pool.get('res.currency').browse(self.cr, self.uid, data)
		return cur_browse.name
	   
 
report_sxw.report_sxw('report.grn.to.issue','stock.picking',
						'addons/kg_grn/report/grn_to_issue.rml',
						parser=grn_to_issue, header= False)
