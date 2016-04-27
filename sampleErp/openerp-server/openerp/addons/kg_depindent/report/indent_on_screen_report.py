import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler
import netsvc


class indent_on_screen_report(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(indent_on_screen_report, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({'time': time})

report_sxw.report_sxw('report.indent.on.screen.report','kg.depindent','addons/kg_depindent/report/indent_on_screen_report.rml',parser=indent_on_screen_report,header=False)


