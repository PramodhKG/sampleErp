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

class po_indent_to_grn(report_sxw.rml_parse):
	
	_name = 'po.indent.to.grn'
	_inherit='stock.picking'
	
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(po_indent_to_grn, self).__init__(cr, uid, name, context=context)
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
				sp.name AS grn_no,
				to_char(sp.date, 'dd/mm/yyyy') AS grn_date,
				sp.date AS sp_date,
				sm.po_to_stock_qty AS grn_qty,
				pt.name AS pro_name,
				uom.name AS uom,
				pi_line.product_qty AS pi_qty,
				pi.name AS pi_no,
				to_char(pi.date_start, 'dd/mm/yyyy') AS pi_date,
				pi.date_start AS tpi_date		
				
				FROM  stock_picking sp
				
				JOIN stock_move sm ON (sm.picking_id=sp.id)
				JOIN purchase_order_line as pol on(pol.id = sm.purchase_line_id)
				JOIN purchase_requisition_line as pi_line on(pi_line.id = pol.pi_line_id)
				JOIN purchase_requisition as pi on(pi.id = pi_line.requisition_id)
				JOIN product_uom uom ON (uom.id=pol.product_uom)
				JOIN product_product prd ON (prd.id=pol.product_id)								
				JOIN product_template pt ON (pt.id=prd.product_tmpl_id)				
				
				where sp.state=%s and sp.type=%s and sp.date >=%s and sp.date <=%s  '''+ product + '''
				order by pi.name''',('done','in',form['date_from'],form['date_to'])) 
				
		data = self.cr.dictfetchall()
		print "data =============>>>>>>>>>>>>>...........", data
		po_obj = self.pool.get('purchase.order')
		fmt = '%Y-%m-%d'
		fmt_time = '%Y-%m-%d %H:%M:%S'
		for sp in data:
			pi_date = sp['tpi_date']
			grn_date = sp['sp_date']
			from_date = pi_date    
			to_date = grn_date
			d = datetime.strptime(from_date, fmt_time)
			from_date = d.strftime('%Y-%m-%d')
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
	   
 
report_sxw.report_sxw('report.po.indent.to.grn','stock.picking',
						'addons/kg_purchase_order/report/po_indent_to_grn.rml',
						parser=po_indent_to_grn, header= False)
