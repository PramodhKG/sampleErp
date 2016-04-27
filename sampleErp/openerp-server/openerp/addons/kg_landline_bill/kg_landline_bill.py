from osv import fields,osv 
import datetime
import time
import re

class kg_landline_bill(osv.osv):
	_name = 'kg.landline.bill'
	_description = 'Enables you to verify employee contribution'
	_columns = {
				'creation_date':fields.datetime('Creation Date'),
				'dept_name':fields.many2one('hr.department','Department Name',required = True),
				'location':fields.char('Location',required = True),
				'land_bill_date':fields.date('Bill Date'),
				'land_bill_no':fields.char('Bill No',required = True),
				'land_line_no':fields.char('Land Line Number',required = True),
				'due_date': fields.date('Due Date'),
				'land_total_amt':fields.float('Bill Amount'),
				'state': fields.selection([('draft','Draft'),('confirm','Entry Confirmed'),('approve','Approved'),('cancel','Cancel')], 'Status',readonly=True),
				'active':fields.boolean('Active'), 
				'land_allowed_amt':fields.float('Allowed Amount' ,required = True),
				'balance_amt':fields.float('Balance amount to be paid',readonly = True),
				'cheque_no':fields.integer('Cheque No'),
				'cheque_date':fields.date('Cheque Date'),
				}

	_defaults = {
	
		'state': 'draft',
		'active': True,
		'creation_date': lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
		
				}
				
	def _check_duplicate_entry(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		obj = self.pool.get('kg.landline.bill')
		dept_id = entry.dept_name.id
		start_date = entry.land_bill_date
		dup_ids = obj.search(cr, uid, [('land_bill_date','=',start_date),( 'dept_name','=',dept_id)])
		print "dup_ids =============>>>", dup_ids
		if len(dup_ids) > 1:
			return False
		return True	
			
	def _landline_bill_amt_check(self, cr, uid, ids, context=None): 
		record = self.browse(cr, uid, ids[0])
		print "record.total_amt",record.land_total_amt
		if record.land_total_amt <= 0.00:
			return False
		return True
	
	
	def approve_entry(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'approve'})
		return True
	
	def confirm_entry(self, cr, uid, ids,context=None):	
		record = self.browse(cr, uid, ids[0])
		bal_amt = 0.00
		if record.land_total_amt > record.land_allowed_amt:
			bal_amt = record.land_total_amt - record.land_allowed_amt
			print bal_amt
		print bal_amt
		self.write(cr,uid,ids,{'state':'confirm','balance_amt':bal_amt})
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

	
	_constraints = [
		(_landline_bill_amt_check, 'Amount should not be empty !!',['Amount']),
		(_check_duplicate_entry, 'System not allow to save duplicate entries. Check Month and Type !!',['Duplicate Entry']),
				
		]
kg_landline_bill()

