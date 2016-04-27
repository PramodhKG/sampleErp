import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale
from datetime import date
import datetime

class closing_stock_report(report_sxw.rml_parse):
	
	_name = 'closing.stock.report'
	_inherit='stock.picking'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(closing_stock_report, self).__init__(cr, uid, name, context=context)
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

			   
			   where sm.product_qty != 0 and sm.state=%s and sm.move_type =%s and sm.date <=%s'''+ where_sql + major + product + pro_type +'''
			   group by sm.product_id''',('done',lo_type,form['date']))
				   
			   
		data=self.cr.dictfetchall()
		print "in_data ::::::::::::::=====>>>>", data
		
		data.sort(key=lambda data: data['in_pro_id'])
		print "data_sort ------------------------>>>.........", data
		
		gr_total=0.0
		gr_total1=0.0
		for item in data:
			move_obj = self.pool.get('stock.move')
			
			out_id = move_obj.search(self.cr, self.uid,
					 [('product_id','=',item['in_pro_id']),('move_type','=','out'),('state','=','done')])
			print "out_id......................",out_id
			
			if out_id:
				for i in out_id:
					out_rec = move_obj.browse(self.cr, self.uid,i)
					if out_rec.expiry_date != False:
						item['exp_date'] = out_rec.expiry_date
					if out_rec.batch_no != False:
						item['batch_no'] = out_rec.batch_no
					else:
						pass
					
			if lo_type == 'out':			
				product_id = item['in_pro_id']
				in_qty = item['in_qty']
				pro_rec = self.pool.get('product.product').browse(self.cr,self.uid,product_id)
				item['product_name'] = pro_rec.name
				item['uom'] = pro_rec.uom_id.name	   
				out_date = "'"+form['date']+"'"
				out_sql = """ select src_id as src_id,product_id as product_id,sum(product_qty) as product_qty from stock_move 
				where product_id=%s and move_type='cons' and state='done' and date <=%s group by src_id,product_id """%(product_id,out_date)
				self.cr.execute(out_sql)			
				out_data = self.cr.dictfetchall()
				print "out_data...........................", out_data
				cons_id = 0
				cons_qty = 0
				if out_data:
					out_qty = [d['product_qty'] for d in out_data if 'product_qty' in d]
					print "product_id................",product_id
					print "in_qty.................",in_qty
					print "out_qty.................",out_qty
					
					for out in out_qty:
						cons_qty += out
					
					print "cons_qty.....................",cons_qty
					close_qty = in_qty - cons_qty
					src_id = [s['src_id'] for s in out_data if 'src_id' in s]
					print "src_id....................",src_id
				else:
					close_qty = in_qty	  
					
				item['close_qty'] = close_qty
				cons_id = src_id
				print "pro_qty..............item['pro_qty']..........", item['close_qty']
				
				####
				total = 0
				value=0
				qty=0
				if item['close_qty']:
					price = 0
					if out_data:
						for out in out_data:
							
							print "consssssssssssssssssssssssssssssssssssssssss"
							
							cons_src_id = out['src_id']
							con_qty = out['product_qty']
							
							print "con_qty.....................",con_qty
							
							
							
							
							
							out_move_id=move_obj.search(self.cr,self.uid,[('product_id','=',product_id),('move_type','=','out'),
							('id','=',cons_src_id),('state','=','done')])
							print "out_move_id...........................",out_move_id
							out_move_rec=move_obj.browse(self.cr,self.uid,out_move_id[0])
							pro_name=out_move_rec.product_id.name
							print "product_name............................",pro_name
							print "out_move_rec.product_qty.....................",out_move_rec.product_qty
							close_qtty = out_move_rec.product_qty - con_qty
							print "close_qtty.....................",close_qtty
							out_price = close_qtty * out_move_rec.price_unit
							print "out_price............................",out_price
							price += out_price
						
					else:
						move_id=move_obj.search(self.cr,self.uid,[('product_id','=',product_id),('move_type','=','out'),
						('state','=','done')])
						if move_id:
							print "outtttttttttttttttttttttttttttttttttttttttt"
							total = 0
							value=0
							qty=0
							for j in move_id:
								move_rec=move_obj.browse(self.cr,self.uid,j)
								pro_name=move_rec.product_id.name
								print "pro_name........................",pro_name
								move_product_qty =move_rec.product_qty
								print "move_product_qty......................",move_product_qty
								pro_price=move_rec.price_unit
								print "move_pro_price......................",pro_price
								
								
								if pro_price:
									out_price=move_product_qty * pro_price
									print "out_price......................",out_price
								else:
									out_price = 0
							
								price += out_price
							
					value += price
					print "value...............................",value
				item['closing_value'] = value
									

							
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
  

report_sxw.report_sxw('report.closing.stock.wizard', 'stock.picking', 
			'addons/kg_store_reports/report/closing_stock_report.rml', 
			parser=closing_stock_report, header = False)
			
			
