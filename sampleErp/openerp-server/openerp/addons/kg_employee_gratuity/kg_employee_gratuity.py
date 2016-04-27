from osv import fields,osv 
import datetime
import time, datetime 
from datetime import * 
import calendar 
import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
import netsvc


class kg_employee_gratuity(osv.osv):
	_name = 'kg.employee.gratuity'
	_description = 'Employee Gratuity'
	
	req = True
	
	_columns = {
				
				'from_date':fields.date('From Date',readonly=True ),
				'to_date':fields.date('To Date',readonly=True ),
				'creation_date':fields.datetime('Creation Date',readonly=True),
				'active':fields.boolean('Active'),
				'employee_id':fields.many2one('hr.employee','Employee Name',readonly=True ),
				'employee_name':fields.char('Employee Code',readonly=True ),
				'state': fields.selection([('draft', 'To Submit'),('confirm', 'Waiting For Approval'),('approved','Approved'),('paid','Paid'),('cancel','Cancelled')],
								'Status', readonly=True, track_visibility='onchange'),
				'gratuity_amount':fields.float('Gratuity Amount',readonly=True ),
				'gratuity_date':fields.date('Gratuity Date',readonly=True ),
				'payment_mode':fields.selection([('bank','Through Bank'),('cash','Through Cash'),('cheque','Through Cheque')],'Payment Mode'
													,readonly=True ,states = {'confirm': [('readonly', False),('required', req)]}),
				'bank': fields.many2one('res.bank','Account Journal Type',readonly = False , states = {'paid': [('readonly', True)],'approved': [('readonly', True)]}),
				'acc_no': fields.char('Account No',readonly = False , states = {'paid': [('readonly', True)],'approved': [('readonly', True)]}),
				'cheque_no':fields.char('Cheque No',states = {'approved': [('readonly', True)]}),
				'approved_date':fields.datetime('Confirmed Date',readonly = True ),
				'approved_by' : fields.many2one('res.users', 'Confirmed By', readonly= True),
				'paid_date':fields.date('Paid Date',readonly = True),
				'paid_by' : fields.many2one('res.users', 'Paid By', readonly= True),
				
				}

	_defaults = {
		'state': 'draft',
		'to_date':fields.date.context_today,
		'active': True,
		'creation_date': lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
				}
				
	
	def confirm_entry(self, cr, uid, ids,context=None):
		self.write(cr,uid,ids,{'state':'confirm'})
		return True	
	
	def approve_entry(self, cr, uid, ids,context=None):
		timein = str(datetime.now())
		self.write(cr,uid,ids,{'state':'approved', 'approved_date':  timein,
									'approved_by' :  uid})	
	
	def paid_entry(self,cr,uid,ids,context = None):
		timein = str(datetime.now())
		self.write(cr,uid,ids,{'state':'paid', 'paid_date':  timein,
									'paid_by' : uid})
	
	def cancel_entry(self, cr, uid, ids,context=None):
		entry = self.browse(cr,uid,ids[0])
		if entry.state == 'paid':
			raise osv.except_osv(_('Amount has been paid!'), 
					_('Cannot cancel this entry!!'))
		else:
			self.req = False
			self.write(cr, uid, ids, {'state':'cancel'})
			
		return True
		
		
	
	def _check_entry_line(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		if not entry.cont_line_id:
			return False
		else:
			for line in entry.cont_line_id:
				if line.cont_type == 'percent':
					if line.contribution_percentage > 100:
						raise osv.except_osv( _('Warning!'), _('You percentage cannot be more than 100.'))
						return False
				if line.contribution_percentage == 0.00: 
					return False
		return True
	
	
	def compute_gratuity_date(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		emp_sql = """ select id from resource_resource where active = 't' and id != 1 """
		cr.execute(emp_sql)
		data = cr.dictfetchall()
		print "data...........",data
		
		gratuity_obj = self.pool.get('kg.employee.gratuity')
		gratuity_id = gratuity_obj.search(cr, uid, [('id','!=',entry.id)])
		print gratuity_id
		n=0
		for item in data:
			# Employee Id
			emp_id = self.pool.get('hr.employee').browse(cr,uid,item['id'])
			print "emp_id.................",emp_id.id
			print "emp_id.................",emp_id.join_date
			
			#by default gra_from_date will be employee's joining date
			
			gra_from_date = emp_id.join_date
			
			#Contract id for gross salary
			print item['id']
			con_id = self.pool.get('hr.contract').search(cr, uid, [('employee_id', '=', item['id'])])
			
			print con_id
			con_gross = 0.00
			tot_grt_amount = 0.00
			if con_id:
				con_rec= self.pool.get('hr.contract').browse(cr, uid,con_id[0])	
				print "con_rec.......................ss",con_rec.gross_salary
				con_gross = con_rec.gross_salary
				print "contract   gross	salary	  ",con_gross
				# Searching in kg_salary_detail
				
				sal_det = self.pool.get('kg.salary.detail')
				ctc_ids = sal_det.search(cr,uid,[('salary_id','=',con_id[0])])
				print "ctc_ids.........................",ctc_ids
			
			#Checking Existance for employee
			#if exist changing form date for that employee
			print "item[id]....   ",item['id']
			
			for ids in gratuity_id:
				grt_sear_ids = gratuity_obj.search(cr,uid,[('employee_id','=',item['id'])])
				if grt_sear_ids:
					print "							",grt_sear_ids
					grt_emp_ids = gratuity_obj.browse(cr,uid,grt_sear_ids[0])
					print "			 grt_emp_ids ___________________________",grt_emp_ids.employee_id
					print emp_id.id
					if grt_emp_ids.employee_id.id == emp_id.id:
						#gra_from_date = grt_emp_ids.from_date
						gra_from_date = grt_emp_ids.to_date
						print "gra_from_date,,,,,,,,,",gra_from_date
						#print "gra_to_date,,,,,,,,,",gra_to_date
		
			#Calculation for gratuity amount
			gra_from_date = str(gra_from_date)
			crut_date = date.today() 
			crut_date = str(crut_date) 
			d1 = datetime.strptime(gra_from_date, "%Y-%m-%d") 
			print "d1111111111111111111111111111111111111",d1
			d2 = datetime.strptime(crut_date, "%Y-%m-%d") 
			print "d222222222222222222222222222222222222",d2 
			daysDiff = str((d2-d1).days) 
			print "days	   diff",daysDiff
			diff = float(daysDiff)/365
			print "diffffffffffffffffffffffffffff",diff

			if diff == 5.00:
				for ids in ctc_ids:
					sal_rec = sal_det.browse(cr,uid,ids)
					print sal_rec.salary_type.code		
					if sal_rec.salary_type.code == 'BASIC' or sal_rec.salary_type.code == 'DA':
						print "fds						 fder"
						if sal_rec.type == 'fixed_amt':
							grat_amount = (sal_rec.salary_amount*15*5)/26
							print "grat_amount......................",grat_amount
							tot_grt_amount += grat_amount
						else:
							per_grat = (con_gross * sal_rec.salary_amount)/100
							print "per_grat....................",per_grat
							grat_amount = (per_grat*15*5)/26
							print  "grat_amount..........................",grat_amount
							tot_grt_amount += grat_amount
				print "tot_grat_amount .......	 .............",tot_grt_amount
			
			
				gratuity_obj.create(cr,uid,{
					'from_date': gra_from_date,
					'to_date': crut_date,
					'employee_id': emp_id.id,
					'employee_name':emp_id.emp_code,
					'gratuity_amount': tot_grt_amount,
					'gratuity_date':entry.to_date,
					'state': 'draft',
				}	)
			
			
		return data

	
kg_employee_gratuity()
