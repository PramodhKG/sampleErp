from osv import fields,osv 
import datetime
import time

class kg_monthly_bills(osv.osv):
	_name = 'kg.monthly.bills'
	_description = 'Enables you to verify employee contribution'
	_columns = {
				'creation_date':fields.datetime('Creation Date'),
				'from_date':fields.date('Start Date'),
				'to_date':fields.date('End Date'),
				'ser_provider':fields.selection([('airtel','Airtel'),
												 ('aircel','Aircel'),
												 ('bsnl','BSNL'),
												 ('reliance','Reliance'),
												 ('v_fone','Vodafone'),
												 ('mts','MTS'),
												 ('idea','IDEA'),
												 ('uninor','uninor'),
												 ('othr','Others')],'Service Provider'),
				'due_date': fields.date('Due Date'),
				'total_amt':fields.float('Total Amount'),
				'state': fields.selection([('draft', 'not Paid'),('confirm', 'Paid')],
						'Status', readonly=True, track_visibility='onchange'),
				'active':fields.boolean('Active'),
				'bill_lines':fields.one2many('kg.monthly.bills.line','monthly_bill_entry','Bill Line')
				}

	_defaults = {
		#'state': 'draft',
		'active': True,
		'creation_date': lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
				}
	
kg_monthly_bills()

class kg_monthly_bills_line(osv.osv):
	
	_name = 'kg.monthly.bills.line'		
	_columns = {
				'monthly_bill_entry':fields.many2one('kg.monthly.bills','Line Entry'),
				'employee_id':fields.many2one('hr.employee','Employee Name',required = True),
				'mob_no':fields.char('Mobile Number',required = True),
				'amount':fields.float('Amount',required=True),
				'description':fields.text('Description'),
			}
kg_monthly_bills_line()
