# -*- coding: utf-8 -*-
##############################################################################
#	
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.	 
#
##############################################################################

import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler

class email_purchase_order(report_sxw.rml_parse):
	print "email_purchase_order class called.....from KGGGGGGGGGG......................"
	
	def __init__(self, cr, uid, name, context):
		super(email_purchase_order, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
			})
		self.context = context				

report_sxw.report_sxw('report.email.purchase.order','purchase.order','addons/kg_purchase_order/report/email_purchase_order.rml',parser=email_purchase_order,header=False)


