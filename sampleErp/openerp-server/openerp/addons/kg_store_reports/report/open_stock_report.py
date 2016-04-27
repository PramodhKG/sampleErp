import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale
from datetime import date
import datetime

class open_stock_report(report_sxw.rml_parse):
	
	_name = 'open.stock.report'
	_inherit='stock.picking'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(open_stock_report, self).__init__(cr, uid, name, context=context)
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
		
		
		if form['location_dest_id']:
			location = form['location_dest_id'][0]
			where_sql.append("sm.location_dest_id = %s" %(location))
			
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
			print "where_sql -------------------------", where_sql
		else:
			where_sql=''
			
		print "date............"	, type(form['date'])
		location_rec = self.pool.get('stock.location').browse(self.cr,self.uid,location)
		print "location_rec.........................", location_rec, location_rec.location_type
		
		if location_rec.location_type == 'main':
			lo_type = 'in'
		else:
			lo_type = 'out'
		
		self.cr.execute('''		
		
			   SELECT  
					sm.product_id as in_pro_id,
					sum(product_qty) as in_qty,
					sum(price_unit) as in_price
					
			   FROM stock_move sm
			   
			  where sm.product_qty > 0 and sm.state=%s and sm.move_type =%s and sm.date <=%s'''+ where_sql +'''
			   group by sm.product_id''',('done','in',form['date']))
				   
			   
		data=self.cr.dictfetchall()
		print "in_data ::::::::::::::=====>>>>", data
		
		gr_tot=0.0
		value_tot=0.0
		pen_qty=0.0
		opening_val=0.0
		gr_total=0.0
		for item in data:			
			if lo_type == 'in':			
				product_id = item['in_pro_id']
				in_qty = item['in_qty']
				print "product_id.....................", product_id
				print "qty.........................", item['in_qty']
				pro_rec = self.pool.get('product.product').browse(self.cr,self.uid,product_id)
				item['product_name'] = pro_rec.name
				item['uom'] = pro_rec.uom_id.name				
				print "dateformatttttt", form['date']
				out_date = "'"+form['date']+"'"
				print "out date.................",out_date, type(out_date)
				out_sql = """ select product_id,sum(product_qty) from stock_move where product_id=%s and move_type='out' and state='done' and date <=%s group by product_id """%(product_id,out_date)
				self.cr.execute(out_sql)			
				out_data = self.cr.dictfetchall()
				print "out_data...........................", out_data
				if out_data:
					out_qty = [d['sum'] for d in out_data if 'sum' in d]
					print "val1111111111111111111", out_qty
					op_qty = in_qty - out_qty[0]
				else:
					op_qty = in_qty		
					
				item['op_qty'] = op_qty
				print "op_qty..............item['op_qty']..........", item['op_qty']
				
				##########
			
				spl_obj=self.pool.get('stock.production.lot')
				spl_id=spl_obj.search(self.cr,self.uid,[('product_id','=',product_id),('date','<=',form['date'])])
				
				print "spl_id...........................",spl_id
				
				value=0
				qty=0
				for j in spl_id:
					spl_rec=spl_obj.browse(self.cr,self.uid,j)
					pro_name=spl_rec.product_id.name
					pend_qty=spl_rec.pending_qty
					product_qty =spl_rec.product_qty
					if pend_qty > 0:
						pro_qty = pend_qty
					else:
						pro_qty = product_qty
					pro_price=spl_rec.price_unit
					print "produ_name,pro_qty,price_unit............",pro_name,pro_qty,pro_price
					price=pro_qty*pro_price
					print "price.............",price
					value += price
					item['opening_value'] =value
					print "value............",value
					qty += pro_qty
					item['open_qty']=qty
					print "item['open_qty']......",item['open_qty']
					gr_total += value
					print "gr_total.............",gr_total
					
					item['grand_total']=gr_total
					print "Grand Total.............",item['grand_total']
			else:
				product_id = item['in_pro_id']
				in_qty = item['in_qty']
				print "product_id.....................", product_id
				print "qty.........................", item['in_qty']
				pro_rec = self.pool.get('product.product').browse(self.cr,self.uid,product_id)
				item['product_name'] = pro_rec.name
				item['uom'] = pro_rec.uom_id.name			
				
				
				print "dateformatttttt", form['date']
				out_date = "'"+form['date']+"'"
				print "out date.................",out_date, type(out_date)
				out_sql = """ select product_id,sum(product_qty) from stock_move where product_id=%s and move_type='cons' and state='done' and date <=%s group by product_id """%(product_id,out_date)
				self.cr.execute(out_sql)			
				out_data = self.cr.dictfetchall()
				print "out_data...........................", out_data
				if out_data:
					out_qty = [d['sum'] for d in out_data if 'sum' in d]
					print "val1111111111111111111", out_qty
					op_qty = in_qty - out_qty[0]
				else:
					op_qty = in_qty		
					
				item['op_qty'] = op_qty
				print "op_qty..............item['op_qty']..........", item['op_qty']
				
				##########
			
				spl_obj=self.pool.get('stock.production.lot')
				spl_id=spl_obj.search(self.cr,self.uid,[('product_id','=',product_id),('date','<=',form['date'])])
				
				print "spl_id...........................",spl_id
				
				value=0
				qty=0
				for j in spl_id:
					spl_rec=spl_obj.browse(self.cr,self.uid,j)
					pro_name=spl_rec.product_id.name
					pend_qty=spl_rec.pending_qty
					product_qty =spl_rec.product_qty
					if pend_qty > 0:
						pro_qty = pend_qty
					else:
						pro_qty = product_qty
					pro_price=spl_rec.price_unit
					print "produ_name,pro_qty,price_unit............",pro_name,pro_qty,pro_price
					price=pro_qty*pro_price
					print "price.............",price
					value += price
					item['opening_value'] =value
					print "value............",value
					qty += pro_qty
					item['open_qty']=qty
					print "item['open_qty']......",item['open_qty']
					gr_total += value
					print "gr_total.............",gr_total
					
					item['grand_total']=gr_total
					print "Grand Total.............",item['grand_total']	
			
			
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
  

report_sxw.report_sxw('report.open.stock.wizard', 'stock.picking', 
			'addons/kg_grn/report/open_stock_report.rml', 
			parser=open_stock_report, header = False)
			
			
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
		
	
					
					
