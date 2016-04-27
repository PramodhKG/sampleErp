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

class po_order_issue(report_sxw.rml_parse):
	
	_name = 'po.order.issue'
	_inherit='stock.picking'
	
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(po_order_issue, self).__init__(cr, uid, name, context=context)
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
		product = []		
		
		if form['product_id']:
			for ids1 in form['product_id']:
				product.append("sm.product_id = %s"%(ids1))			
				
		if product:
			product = 'and ('+' or '.join(product)
			product =  product+')'
		else:
			product = ''
		
				
		self.cr.execute('''
		
				SELECT
				sp.id AS sp_id,
				sp.name AS issue_no,
				to_char(sp.date, 'dd/mm/yyyy') AS issue_date,
				sp.date AS sp_date,
				sm.po_to_stock_qty AS issue_qty,
				pol.product_qty AS po_qty,
				pol.id AS pol_id,
				po.name AS po_no,
				to_char(po.date_order, 'dd/mm/yyyy') AS po_date,
				pt.name AS pro_name,
				uom.name AS uom,
				po.date_order AS ta_po_date							
				
				FROM  stock_picking sp
				
				JOIN stock_move sm ON (sm.picking_id=sp.id)
				JOIN kg_out_grn_lines grn_out ON (grn_out.grn_id=sm.id)
				JOIN stock_production_lot lot ON (lot.id=grn_out.lot_id)
				JOIN stock_move smp ON(smp.id=lot.grn_move)
				JOIN purchase_order_line pol ON (pol.id=smp.purchase_line_id)
				JOIN purchase_order po ON(po.id=pol.order_id)
				JOIN product_uom uom ON (uom.id=pol.product_uom)
				JOIN product_product prd ON (prd.id=pol.product_id)								
				JOIN product_template pt ON (pt.id=prd.product_tmpl_id)				
				
				where sp.state=%s and sp.type=%s and sp.date >=%s and sp.date <=%s  '''+ product + '''
				order by po.name''',('done','out',form['date_from'],form['date_to'])) 
				
		data = self.cr.dictfetchall()
		print "data =============>>>>>>>>>>>>>...........", data
		po_obj = self.pool.get('purchase.order')
		for sp in data:
			po_date = sp['ta_po_date']
			issue_date = sp['sp_date']
			fmt = '%Y-%m-%d'
			from_date = po_date    
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
	   
 
report_sxw.report_sxw('report.po.order.issue','stock.picking',
						'addons/kg_purchase_order/report/po_order_issue.rml',
						parser=po_order_issue, header= False)
