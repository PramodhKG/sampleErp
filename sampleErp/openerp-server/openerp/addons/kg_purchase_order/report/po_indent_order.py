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

class po_indent_order(report_sxw.rml_parse):
	
	_name = 'po.indent.order'
	_inherit='purchase.order,purchase.order.line'
	
	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(po_indent_order, self).__init__(cr, uid, name, context=context)
		self.query = ""
		self.period_sql = ""
		self.localcontext.update( {
			'time': time,
			'get_filter': self._get_filter,
			'get_start_date':self._get_start_date,
			'get_end_date':self._get_end_date,
			'get_data':self.get_data,
			#'get_data_line':self.get_data_line,
			'locale':locale,
		
		})
		self.context = context

	def get_data(self,form):
		res = {}
		product = []
		
		if form['product_id']:
			for ids1 in form['product_id']:
				product.append("pol.product_id = %s"%(ids1))
				
		if product:
			product = 'and ('+' or '.join(product)
			product =  product+')'
		else:
			product = ''
		
				
		self.cr.execute('''
		
				SELECT 
				po.id as po_id, 
				to_char(po.date_order,'dd/mm/yyyy') as date,
				po.date_order AS tat_po_date,
				po.name AS po_no,
				pol.product_qty AS qty,
				uom.name AS uom,
				pt.name AS name,
				pi.name AS pi_no,
				to_char(pi.date_start, 'dd/mm/yyyy') AS pi_date,
				pi.date_start AS tat_pi_date,
				pi_line.product_qty AS pi_qty
				
				FROM  purchase_order po
				
				JOIN purchase_order_line as pol on(pol.order_id = po.id)
				JOIN purchase_requisition_line as pi_line on(pi_line.id = pol.pi_line_id)
				JOIN purchase_requisition as pi on(pi.id = pi_line.requisition_id)
				JOIN product_uom uom ON (uom.id=pol.product_uom)
				JOIN product_product prd ON (prd.id=pol.product_id)
				JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
				
				where po.state = %s and pol.line_state != %s and po.date_order >=%s and po.date_order <=%s  '''+ product + '''
				order by pi.name ''',('approved','cancel',form['date_from'],form['date_to'])) 
				
		data = self.cr.dictfetchall()
		print "data =============>>>>>>>>>>>>>...........", data
		po_obj = self.pool.get('purchase.order')
		for po in data:
			order_id = po['po_id']
			pi_date = po['tat_pi_date']
			po_date = po['tat_po_date']
			fmt = '%Y-%m-%d'
			fmt_time = '%Y-%m-%d %H:%M:%S'
			from_date = pi_date    
			to_date = po_date			
			d = datetime.strptime(pi_date, fmt_time)
			from_date = d.strftime('%Y-%m-%d')
			print "from_date ::::::::::", from_date, "to_date  :::::::::", to_date
			d1 = datetime.strptime(from_date, fmt)
			d2 = datetime.strptime(to_date, fmt)
			daysDiff = str((d2-d1).days)
			print "daysDiff--------------->>", daysDiff
			po['tat_days'] = daysDiff
		
			
		return data
		
	"""	
	def get_data_line(self,data):
		line_data=[]
		print "data~~~~~~~~~~~~~~~~~~~~~~~~", data
		po_line_id = self.pool.get('purchase.order.line').search(self.cr, self.uid,
						[('order_id', '=', data)], context=None)
		
		po_line_browse = self.pool.get('purchase.order.line').browse(self.cr, self.uid, po_line_id)
		for po_line in po_line_browse:
							
			line ={
			
			'product':po_line.product_id.name,
			'prod_uom':po_line.product_uom.name,
			'prod_qty':po_line.product_qty,			
			}
			
			line_data.append(line)
			
		return line_data
		"""


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
	   
 
report_sxw.report_sxw('report.po.indent.order','purchase.order',
						'addons/kg_purchase_order/report/po_indent_order.rml',
						parser=po_indent_order, header= False)
