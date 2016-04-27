import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale
from datetime import date
import datetime

class kg_pending_depindent_report(report_sxw.rml_parse):
	
	_name = 'kg.pending.depindent.report'
	_inherit='kg.depindent,kg.depindent.line'  

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_pending_depindent_report, self).__init__(cr, uid, name, context=context)
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
		indent = []
				
		if form['dep_id']:
			location = form['dep_id'][0]
			where_sql.append("indent.dep_name = %s" %(location))
		
		if form['ind_id']:
			for ids2 in form['ind_id']:
				indent.append("indent.id = %s"%(ids2))

			

		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
			
		else:
			where_sql=''		
			
			
		if indent:
			indent = ' and '+' or '.join(indent)
			
		else:
			indent=''		
			
		print "department.............................", where_sql
		print "indent....................................",indent
		print "form[d................................",form['date_from']
		print "form[d................................",form['date_to']
		
		self.cr.execute('''
				SELECT  indent.id as indent_id, 
				to_char(indent.date,'dd/mm/yyyy') as date, 
				indent.name as indent_number,
				depline.qty as indent_qty,
				depline.issue_pending_qty as issue_pen_qty,
				temp.name as product_name,
				uom.name as product_uom
				
				
				FROM  kg_depindent indent
				
				left join kg_depindent_line depline on (depline.indent_id=indent.id)
				left join product_product pro on (pro.id=depline.product_id)
				left join product_template temp on (temp.id=pro.product_tmpl_id)
				left join product_uom uom on(uom.id=depline.uom)
				
				
				where indent.state = %s and indent.date >=%s and indent.date <=%s '''+ where_sql + indent +'''
				order by indent.date, indent.name ''',('approved',form['date_from'],form['date_to']))
				
		data = self.cr.dictfetchall()
		print "Data ABBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", data
		
		data_renew = []
		for item in data:
			print "&&***&&&",item
			if item['issue_pen_qty'] > 0.0:
				if item['indent_qty'] == item['issue_pen_qty']:
					item['pending_qty'] = item['issue_pen_qty']
					data_renew.append(item)
					print "-----===========data_renew==========>",data_renew
				elif item['indent_qty'] != item['issue_pen_qty']:
					item['pending_qty'] = item['indent_qty'] - item['issue_pen_qty']
					data_renew.append(item)
					print "-----===========data_renew==========>",data_renew
			else:
				pass
		data = data_renew
		print "=================data============>",data
				
		return data
			
			   

	def _get_filter(self, data):
		if data.get('form', False) and data['form'].get('filter', False):
			if data['form']['filter'] == 'filter_date':
				return _('Date')			
		return _('No Filter')
		
	def _get_start_date(self, data):
		if data.get('form', False) and data['form'].get('date_from', False):
			return data['form']['date_from']
		return ''
		
	def _get_end_date(self, data):
		if data.get('form', False) and data['form'].get('date_to', False):
			return data['form']['date_to']
		return ''		   
  

report_sxw.report_sxw('report.kg.pending.depindent.report','kg.depindent','addons/kg_depindent/report/kg_pending_depindent_report.rml',
						parser=kg_pending_depindent_report, header= False)
			
