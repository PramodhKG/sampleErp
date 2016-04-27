# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2006 CamptoCamp
# Copyright (c) 2006-2010 OpenERP S.A
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale
from datetime import datetime, date
import ast


class po_pending_stm(report_sxw.rml_parse):
	
	_name = 'po.pending.stm'
	_inherit='purchase.order,purchase.order.line'

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(po_pending_stm, self).__init__(cr, uid, name, context=context)
		self.query = ""
		self.period_sql = ""
		self.localcontext.update( {
			'time': time,
			'get_filter': self._get_filter,
			'get_start_date':self._get_start_date,
			'get_end_date':self._get_end_date,
			'get_data':self.get_data,
			'locale':locale,
			#'get_data_line':self.get_data_line,

		})
		self.context = context
		
	def get_data(self,form):
		
		res = {}
		where_sql = []
		partner = []
		product = []
			
		if form['supplier']:
			for ids1 in form['supplier']:
				partner.append("po.partner_id = %s"%(ids1))
		
		if form['product_id']:
			for ids2 in form['product_id']:
				product.append("pol.product_id = %s"%(ids2))		
				

		if partner:
			partner = 'and ('+' or '.join(partner)
			partner =  partner+')'
			print "partner -------------------------->>>>", partner
		else:
			partner = ''
			
		if product:
			product = 'and ('+' or '.join(product)
			product =  product+')'
			print "product -------------------------->>>>", product
		else:
			product = ''

			
		self.cr.execute('''
		
			  SELECT
			  po.id AS po_id,
			  po.name AS po_no,
			  to_char(po.date_order,'dd/mm/yyyy') AS po_date,
			  po.date_order AS date,
			  po.note AS remark,
			  pol.id as pol_id,
			  pol.product_qty AS qty,
			  pol.pending_qty AS pending_qty,
			  pol.price_unit as rate,
			  pol.kg_discount_per as disc1,
			  pol.kg_disc_amt_per as disc2,		  
			  uom.name AS uom,
			  pt.name AS pro_name,
			  res.name AS su_name,
			  res.street as str1,
			  ct.name as city,
			  res.zip as zip,
		      st.name as state,
			  coun.name as country	  
			  			  
			  FROM  purchase_order po
			  			  
			  JOIN res_partner res ON (res.id=po.partner_id)
			  join res_country_state st on(st.id=res.state_id)
			  left join res_city ct on(ct.id=res.city)
		      join res_country as coun on(coun.id=res.country_id)
			  JOIN purchase_order_line pol ON (pol.order_id=po.id)
			  JOIN product_product prd ON (prd.id=pol.product_id)
			  JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
			  JOIN product_uom uom ON (uom.id=pol.product_uom)
			  

			  where pol.pending_qty > 0 and po.state=%s and pol.line_state != %s and po.date_order >=%s and po.date_order <=%s '''+ product + partner + '''
			  order by po.name''',('approved','cancel',form['date_from'],form['date_to']))
			   
		data=self.cr.dictfetchall()
		data.sort(key=lambda data: data['po_id'])
		#print "data ::::::::::::::=====>>>>", data										
		new_data = []
		count = 0
		pol_obj = self.pool.get('purchase.order.line')
		for pos1, item1 in enumerate(data):
			if item1['disc1'] == None:
				item1['disc1'] = 0.00
			else:
				item1['disc1'] = item1['disc1']
				
			if item1['disc2'] == None:
				item1['disc2'] = 0.00
			else:
				item1['disc2'] = item1['disc2']							
			delete_items = []
			po_no = item1['po_no']
			order_id = item1['po_id']
			po_date = item1['date']
			net = item1['qty'] * item1['rate']
			item1['net_total'] = net
			fmt = '%Y-%m-%d'
			from_date = po_date    
			to_date = date.today()
			to_date = str(to_date)
			d1 = datetime.strptime(from_date, fmt)
			d2 = datetime.strptime(to_date, fmt)
			daysDiff = str((d2-d1).days)
			print "daysDiff--------------->>", daysDiff
			item1['pending_days'] = daysDiff
			pol_rec = pol_obj.browse(self.cr, self.uid,item1['pol_id'])
			netamt1 = pol_rec.price_subtotal
			taxes = pol_rec.taxes_id
			item1['netamt'] = netamt1 
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
					if item1['po_id'] == item2['po_id'] and item1['su_name'] == item2['su_name']:												
						if count == 0:
							new_data.append(item1)
							count = count + 1
						item2_2 = item2
						item2_2['su_name'] = ''
						item2_2['str1'] = ''
						item2_2['zip'] = ''
						item2_2['city'] = ''
						item2_2['state'] = ''
						item2_2['country'] = ''
						item2_2['po_no'] = ''
						item2_2['po_date'] = ''
						new_data.append(item2_2)
						delete_items.append(item2)
				else:
					print "Few PO have one line"
					
		return data
		
	"""
	def get_data_line(self,data):
		
		line_data=[]
		print "data~~~~~~~~~~~~~~~~~~~~~~~~", data	
		po_line_id = self.pool.get('purchase.order.line').search(self.cr, self.uid,
						[('order_id', '=', data)], context=None)		
		po_line_browse = self.pool.get('purchase.order.line').browse(self.cr, self.uid, po_line_id)
		for po_line in po_line_browse:
			print "po_line____________________>>>>", po_line
			line ={
			
			'product':po_line.product_id.name,
			'prod_uom':po_line.product_uom.name,
			'order_qty':po_line.product_qty,
			'pending_qty':po_line.pending_qty,
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
		if data.get('form', False) and data['form'].get('date_from', False):
			return data['form']['date_from']
		return ''
		
	def _get_end_date(self, data):
		if data.get('form', False) and data['form'].get('date_to', False):
			return data['form']['date_to']
		return ''		   
  

report_sxw.report_sxw('report.po.pending.stm', 'purchase.order', 
			'addons/kg_po_reports/report/po_pending_stm.rml', 
			parser=po_pending_stm, header = False)
"""		
for po in data:
			po_no = po['po_no']
			order_id = po['po_id']
			po_date = po['date']
			fmt = '%Y-%m-%d'
			from_date = po_date    
			to_date = date.today()
			to_date = str(to_date)
			print "from_date ::::::::::", from_date, "to_date  :::::::::", to_date
			d1 = datetime.strptime(from_date, fmt)
			d2 = datetime.strptime(to_date, fmt)
			daysDiff = str((d2-d1).days)
			print "daysDiff--------------->>", daysDiff
			po['pending_days'] = daysDiff
		
		return data
		"""
