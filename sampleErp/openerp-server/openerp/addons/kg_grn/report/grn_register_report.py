import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class grn_register_report(report_sxw.rml_parse):
	
	_name = 'report.grn.register.report'
	_inherit='stock.picking'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(grn_register_report, self).__init__(cr, uid, name, context=context)
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
		partner = []
		product=[]
		
		if form['supplier']:
			for ids1 in form['supplier']:
				partner.append("sp.partner_id = %s"%(ids1))
		
		if form['product']:
			for ids2 in form['product']:
				product.append("pol.product_id = %s"%(ids2))
		
		if form['product_type']:
				where_sql.append("pt.type= '%s' "%form['product_type'])
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
			
		if partner:
			partner = 'and ('+' or '.join(partner)
			partner =  partner+')'
		else:
			partner = ''
			
		if product:
			product = 'and ('+' or '.join(product)
			product =  product+')'
		else:
			product = ''
		
		print "where_sql --------------------------->>>", where_sql	
		print "partner --------------------------->>>", partner
		print "product------------------------------>",product
		
		self.cr.execute('''
		
			  SELECT 
			  sp.id AS sp_id,
			  to_char(sp.date,'dd/mm/yyyy') AS date,
			  sp.name AS grn_number,
			  sp.grn_total As grn_tot,
			  sp.dc_no AS dc_no,
			  to_char(sp.dc_date,'dd/mm/yyyy') AS dc_date,			   
			  sp.origin AS po_no,
			  sp.user_id AS user_id,
			  to_char(po.date_order,'dd/mm/yyyy') AS po_date,
			  part.name AS part_name,
			  part.street as str1,
			  ct.name as city,
			  part.zip as zip,
		      st.name as state,
			  coun.name as country,
			  sm.name AS product_name,
			  sm.po_to_stock_qty AS qty,
			  to_char(sm.expiry_date,'dd/mm/yyyy') AS ex_date,
			  uom.name AS uom,
			  pol.id as pol_id,
			  pol.product_qty AS po_qty,
			  pol.price_unit AS po_price,
			  pol.product_id As product,
			  pol.kg_discount_per As discount,
			  pol.kg_disc_amt_per As amtdiscount,
			  po.add_text as address,		  
			  sm.id AS sm_id,
			  sm.price_unit As cost_price,
			  inw.name AS inward_type,
			  depl.qty AS ind_qty,			
			  dep.dep_name AS dep
			  
			  FROM  stock_picking sp

			  JOIN res_partner part ON (part.id=sp.partner_id)
			  join res_country_state st on(st.id=part.state_id)
			  left join res_city ct on(ct.id=part.city)
		      join res_country as coun on(coun.id=part.country_id)
			  JOIN stock_move sm ON (sm.picking_id=sp.id)
			  JOIN purchase_order po ON (po.id=sp.po_id)
			  JOIN purchase_order_line pol ON (pol.id = sm.purchase_line_id)
			  JOIN kg_inwardmaster inw ON (inw.id = sp.inward_type)
			  JOIN product_uom uom ON (uom.id=sm.product_uom)
			  JOIN product_product prd ON (prd.id=sm.product_id)
			  JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
			  JOIN purchase_requisition_line prl ON (prl.id = pol.pi_line_id)
			  JOIN kg_depindent_line depl ON (depl.id = prl.depindent_line_id)
			  JOIN kg_depindent ind ON (ind.id = depl.indent_id)
			  JOIN kg_depmaster dep ON (dep.id = ind.dep_name)			  

			  where sp.type = %s and (sp.state = %s or sp.state= %s) and sp.date >=%s and sp.date <=%s'''+ where_sql + partner + product +'''
			   order by sp.name,sp.date''',('in', 'done', 'inv', form['date_from'],form['date_to']))
		
		data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
		
		# GRN NO and Supplier should be blank if a GRN have more than one line
		new_data = []
		count = 0
		gr_total = 0.0
		pol_obj = self.pool.get('purchase.order.line')
		for pos1, item1 in enumerate(data):
			delete_items = []
			user_id = item1['user_id']
			user = self.pool.get('res.users').browse(self.cr, self.uid,user_id)
			
			name = user.name
			item1['user_name'] = name
			if item1['grn_tot']:
				amount = item1['grn_tot']
			else:
				amount = 0
		
			gr_total += amount
			item1['total'] = gr_total
			pol_rec = pol_obj.browse(self.cr, self.uid,item1['pol_id'])
			taxes = pol_rec.taxes_id
			if taxes and len(taxes) !=1:				
				tax_name = []
				for tax in taxes:
					name = tax.name
					tax_name.append(name)
					a = (', '.join('"' + item + '"' for item in tax_name))
					tax = [ item.encode('ascii') for item in ast.literal_eval(a) ]
					po_tax = ', '.join(tax)
					item1['tax'] = po_tax
			else:
				if taxes:						
					po_tax = taxes[0].name
					item1['tax'] = po_tax			
			
			for pos2, item2 in enumerate(data):
				if not pos1 == pos2:
					if item1['sp_id'] == item2['sp_id'] and item1['part_name'] == item2['part_name']:
						
												
						if count == 0:
							new_data.append(item1)
							print "new_data -------------------------------->>>>", new_data
							count = count + 1
						item2_2 = item2
						item2_2['grn_number'] = ''
						item2_2['part_name'] = ''
						item2_2['str1']=''
						item2_2['city']=''
						item2_2['zip']=''
						item2_2['state']=''
						item2_2['date'] = ''
						item2_2['grn_tot']=''
						
						new_data.append(item2_2)
						print "new_data 2222222222222222", new_data
						delete_items.append(item2)
						print "delete_items _____________________>>>>>", delete_items
				else:
					print "Few GRN have one line"
					
		return data	

		"""
		for pick in data:
			user_id = pick['user_id']
			user = self.pool.get('res.users').browse(self.cr, self.uid,user_id)
			name = user.name
			pick['user_name'] = name
			print "pick <><><><><><><><><><><><><<><><", pick
			move_id = self.pool.get('stock.move').search(self.cr, self.uid,
					[( 'picking_id','=',pick['sp_id'])])
			print "move_id ---------------------------->>", move_id
			if len(move_id) != 1:			
				print "GRN WISE TOTAL ISSSSSSSSSSSSSssss", move_id
				tot = 0.0
				for move in move_id:
					move_rec = self.pool.get('stock.move').browse(self.cr,self.uid,move)
					print "move_rec .QTY::::::::::::::::::::::::", move_rec.po_to_stock_qty
					print "move_rec .Price::::::::::::::::::::::::", move_rec.price_unit
					tot += move_rec.po_to_stock_qty * move_rec.price_unit
				pick['grn_total'] = tot
				print "total amount $$$$$$$$$$$$$$$$$", pick['grn_total']
			else:
				pick['grn_total'] = 0.0
								"""
		
		
			   

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
  

report_sxw.report_sxw('report.grn.register.report', 'stock.picking', 
			'addons/kg_grn/report/grn_register_report.rml', 
			parser=grn_register_report, header = False)
