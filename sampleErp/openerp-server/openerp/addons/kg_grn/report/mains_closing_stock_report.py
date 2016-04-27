import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale
from datetime import date
import datetime

class mains_closing_stock_report(report_sxw.rml_parse):
	
	_name = 'mains.closing.stock.report'
	_inherit='stock.picking'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(mains_closing_stock_report, self).__init__(cr, uid, name, context=context)
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
		major = []
		product=[]
		pro_type=[]
		
		if form['location_dest_id']:
			location = form['location_dest_id'][0]
			where_sql.append("sm.location_dest_id = %s" %(location))
		
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
			
		else:
			where_sql=''
			
		if form['major_name']:
			majorwise = form['major_name'][0]
			major.append("pt.categ_id = %s" %(majorwise))
		
		if major:
			major = ' and '+' or '.join(major)
			
		else:
			major=''
			
		if form['product']:
			for ids2 in form['product']:
				product.append("sm.product_id = %s"%(ids2))	
				
		if product:
			product = ' and '+' or '.join(product)
		else:
			product=''
			
		if form['product_type']:
				pro_type.append("pt.type= '%s' "%form['product_type'])
				
		if pro_type:
			pro_type = ' and '+' or '.join(pro_type)
		else:
			pro_type=''
			
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
					sum(product_qty) as in_qty
					
			   FROM stock_move sm
			   
			   JOIN product_template pt ON (pt.id=sm.product_id)
			   JOIN product_category pc ON (pc.id=pt.categ_id)

			   
			   where sm.product_qty != 0 and sm.state=%s and sm.move_type =%s and sm.date <=%s '''+ where_sql + major + product + pro_type +'''
			   group by sm.product_id''',('done',lo_type,form['date']))
				   
			   
		data=self.cr.dictfetchall()
		print "in_data ::::::::::::::=====>>>>", data
		
		gr_total=0.0
		gr_total1=0.0
		for item in data:
			lot_obj = self.pool.get('stock.production.lot')
			lot_id = lot_obj.search(self.cr, self.uid,[('product_id','=',item['in_pro_id']),('lot_type','=','in')])
			print "exp____lot_id",lot_id
			if lot_id:
				for lot in lot_id:
					lot_rec = lot_obj.browse(self.cr,self.uid,lot)
					print "exp_product name",lot_rec.product_id.name
					item['exp_date']=lot_rec.expiry_date
					item['batch_no']=lot_rec.batch_no
						
			if lo_type == 'in':			
				product_id = item['in_pro_id']
				in_qty = item['in_qty']
				
				pro_rec = self.pool.get('product.product').browse(self.cr,self.uid,product_id)
				item['product_name'] = pro_rec.name
				item['uom'] = pro_rec.uom_id.name				
				
				out_date = "'"+form['date']+"'"
				
				out_sql = """ select product_id,sum(product_qty) from stock_move where product_id=%s and move_type='out' and state='done' and date <=%s and location_id != 254 group by product_id """%(product_id,out_date)
				self.cr.execute(out_sql)			
				out_data = self.cr.dictfetchall()
				print "out_data...........................", out_data
				if out_data:
					out_qty = [d['sum'] for d in out_data if 'sum' in d]
					print "product_id................",product_id
					print "in_qty.................",in_qty
					print "out_qty.................",out_qty[0]
					op_qty = in_qty - out_qty[0]
					print "cl_qty..............",op_qty
				else:
					op_qty = in_qty		
					
				item['close_qty'] = op_qty
				print "op_qty.........yyyyyyyyyyyy.....item['op_qty']..........", item['close_qty']
				
				#####
				if item['close_qty']:
					spl_obj=self.pool.get('stock.production.lot')
					spl_id=spl_obj.search(self.cr,self.uid,[('product_id','=',product_id),('lot_type','=','in')])
					print "innnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"
							
					
					value=0
					qty=0
					for j in spl_id:
						spl_rec=spl_obj.browse(self.cr,self.uid,j)
						pro_name=spl_rec.product_id.name
						pend_qty=spl_rec.pending_qty
						product_qty =spl_rec.product_qty
						pro_price = spl_rec.price_unit
						if pend_qty > 0:
							pro_qty = pend_qty
							price=pro_qty*pro_price
						else:
							price = 0	
						
						
						value += price
					item['closing_value'] =value
										
		

		print "----------------------------->>>>",data
		
		data_renew = []
		val = 0.0
		val1 = 0.0
		for item in data:
			print "&&***&&&",item
			if item['close_qty'] > 0.0:
				val = item['closing_value']
				gr_total += val
				print "gr_total1.............",gr_total
				item['gr_total'] = gr_total
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
  

report_sxw.report_sxw('report.mains.closing.stock.report', 'stock.picking', 
			'addons/kg_grn/report/mains_closing_stock_report.rml', 
			parser=mains_closing_stock_report, header = False)
			
			
