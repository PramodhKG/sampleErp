import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale

class consumption_details_report(report_sxw.rml_parse):
	
	_name = 'consumption.details.report'
	_inherit='stock.picking'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(consumption_details_report, self).__init__(cr, uid, name, context=context)
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
		loc = []
		
		if form['dep_id']:
			department = form['dep_id'][0]
			where_sql.append("sp.dep_name = %s" %(department))
				
	
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
			
		
			
	
		
	
			
		self.cr.execute('''
					
		SELECT
			   
		sm.product_qty as cons_qty,
		sm.price_unit as cons_rate,
		sm.name as cons_item,
		uom.name as cons_uom,
		sp.name as cons_no,
		sp.date as cons_date,
		sp_user.login AS user_name
	
		
		
		FROM stock_picking sp	
		
		join stock_move sm on (sm.picking_id = sp.id)
		left join product_uom uom on (sm.product_uom = uom.id)
		left join res_users sp_user on (sp.user_id = sp_user.id)
		
	
		where sp.type=%s and sp.state=%s and sp.date >=%s and sp.date <=%s'''+ where_sql + '''
		order by sp.date , sp.name ''',('internal','done',form['date_from'],form['date_to']))		   
			   
		data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
		
		if data:
			data_renew = [] 
			
			sub_tot = 0.00
			gr_tot = 0.00
			for position1, item1 in enumerate(data):
				print"pos,it",position1, item1
				data_renew.append({'cons_no':item1['cons_date'],'type':2})
				data_renew.append(item1)
				
				item1['cons_date'] = " "
				sub_tot = item1['cons_rate']
				remove_item_list = []
				for position2, item2 in enumerate(data):
					print"pos,it,,,,,,,,,,,,,,,,,,,,,,,",position2, item2
					if position1 != position2:
						if item1['cons_no'] == item2['cons_no']: 
							item2['cons_date'] = " "
							item2['cons_no'] = " "
							
							data_renew.append(item2)
							remove_item_list.append(item2)
							
							sub_tot += item2['cons_rate'] 
													
				
				data_renew.append({'cons_item': 'Sub Total', 'sub_tot': sub_tot,})		   
				gr_tot += sub_tot   
				for entry in remove_item_list:
					data.remove(entry)
			data_renew.append({'cons_item': 'Grand Total', 'sub_tot': gr_tot,})				  
			return data_renew 
			
		else:
			
			print "No Data"		   

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
  

report_sxw.report_sxw('report.consumption.details.report', 'stock.picking', 
			'addons/kg_store_reports/report/consumption_details_report.rml', 
			parser=consumption_details_report, header = False)
			
