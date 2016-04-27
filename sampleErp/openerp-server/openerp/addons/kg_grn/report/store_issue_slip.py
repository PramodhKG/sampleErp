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

class store_issue_slip(report_sxw.rml_parse):
	
	_name = 'report.store.issue.slip'
	_inherit='stock.picking'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(store_issue_slip, self).__init__(cr, uid, name, context=context)
		self.query = ""
		self.period_sql = ""
		self.localcontext.update( {
			'time': time,
			'get_filter': self._get_filter,
			'get_start_date':self._get_start_date,
			'get_end_date':self._get_end_date,
			'get_data':self.get_data,
			'get_stock_move':self.get_stock_move,
			'locale':locale,
		})
		self.context = context
		
	def get_data(self,form):
		res = {}
		"""
	   Write sql or orm queries to get detail as a list of dict
		"""
		where_sql = []
		
		if form['dep_id']:
			for ids1 in form['dep_id']:
				where_sql.append("sp.dep_name = %s"%(ids1))
						
		if where_sql:
			
			where_sql = 'and ('+' or '.join(where_sql)
			where_sql =  where_sql+')'
		else:
			where_sql = ''
			
		self.cr.execute('''
		
			  SELECT distinct on (sm.id)			  
			  sp.id AS sp_id,
			  to_char(sp.date,'dd/mm/yyyy') AS date,
			  sp.name AS iss_number,
			  dep.dep_name AS dep_name,
			  sm.name AS product_name,
 			  uom.name AS uom,
			  sm.po_to_stock_qty AS qty,
			  sm.id AS sm_id,
			  sm.price_unit AS rate,
			  line.indent_id AS indent,
			  ind.name AS dp_name,
			  to_char(ind.date, 'dd/mm/yyyy') AS dp_date,
			  sp.user_id AS user_id,
			  sp.note AS remark,
			  lot.id AS lot_id,
			  lot.price_unit AS grn_price
			  			  
			  FROM  stock_picking sp

			  JOIN stock_move sm ON (sm.picking_id=sp.id)
			  JOIN kg_depmaster dep ON (dep.id=sp.dep_name)
			  JOIN product_uom uom ON (uom.id=sm.product_uom)
			  JOIN product_product prd ON (prd.id=sm.product_id)
			  JOIN product_template pt ON (pt.id=prd.product_tmpl_id)
			  JOIN kg_depindent_line line ON (line.id = sm.depindent_line_id)
			  JOIN kg_depindent ind ON (ind.id = line.indent_id)
			  JOIN kg_out_grn_lines grn_out ON(grn_out.grn_id=sm.id)
			  JOIN stock_production_lot lot ON(lot.id=grn_out.lot_id)

			  where sp.type=%s and sp.state=%s and sp.date >=%s and sp.date <=%s'''+ where_sql + '''
			   ''',('out','done',form['date_from'],form['date_to']))
			   
		print "where_sql --------------------------->>>", where_sql
		data=self.cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
	
		for sp in data:
			user_id = sp['user_id']
			user = self.pool.get('res.users').browse(self.cr, self.uid,user_id)
			name = user.name
			sp['user_name'] = name
			pick_id = sp['sp_id']
			move_id = sp['sm_id']
			st_move = self.pool.get('stock.move').browse(self.cr, self.uid,move_id)
			print "st_move ----",st_move, "pick -id-------------", st_move.picking_id		
		
		return data
		
		
	def get_stock_move(self,data):
		move_data=[]
		stock_move_id = self.pool.get('stock.move').search(self.cr, self.uid,
						[('picking_id', '=', data)], context=None)
		print "stock_move_id ~~~~~~~~~~~~~~~~~~~~~~~~~~~~", stock_move_id
		
		move_browse = self.pool.get('stock.move').browse(self.cr, self.uid, stock_move_id)
		print "move_browse ~~~~~~~~~~~~~~~~~~~~~~~~~~~", move_browse
		total = 0.0
		for move in move_browse:			
			#sql = """ select lot_id from kg_out_grn_lines where grn_id=%s""" %(move.id)
			#self.cr.execute(sql)
			#move_data = self.cr.dictfetchall()
			#lot_id = move_data[0]['lot_id']			
			#lot_rec = self.pool.get('stock.production.lot').browse(self.cr, self.uid, lot_id)
			#price = lot_rec.price_unit
			tot_amt = move.po_to_stock_qty * move.price_unit
			total += tot_amt
			
			print "total.................>>>",total
			
			line ={
			'product':move.product_id.name,
			'prod_uom':move.product_uom.name,
			'prod_qty':move.po_to_stock_qty,
			'indent_no':move.depindent_line_id.indent_id.name,
			'indent_date':move.depindent_line_id.indent_id.date,
			'price':move.stock_rate,
			'total': total
			}
			move_data.append(line)
			print "move_data --------------------------------", move_data
		return move_data
				   

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
  

report_sxw.report_sxw('report.store.issue.slip', 'stock.picking', 
			'addons/kg_grn/report/store_issue_slip.rml', 
			parser=store_issue_slip, header = False)
			
