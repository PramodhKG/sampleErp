from osv import fields,osv 
import datetime
import time
import re

class kg_mobile_bills(osv.osv):
	_name = 'kg.mobile.bills'
	_description = 'Enables you to verify employee contribution'
	_columns = {
				'creation_date':fields.datetime('Creation Date'),
				'bill_date':fields.date('Bill Date',readonly=True ,states = {'draft': [('readonly', False)]}),
				'employee_name':fields.many2one('hr.employee','Employee Name',required = True,readonly=True ,states = {'draft': [('readonly', False)]}),
				'employee_code':fields.char('Employee Code',readonly = True),
				'mobile_no':fields.char('Mobile Number',readonly = True),
				'bill_no':fields.char('Bill No',required = True,readonly=True ,states = {'draft': [('readonly', False)]}),
				'ser_provider':fields.selection([('airtel','Airtel'),
												 ('aircel','Aircel'),
												 ('bsnl','BSNL'),
												 ('reliance','Reliance'),
												 ('v_fone','Vodafone'),
												 ('mts','MTS'),
												 ('idea','IDEA'),
												 ('uninor','uninor'),
												 ('othr','Others')],'Service Provider',readonly=True ,states = {'draft': [('readonly', False)]}),
				'due_date': fields.date('Due Date',readonly=True ,states = {'draft': [('readonly', False)]}),
				'total_amt':fields.float('Bill Amount',readonly=True ,states = {'draft': [('readonly', False)]}),
				'state': fields.selection([('draft','Draft'),('confirm','Entry Confirmed'),('cancel','Cancel')], 'Status',readonly=True),
				'active':fields.boolean('Active'), 
				'con_tell_allow':fields.float('Allowed Amount',readonly = True),
				'balance_amt':fields.float('Balance amount to be paid',readonly = True),
				}

	_defaults = {
		'state': 'draft',
		'active': True,
		'creation_date': lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
				}
				
	def _check_duplicate_entry(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		obj = self.pool.get('kg.mobile.bills')
		emp_id = entry.employee_name.id
		start_date = entry.bill_date
		#end_date = entry.to_date
		dup_ids = obj.search(cr, uid, [('bill_date','=',start_date),( 'employee_name','=',emp_id)])
		print "dup_ids =============>>>", dup_ids
		if len(dup_ids) > 1:
			return False
		return True	
			
	def _mobile_bill_amt_check(self, cr, uid, ids, context=None): 
		record = self.browse(cr, uid, ids[0])
		print "record.total_amt",record.total_amt
		if record.total_amt <= 0.00:
			return False
		return True
	
	def confirm_entry(self, cr, uid, ids,context=None):		
		self.write(cr,uid,ids,{'state':'confirm'})
		return True
		
	def cancel_entry(self, cr, uid, ids,context=None):
		record = self.browse(cr, uid, ids[0])		
		if record.state == 'draft':
			self.write(cr,uid,ids,{'state':'cancel'})
		else:
			self.write(cr,uid,ids,{'state':'cancel'})
		return True

	def draft_entry(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'draft'})
		return True
	
	def _check_entry_line(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		if not entry.bill_lines:
			return False
		else:
			for line in entry.bill_lines:
				if not (line.employee_id and line.mob_no and line.amount):
					raise osv.except_osv( ('Warning!'), ('Required fields cannot be empty!'))
					return False
		return True

	def onchange_employee_code(self, cr, uid, ids, employee_name,employee_code,total_amt, context=None):
		value = {'employee_code':''}
		if employee_name:
			emp = self.pool.get('hr.employee').browse(cr, uid, employee_name, context=context)
			con_ids = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',employee_name)])
			con_rec = self.pool.get('hr.contract').browse(cr,uid,con_ids[0])
			value = {'employee_code': emp.emp_code,'mobile_no':emp.work_phone,'con_tell_allow':con_rec.tel_allow,
					}
		return {'value': value}
		
	def create(self, cr, uid,vals,context=None):
		#print "vals.......create..............", ids
		if vals.has_key('employee_name') and vals['employee_name']:
			emp_rec = self.pool.get('hr.employee').browse(cr,uid,vals['employee_name'])
			con_ids = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',vals['employee_name'])])
			con_rec = self.pool.get('hr.contract').browse(cr,uid,con_ids[0])
			if vals['total_amt'] > con_rec.tel_allow:
				bal = con_rec.tel_allow - vals['total_amt']
			else:
				bal = 0.00
			if emp_rec:
				vals.update({'employee_code':emp_rec.emp_code,'mobile_no':emp_rec.work_phone,'con_tell_allow':con_rec.tel_allow,
							 'balance_amt': -(bal) })						  
		order =  super(kg_mobile_bills, self).create(cr, uid, vals, context=context)
		return order
	
	_constraints = [
		(_mobile_bill_amt_check, 'Amount should not be empty !!',['Amount']),
		(_check_duplicate_entry, 'System not allow to save duplicate entries. Check Month and Type !!',['Duplicate Entry']),
				
		]
kg_mobile_bills()

