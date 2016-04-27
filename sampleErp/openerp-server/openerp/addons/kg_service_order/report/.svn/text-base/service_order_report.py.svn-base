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

class service_order_report(report_sxw.rml_parse):
	print "purchase_order_report class called.....from KGGGGGGGGGG......................"
	def __init__(self, cr, uid, name, context):
		super(service_order_report, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({'time': time})

report_sxw.report_sxw('report.service.order.report','kg.service.order','addons/kg_service_order/report/service_order_report.rml',parser=service_order_report,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

