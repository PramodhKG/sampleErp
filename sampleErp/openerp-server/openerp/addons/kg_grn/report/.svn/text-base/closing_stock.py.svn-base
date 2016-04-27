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

class dep_issue_register(report_sxw.rml_parse):
	_name = 'report.dep.issue.register'
	_inherit='stock.picking'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(dep_issue_register, self).__init__(cr, uid, name, context=context)
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
		"""
	   Write sql or orm queries to get detail as a list of dict
		"""
		where_sql = []
		
		if form['supplier']:
			for ids1 in form['supplier']:
				where_sql.append("sp.partner_id = %s"%(ids1))
		
		if form['product_type']:
				where_sql.append("pt.type= '%s' "%form['product_type'])
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
		self.cr.execute('''
		
			  SELECT distinct on (sm.id)			  
			  sp.id AS sp_id,
			  sp.type AS type,
			  to_char(sp.date,'dd/mm/yyyy') AS date,
			  sp.name AS iss_number,
			  dep.dep_name AS dep_name,
			  sm.name AS product_name,
 			  uom.name AS uom,
			  sm.po_to_stock_qty AS qty,
			  sm.id AS sm_id,
			  sm.price_unit AS rate,
			  sm.picking_id AS sm_sp_id,
			  out.name AS out_type,
			  line.indent_id AS indent,
			  ind.name AS dp_name,
			  to_char(ind.date, 'dd/mm/yyyy') AS dp_date,
			  sp.user_id AS user_id,
			  lot.price_unit AS rate
			  			  
			  FROM  stock_picking sp

			  JOIN stock_move sm ON (sm.picking_id=sp.id)
			  JOIN kg_depmaster dep ON (dep.id=sp.dep_name)
			  JOIN product_uom uom ON (uom.id=sm.product_uom)
			  JOIN product_product prd ON (prd.id=sm.product_id)
			  JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
			  JOIN kg_outwardmaster out ON (out.id = sp.outward_type)
			  JOIN kg_depindent_line line ON (line.id = sm.depindent_line_id)
			  JOIN kg_depindent ind ON (ind.id = line.indent_id)
			  JOIN kg_out_grn_lines out_grn ON(out_grn.grn_id=sm.id)
			  JOIN stock_production_lot lot ON(lot.id=out_grn.lot_id) 

			  where sp.type=%s and sp.state=%s and sp.date >=%s and sp.date <=%s'''+ where_sql + '''
			   order by sm.id''',('out','done',form['date_from'],form['date_to']))
			   
		print "where_sql --------------------------->>>", where_sql
		data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data		
		gr_total = 0.0
		lot_obj = self.pool.get('stock.production.lot')
		sp = False
		for sp in data:
			user_id = sp['user_id']
			user = self.pool.get('res.users').browse(self.cr, self.uid,user_id)
			name = user.name
			sp['user_name'] = name
			print "sp['qty'] :::::::", sp['qty'] , "sp['rate'] :::::", sp['rate']
			if sp['rate'] is None:
				sp['rate'] = 0.0
			else:
				sp['rate'] = sp['rate']
				
			val = sp['qty'] * sp['rate']
			gr_total += val
			"""
			print "sp ^^^^^^^^^^^^^^^^^^^^^^^^^^^", sp['sp_id']
			move_id = self.pool.get('stock.move').search(self.cr, self.uid,
					[( 'picking_id','=',sp['sp_id'])])
			#print "move_id MMMMMMMMMMM ^^^^^^^^^^^^^^^^^^^^^^^^^", move_id
			if len(move_id) != 1:
				tot = 0.0
				print "GRN WISE TOTAL ISSSSSSSSSSSSSssss", move_id
				for move in move_id:
					move_rec = self.pool.get('stock.move').browse(self.cr,self.uid,move)
					print "move_rec ::::::::::::::::::::::::", move_rec
					tot += move_rec.po_to_stock_qty * move_rec.price_unit
					print "total amount $$$$$$$$$$$$$$$$$", tot
				
			else:
				print "COOOOOOOOOOOOOOOOOOOOOOOOOlllllllll"
				"""
					
		sp['total'] = gr_total
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
  

report_sxw.report_sxw('report.dep.issue.register', 'stock.picking', 
			'addons/kg_grn/report/dep_issue_register.rml', 
			parser=dep_issue_register, header = False)
			
			
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
		
	
					
					
