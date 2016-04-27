import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler
import netsvc


class gate_pass_report(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(gate_pass_report, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({'time': time})

report_sxw.report_sxw('report.gate.pass.report','kg.gate.pass','addons/kg_gate_pass/report/gate_pass_report.rml',parser=gate_pass_report,header=False)


