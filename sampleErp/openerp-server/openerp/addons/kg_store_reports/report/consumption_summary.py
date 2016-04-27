import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale

class consumption_summary(report_sxw.rml_parse):
	
	_name = 'consumption.summary'
	_inherit='stock.picking'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(consumption_summary, self).__init__(cr, uid, name, context=context)
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
			for ids1 in form['dep_id']:
				where_sql.append("sp.dep_name = %s"%(ids1))	
				
		if form['location_dest_id']:
			location = form['location_dest_id'][0]
			loc.append("sm.location_dest_id = %s" %(location))
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
			
		if loc:
			loc = ' and '+' or '.join(loc)
		else:
			loc=''
			
		location_rec = self.pool.get('stock.location').browse(self.cr,self.uid,location)
		print "location_rec.........................", location_rec, location_rec.location_type
		
		if location_rec.location_type == 'main':
			
			
			self.cr.execute('''
						
			SELECT
				   
			sum(sm.product_qty * sm.price_unit) as val,
			sp.dep_name as dep_id,
			dep.dep_name as dep
			
			FROM stock_picking sp	
			join stock_move sm on (sm.picking_id = sp.id)
			join kg_depmaster dep on(dep.id=sp.dep_name)
		
			where sp.type=%s and sp.state=%s and sp.date >=%s and sp.date <=%s'''+ where_sql + '''
			group by sp.dep_name,dep.dep_name''',('out','done',form['date_from'],form['date_to']))		   
				   
			data=self.cr.dictfetchall()
			print "data ::::::::::::::=====>>>>", data
			cons_val = 0.0
			ret_val = 0.0
			net_val = 0.0
			total = 0.0
			#test = reduce(lambda x, y : x+y, data['val'])
			#print "test lambda ---------------->>>", test
			for item in data:
				
				total += item['val']
				item['total'] = total		
				
		else:
			
			
			self.cr.execute('''
							
			SELECT
					   
			sum(sm.product_qty * sm.price_unit) as val,
			sp.dep_name as dep_id,
			dep.dep_name as dep
			
			FROM stock_picking sp	
			join stock_move sm on (sm.picking_id = sp.id)
			join kg_depmaster dep on(dep.id=sp.dep_name)
					
			where sp.type=%s and sp.state=%s and sp.date >=%s and sp.date <=%s'''+ where_sql + '''
			group by sp.dep_name,dep.dep_name''',('internal','done',form['date_from'],form['date_to']))		   
					   
			data=self.cr.dictfetchall()
			print "data ::::::::::::::=====>>>>", data
			cons_val = 0.0
			ret_val = 0.0
			net_val = 0.0
			total = 0.0
			#test = reduce(lambda x, y : x+y, data['val'])
			#print "test lambda ---------------->>>", test
			for item in data:
				
				total += item['val']
				item['total'] = total		
			
			
					
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
  

report_sxw.report_sxw('report.consumption.summary', 'stock.picking', 
			'addons/kg_store_reports/report/consumption_summary.rml', 
			parser=consumption_summary, header = False)
			
			
# GRN NO and Supplier should be blank if a picking have more than one line
"""
new_data=[]
count = 0
for pos1, item1 in enumerate(data):
	delete_items = []
	match_found = False
	for pos2, item2 in enumerate(data):
		if not pos1 == pos2:
			if item1['grn_number'] == item2['grn_number'] and item1['part_name'] == item2['part_name']:
				match_found = True
				if count == 0:
					new_data.append(item1)
					count = count + 1
				item2_2 = item2
				item2_2['grn_number'] = ''
				item2_2['part_name'] = ''
				item2_2['date'] = ''
				new_data.append(item2_2)
				delete_items.append(item2)
	if not match_found:
		new_data.append(item1)
	for ele in delete_items:
		data.remove(ele)
data = new_data
for d in data:
	seq = 0.0
	if d['grn_number'] != '' and d['part_name'] != '':
		seq = seq + 1
		d['sequence'] = seq
		"""
		
	
					
					
