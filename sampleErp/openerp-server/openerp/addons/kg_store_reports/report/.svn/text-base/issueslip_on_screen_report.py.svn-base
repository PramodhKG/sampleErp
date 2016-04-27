import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler


class issueslip_on_screen_report(report_sxw.rml_parse):
	print "issueslip_on_screen_report class called.....from KGGGGGGGGGG......................"
	def __init__(self, cr, uid, name, context):
		super(issueslip_on_screen_report, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({'time': time})

report_sxw.report_sxw('report.issueslip.on.screen.report','stock.picking','addons/kg_grn/report/issueslip_on_screen_report.rml',parser=issueslip_on_screen_report,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

