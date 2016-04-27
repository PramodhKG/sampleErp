import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
import netsvc

class kg_job_request(osv.osv):

	_name = "kg.job.request"
	_description = "Job Request"
	
	_columns = {
	
		#### Position Information ###
		'state': fields.selection([('confirm','Confirmed'),('open','Draft')], 'Status', readonly=True),
		'job_id': fields.many2one('hr.job','Job Title',required=True,readonly=True, states={'open':[('readonly',False)]}),
		'no_of_persons':fields.integer('No. of Candidates Required',required=True,readonly=True, states={'open':[('readonly',False)]}),
		'department_id':fields.many2one('hr.department','Department to be placed in',required=True,readonly=True, states={'open':[('readonly',False)]}),
		'location': fields.selection([('hyd','HYDERABAD')], 'Location',readonly=True, states={'open':[('readonly',False)]}),
		'join_date':fields.date('Date of Joining',readonly=True, states={'open':[('readonly',False)]}),
		'manager':fields.many2one('hr.employee','Line Manager',readonly=True, states={'open':[('readonly',False)]}),
		'type':fields.selection([('perm','Permanent'),('contract','Contractual')], 'Employee Type',readonly=True, states={'open':[('readonly',False)]}),
		'date_req':fields.date('Date by which resource is required',required=True,readonly=True, states={'open':[('readonly',False)]}),
		'pos_type':fields.selection([('intern','Intern'),('replace','Replacement'),('project','Project'),], 'Position Type',required=True,readonly=True, states={'open':[('readonly',False)]}),
		'proj_name':fields.char('Project Name',readonly=True, states={'open':[('readonly',False)]}),
		'emp_replace':fields.many2one('hr.employee','Employee to be Replaced',readonly=True, states={'open':[('readonly',False)]}),
		'emp_period':fields.selection([('one', '1 Month'),
										('two', '2 Months'),
										('three', '3 Months'),
										('four', '4 Months'),
										('five', '5 Months'),
										('six', '6 Months'),
										('seven', '7 Months'),
										('eight', '8 Months'),
										('nine', '9 Months'),
										('ten', '10 Months'),
										('ele', '11 Months'),
										('twe', '12 Months')], 'Employment Period(if not permanent)',readonly=True, states={'open':[('readonly',False)]}),
		'justify':fields.char('Justification for the Requisition',readonly=True, states={'open':[('readonly',False)]}),
	   
		### Salary Entitlement ###
		
		'rec_ctc':fields.float('Recommended Monthly CTC monthly : Rs.',required=True,readonly=True, states={'open':[('readonly',False)]}),
		'car':fields.boolean('Car',readonly=True, states={'open':[('readonly',False)]}),
		'fuel':fields.boolean('Fuel',readonly=True, states={'open':[('readonly',False)]}),
		'mobile':fields.boolean('Mobile Allowance',readonly=True, states={'open':[('readonly',False)]}),
		'comp_eqp':fields.selection([('desk','Desktop'),('lap','Laptop')], 'Computer Equipment',readonly=True, states={'open':[('readonly',False)]}),
		'cc_det':fields.char('Details (cc)',readonly=True, states={'open':[('readonly',False)]}),
		'lit_det':fields.char('Details (Litres/kg)',readonly=True, states={'open':[('readonly',False)]}),
		'amt_det':fields.float('Details (Amount)',readonly=True, states={'open':[('readonly',False)]}),
		'justify_lap':fields.char('Justification for Laptop',readonly=True, states={'open':[('readonly',False)]}),
		
		
		### Budget Information ###
		
		'budget':fields.selection([('yes','YES'),('no','NO')], 'Budgeted'),
		'month':fields.selection([('jan', 'January'),
										('feb', 'February'),
										('mar', 'March'),
										('apr', 'April'),
										('may', 'May'),
										('june', 'June'),
										('july', 'July'),
										('aug', 'August'),
										('sep', 'September'),
										('oct', 'October'),
										('nov', 'November'),
										('dec', 'December')], 'From which month',readonly=True, states={'open':[('readonly',False)]}),
		'bud_justify':fields.char('(if no) Justification for new position',readonly=True, states={'open':[('readonly',False)]}),
		'gross_sal':fields.float('Budgeted Monthly Gross Salary : Rs.',required=True,readonly=True, states={'open':[('readonly',False)]}),
		
		### Approvals ###
		
		'man_sign':fields.many2one('hr.employee','Line Manager(Signature)',required=True,readonly=True, states={'open':[('readonly',False)]}),
		'head_sign':fields.many2one('hr.employee','Business Unit Heads(Signature)',required=True,readonly=True, states={'open':[('readonly',False)]}),
		'hr_sign':fields.many2one('hr.employee','HR Department(Signature)',required=True,readonly=True, states={'open':[('readonly',False)]}),
		'man_dir':fields.many2one('hr.employee','MD/CEO(Signature)',readonly=True, states={'open':[('readonly',False)]}),
		'fin_sign':fields.many2one('hr.employee','Manager Finance(Signature)',required=True,readonly=True, states={'open':[('readonly',False)]}),
		'man_date':fields.date('Date',readonly=True, states={'open':[('readonly',False)]}),
		'head_date':fields.date('Date',readonly=True, states={'open':[('readonly',False)]}),
		'hr_date':fields.date('Date',readonly=True, states={'open':[('readonly',False)]}),
		'fin_date':fields.date('Date',readonly=True, states={'open':[('readonly',False)]}),
		'man_date':fields.date('Date',readonly=True, states={'open':[('readonly',False)]}),
				
		
	}
	
	_defaults = {
		'date_req' : fields.date.context_today,
		'state': 'open',
		
		

	}
	
		
	def unlink(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state not in ['open']:
				raise osv.except_osv(_('Warning!'),_('You cannot delete a job Request which is in %s state.')%(rec.state))
		return super(kg_job_request, self).unlink(cr, uid, ids, context)
		
	def write(self, cr, uid, ids, vals, context=None):
		for  holiday in self.browse(cr, uid, ids, context=context):
			if holiday.state in ('confirm') and not check_fnct(cr, uid, 'write', raise_exception=False):
				raise osv.except_osv(_('Warning!'),_('You cannot modify a job request that has been confirmed. Contact a human resource manager.'))
		return super(kg_job_request, self).write(cr, uid, ids, vals, context=context)
		
	def confirm_request(self, cr, uid, ids,context=None):
		request_rec = self.browse(cr,uid,ids[0])
		job_name=request_rec.job_id.name
		print "job_name",job_name
		positions=request_rec.no_of_persons
		job_obj = self.pool.get('hr.job')
		print "job_obj.........",job_obj
		
		job_id = job_obj.search(cr,uid,[('name','=',job_name)])
		if job_id:
			job_rec=job_obj.browse(cr,uid,job_id[0])
			print "job_obj.........",job_rec
			no_of_recruit=job_rec.no_of_recruitment
			no_of_positions=no_of_recruit + positions
			job_rec.write({'no_of_recruitment':no_of_positions})					
			self.write(cr,uid,ids,{'state':'confirm'})
		return True
	
	
	def onchange_department(self, cr, uid, ids, job_id,department_id,context=None):
		value = {'dapartment_id' : ''}
		if job_id:
			department = self.pool.get('hr.job').browse(cr, uid, job_id, context=context)
			print "department..........",department
			value = {'department_id' : department.department_id.id}
			print "value",value
		return {'value' : value}
	
kg_job_request()

