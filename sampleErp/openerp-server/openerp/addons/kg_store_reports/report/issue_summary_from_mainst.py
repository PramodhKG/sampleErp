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

class issue_summary_from_mainst(report_sxw.rml_parse):
	
	_name = 'issue.summary.from.mainst'
	_inherit='stock.picking'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(issue_summary_from_mainst, self).__init__(cr, uid, name, context=context)
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
		
		"""
		if form['dep_id']:
			for ids1 in form['dep_id']:
				where_sql.append("sp.dep_name = %s"%(ids1))
				"""
		
		if form['dep_id']:
				dep_id = form['dep_id']
				where_sql.append("sp.dep_name= '%s' "%(dep_id[0]))
				
		if form['product_type']:
				where_sql.append("pt.type= '%s' "%form['product_type'])
		
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
			print "where_sql -------------------------", where_sql
		else:
			where_sql=''
		self.cr.execute('''
		
			  SELECT			  
			  sp.id AS sp_id,
			  sp.type AS type,
			  to_char(sp.date,'dd/mm/yyyy') AS date,
			  sp.name AS iss_number,
			  dep.dep_name AS dep_name,
			  sm.name AS product_name,
 			  uom.name AS uom,
			  sm.po_to_stock_qty AS qty,
			  sm.id AS sm_id,
			  sm.price_unit AS rate
			  			  
			  FROM  stock_picking sp

			  JOIN stock_move sm ON (sm.picking_id=sp.id)
			  JOIN kg_depmaster dep ON (dep.id=sp.dep_name)
			  JOIN product_uom uom ON (uom.id=sm.product_uom)
			  JOIN product_product prd ON (prd.id=sm.product_id)
			  JOIN product_template pt ON (pt.id=prd.product_tmpl_id)

			  where sp.type=%s and sp.state=%s and sp.date >=%s and sp.date <=%s'''+ where_sql + '''
			   order by sp.name,sp.date''',('out','done',form['date_from'],form['date_to']))
			   
		print "where_sql --------------------------->>>", where_sql
		data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
		
		gr_total = 0.0
		for sp in data:
			if sp['rate'] is None:
				sp['rate'] = 0.0
			else:
				sp['rate'] = sp['rate']
				
			val = sp['qty'] * sp['rate']
			gr_total += val
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
  

report_sxw.report_sxw('report.issue.summary.from.mainst', 'stock.picking', 
			'addons/kg_store_reports/report/issue_summary_from_mainst.rml', 
			parser=issue_summary_from_mainst, header = False)
			
			
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
		
	
					
					
