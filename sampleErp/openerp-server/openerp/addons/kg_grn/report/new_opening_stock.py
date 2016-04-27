import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale

class new_opening_stock(report_sxw.rml_parse):
	
	_name = 'new.opening.stock'
	_inherit='stock.picking'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(new_opening_stock, self).__init__(cr, uid, name, context=context)
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
			ids = form['location_dest_id'][0]
			where_sql.append("sm.location_dest_id = %s" %(ids))
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
			print "where_sql -------------------------", where_sql
		else:
			where_sql=''
		self.cr.execute('''		
		
		  SELECT distinct on (sm.product_id)		  			
			sm.product_id as pro_id,
			sm.product_qty as pro_qty
			
			FROM stock_move sm
			
						
			where sm.move_type=%s and sm.state=%s and sm.date >=%s and sm.date <=%s'''+ where_sql + '''
			order by sm.product_id''',('dummy','done',form['date_from'],form['date_to']))		   
			   
		data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
		pro_obj = self.pool.get('product.product')
		uom_obj = self.pool.get('product.uom')
		lot_obj = self.pool.get('stock.production.lot')
		gr_total = 0.0
		if data:			
			for item in data:
				pro_id = item['pro_id']
				pro_rec = pro_obj.browse(self.cr, self.uid,pro_id)
				print "pro_id <><><><><><><><><><><><><><>", pro_id
				lot_pro_ids = lot_obj.search(self.cr, self.uid,[( 'product_id','=',pro_id),
										('pending_qty','>',0),('price_unit','!=',0)])
				print "lot_pro_ids ---------============>>>", lot_pro_ids
				op_val = 0.0
				if len(lot_pro_ids) != 1:
					for ids in lot_pro_ids:
						lot_rec = lot_obj.browse(self.cr, self.uid, ids)
						val = lot_rec.pending_qty * lot_rec.price_unit
						op_val += val
				else:
					lot_rec = lot_obj.browse(self.cr, self.uid, lot_pro_ids[0])
					val = lot_rec.pending_qty * lot_rec.price_unit
					op_val += val
				item['product'] = pro_rec.name
				item['op_val'] = op_val
				item['uom'] = pro_rec.uom_id.name
				item['qty'] = pro_rec.qty_available
				gr_total += op_val
				item['gr_total'] = gr_total
			return data
		else:
			print "data not found"
			

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
  

report_sxw.report_sxw('report.new.opening.stock', 'stock.picking', 
			'addons/kg_grn/report/new_opening_stock.rml', 
			parser=new_opening_stock, header = False)
			
			
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
		
	
					
					
