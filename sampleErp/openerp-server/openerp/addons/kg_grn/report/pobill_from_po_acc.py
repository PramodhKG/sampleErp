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

class pobill_from_po_acc(report_sxw.rml_parse):
	
	_name = 'report.pobill.from.po.acc'
	_inherit='stock.picking'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(pobill_from_po_acc, self).__init__(cr, uid, name, context=context)
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
		partner = []
		
		if form['supplier']:
			for ids1 in form['supplier']:
				partner.append("inv.partner_id = %s"%(ids1))
		
		if form['product_type']:
				where_sql.append("ptem.type= '%s' "%form['product_type'])
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
			
		if partner:
			partner = 'and ('+' or '.join(partner)
			partner =  partner+')'
		else:
			partner = ''
			
		self.cr.execute('''
		
			  SELECT 
			  inv.id AS inv_id,
			  inv.type AS type,
			  to_char(inv.date_invoice,'dd/mm/yyyy') AS date,
			  inv.name AS inv_no,
			  inv.amount_total AS total,
			  inv.supplier_invoice_number AS su_inv,
			  to_char(inv.sup_inv_date, 'dd/mm/yyyy') AS sup_date,
			  inv.comment AS remark,
			  part.name AS su_name,
			  confuser.login AS username,
			  appruser.login AS approveuser,
			  pick.name AS grnno,
			  to_char(pick.date, 'dd/mm/yyyy') AS grndate,
			  to_char(inv.inv_confirm_date, 'dd/mm/yyyy') AS confirmdate,
			  to_char(inv.inv_approve_date, 'dd/mm/yyyy') AS approvedate,
			  po.bill_type AS pay		 
			  			  
			  FROM  account_invoice inv

			  JOIN res_partner part ON (part.id = inv.partner_id)
			  JOIN purchase_order po ON(po.id = inv.po_id)
			  JOIN res_users confuser ON (inv.confirmed_by = confuser.id)
			  JOIN res_users appruser ON (inv.approved_by = appruser.id)
			  JOIN stock_picking pick ON (pick.id = inv.grn_id)


			  where inv.type=%s and inv.state=%s and
			  inv.inv_approve_date >=%s and inv.inv_approve_date <=%s'''+ where_sql + partner +'''
			   order by inv.name''',('in_invoice','open',form['date_from'],form['date_to']))
			   
		print "where_sql --------------------------->>>", where_sql
		data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
		gr_total = 0.0
		if data:				
			for inv in data:
				val = inv['total'] 
				gr_total += val
				
			inv['gr_total'] = gr_total
			return data
		else:
			print "No Data Cool"				   

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
  

report_sxw.report_sxw('report.pobill.from.po.acc', 'stock.picking', 
			'addons/kg_grn/report/pobill_from_po_acc.rml', 
			parser=pobill_from_po_acc, header = False)
			
			
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
