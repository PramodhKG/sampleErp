## Employee Contract Module Customization ##

import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
import netsvc
import time
import datetime 
from osv import fields,osv 
import calendar 

class kg_contract(osv.osv):
	
	_name = 'hr.contract'   
	_inherit = 'hr.contract'
	
	_rec_name = 'emp_name'	
	
	_columns = {
	
	   'allowance': fields.float('HRA'),
	   'spl_allowance':fields.float('Special Allowance'),
	   'pf_status': fields.boolean('PF Applicable'),
	   'tds_status': fields.boolean('TDS Applicable'),
	   'pt_status': fields.boolean('PT Applicable'),
	   'pli_status':fields.boolean('PLI(10%)'),
	   'emp_name': fields.char('Employee Code', size=128, readonly=True),
	   'pre_basic': fields.float('Previous Basic', readonly=True),
	   'pre_allowance': fields.float('Previous Allowance',readonly=True),
	   'pre_cross': fields.float('Previous Cross Salary',readonly=True),
	   'pre_income': fields.float('Previous Annul Income',readonly=True),
	   'pre_eff_date': fields.date('Previous Effective Date',readonly=True),
	   'eff_date': fields.date('Effect On'),
	   'payment_mode': fields.selection([('cheque','THROUGH CHEQUE'),('bank','THROUGH BANK'),
							('cash','THROUGH CASH')], 'Payment Mode'),
		'bank': fields.many2one('res.bank','Bank Name'),
		'acc_no': fields.char('Salary Account No', size=32),
		'med_policy_no': fields.char('Mediclaim Policy No', size=128),
		'sal_date': fields.selection([('5th','5th Pay Day'),('7th','7th Pay Day')], 'Salary Date'),
		'sal_type': fields.selection([('pf','PF EMPLOYEE'),('non_pf', 'NON-PF EMPLOYEE')], 'Salary Type'),
		'pf_acc_no': fields.char('PF Account NO', size=32),
		'pan_no': fields.char('PAN NO', size=32),
		'esi_acc_no': fields.char('ESI NO', size=32),
		'ot': fields.boolean('Applicable OT'),
		'tax': fields.boolean('Income Tax(10%)'),
		'esi': fields.boolean('ESI'),
		'esi_eff_date':fields.date('ESI Effective From'),
		'over_type': fields.char('Over Type', size=128,invisible = True),
		'pf_eff_date': fields.date('PF Effective From'),
		'tax_val': fields.float('Tax Percentage(%)'),
		'dep_id': fields.many2one('hr.department', 'Department Name', readonly=True),
		'join_date': fields.date('Date Of Joining', readonly=True),
		'designation': fields.char('Designation', size=128, readonly=True),
		'leave_type': fields.selection([('tut', 'TUTOR'),('emp', 'EMPLOYEE')], 'Leave Type', readonly=True),	
		'shift_type': fields.many2one('kg.shift.time', 'Shift Type', readonly=True),
		'last_update_date': fields.date('Last Update Date'),
		'pf_percentage':fields.float('PF Percentage'),
		'esi_percentage':fields.float('ESI Percentage'),
		'salary_entry':fields.one2many('kg.salary.detail','salary_id','Salary Entry'),
		'gross_salary':fields.float('Gross Salary', help="Please Enter the Gross salary per month.",required = True),
		'tel_allow':fields.float('Mobile Allowance',required = True),
		'increament_type':fields.selection([('yr','Yearly'),('perform','Performance'),('promotion','Promotions')],'Increament Type',required=True),
		'increament_amount':fields.float('Increment Amount',required = True),
		'creation_date':fields.datetime('Creation Date',readonly = True),
		'active':fields.boolean('active')
	}
	
	def _gross_salary(self,cr,uid,ids,context = None):
		print "IDS..........................",ids
		con_det = self.browse(cr,uid,ids[0])
		print "con_det............................", con_det.salary_entry
		fix_amt,per_amt = 0.00,0.00
		for entry in con_det.salary_entry:
			if entry.type =='fixed_amt':
				fix_amt += entry.salary_amount
			else:
				per_amt += (con_det.gross_salary * entry.salary_amount)/100
				
		tot_amt = fix_amt + per_amt
		print "tot_amt.......................",tot_amt
		print "con_det.gross_salary..........",con_det.gross_salary
		if con_det.gross_salary != tot_amt:
			return False
		else:
			return True
			
	def _gross_salary_check(self, cr, uid, ids, context=None):
		record = self.browse(cr, uid, ids[0])
		if record.gross_salary <= 0:
			return False
		return True
	
	def _contract_duplicate(self, cr, uid, ids, context=None):
		obj = self.pool.get('hr.contract')
		record = self.browse(cr, uid, ids[0])
		emp_id = record.employee_id.id
		dup_ids = obj.search(cr, uid,[('employee_id','=',emp_id)])
		print "dup_ids =======================>>>>", dup_ids
		if len(dup_ids) > 1:
			return False
		return True
		
	def _onchange_pf_date(self, cr, uid, ids, pf_eff_date,pf_status,context= None):
		record = self.browse(cr,uid,ids[0])
		value = {'pf_eff_date':''}
		print "record.joing dateeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee       ",record.join_date	
		join_date = str(record.join_date) 
		d1 = datetime.datetime.strptime(join_date, "%Y-%m-%d") 
		pf_date = d1 + datetime.timedelta(days = 30)
		print "diffffffffffffffffffffffffffff",pf_date
		return {value :{'pf_eff_date':pf_date}}

	def onchange_roll(self,cr,uid,ids,name,roll_no,context=None):
		value = {'roll_no':''}
		if name:
			stu = self.pool.get('school.management')
			stu_obj = stu.browse(cr,uid,name,roll_no)
			valu = {'roll_no': stu_obj.roll_no}
		return {'value': valu}

	def _check_entry_line(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		if not entry.salary_entry:
			return False
		else:
			for line in entry.salary_entry:
				if line.type == 'percent':
					if line.salary_amount > 100:
						raise osv.except_osv( ('Warning!'), ('You percentage cannot be more than 100.'))
						return False
				if line.salary_amount == 0.00:
					return False
		return True
	
	_constraints = [
		
		(_contract_duplicate, 'System not allow to save duplicate entries. Contract already available for this employee !!',['amount']),
		(_check_entry_line, 'Salary Details can not be empty !!',['Entry Line']),
		(_gross_salary,'Please enter the salary details',['Details']),
		#(_gross_salary_check,'Gross Salary Must be greater than Zero',['Gross Salary']),
		#(_onchange_pf_date,'Joing date',['Joining Date'])
		]
		
		
	_defaults = {
		
        'creation_date': lambda *a: datetime.date.today().strftime('%Y-%m-%d %I:%M:%S'),
		'pf_status': True,
		'active':True
	
		}
	
	_order = 'employee_id'
		
	def onchange_employee_code(self, cr, uid, ids, employee_id,emp_name, context=None):
		value = {'emp_name':'','dep_id':'','join_date':'','designation':'','leave_type':'','shift_type':''}
		if employee_id:
			emp = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
			value = {'emp_name': emp.emp_code,
					'dep_id':emp.department_id.id,
					'join_date': emp.join_date,
					'designation': emp.job_id.name,
					'leave_type': emp.leave_type,
					'shift_type': emp.shift_type.id
					}
		return {'value': value}
		
	def create(self, cr, uid,vals,context=None):
		#print "vals.......create..............", ids
		if vals.has_key('employee_id') and vals['employee_id']:
			emp_rec = self.pool.get('hr.employee').browse(cr,uid,vals['employee_id'])
			if emp_rec:
				vals.update({'emp_name':emp_rec.emp_code,
							'dep_id':emp_rec.department_id.id,
							'join_date': emp_rec.join_date,
							'designation': emp_rec.job_id.name,
							'leave_type': emp_rec.leave_type,
							'shift_type': emp_rec.shift_type.id
							})						  
		order =  super(kg_contract, self).create(cr, uid, vals, context=context)
		return order
		
	def write(self, cr, uid,ids, vals, context=None):
		print "vals.....................", vals
		if vals.has_key('employee_id') and vals['employee_id']:
			emp_rec = self.pool.get('hr.employee').browse(cr,uid,vals['employee_id'])
			if emp_rec:
				vals.update({'emp_name':emp_rec.emp_code,
							'dep_id':emp_rec.department_id.id,
							'join_date': emp_rec.join_date,
							'designation': emp_rec.job_id.name,
							'leave_type': emp_rec.leave_type,
							'shift_type': emp_rec.shift_type.id
							})
		
			
		res = super(kg_contract, self).write(cr, uid, ids,vals, context)
		return res
		
	def salary_update(self, cr, uid, ids,context=None):
		con_rec = self.browse(cr,uid,ids[0])
		revision_obj = self.pool.get('kg.salary.revision')
		today = datetime.date.today()
		emp_id = con_rec.employee_id.id
		last_date = con_rec.last_update_date
		print "con_rec===================", con_rec
		print "uid==================", uid
		up_ids = revision_obj.search(cr, uid,[('creation_date','=',last_date),('employee_id','=',emp_id),
													('contract_id','=',ids[0])]) 
		print "up_ids-----------------........", up_ids
		if up_ids:		  
			revision_rec = revision_obj.browse(cr, uid,up_ids[0])
			last_basic = revision_rec.basic_pay
			last_allo = revision_rec.allowance_pay	  
			print "last_basic---------------", last_basic
			print "con_rec.wage-------------------",con_rec.wage
		else:
			last_basic = con_rec.wage
			last_allo = con_rec.allowance
						
		if not up_ids or con_rec.wage != last_basic or con_rec.allowance != last_allo:
						
			vals = {
					
					'user_id': uid,
					'creation_date': today,
					'employee_id': con_rec.employee_id.id,
					'contract_id': ids[0],
					'basic_pay': con_rec.wage,
					'allowance_pay': con_rec.allowance,
					'last_basic': last_basic,
					'last_allowance':last_allo,
					'last_up_date': last_date,
					}
					
			changes = revision_obj.create(cr, uid, vals)
			con_rec.write({'last_update_date': today,'pre_basic':last_basic, 'pre_allowance': last_allo})
		else:
			raise osv.except_osv(_('No Changes'),_('There is no changes between current and last one !!'))
		
		return True
	
	
	
kg_contract()


class kg_salary_revision(osv.osv):
	
	_name = 'kg.salary.revision'
	_description = 'Employee Salary Revision Details'
	
	_columns = {
	
	'employee_id': fields.many2one('hr.employee', 'Employee Name'),
	'emp_name':fields.char('Employee Code'),
	'contract_id': fields.many2one('hr.contract', 'Contract'),
	'user_id': fields.many2one('res.users', 'System User'),
	'creation_date': fields.date('Creation Date'),
	'basic_pay': fields.float('Basic Pay'),
	'allowance_pay': fields.float('Allowance'),
	'last_basic': fields.float('Last Basic Pay'),
	'last_allowance': fields.float('Last Allowatypence Pay'),
	'last_up_date': fields.date('Last Update Date'),
	
	}
	
kg_salary_revision()
	
	
class kg_salary_detail(osv.osv):
	
	_name = 'kg.salary.detail'
	_columns = {
				'salary_id':fields.many2one('hr.contract','Salary ID',invisible= True),
				'salary_type':fields.many2one('hr.salary.rule','Salary',required=True),
				'type':fields.selection([('fixed_amt','Fixed Amount'),('percent','Percentage')],'Type',required=True),
				'salary_amount':fields.float('Amount',required = True)
				}
	_defaults = {

				'type':'fixed_amt',

				}
				
	
		
	
kg_salary_detail()


