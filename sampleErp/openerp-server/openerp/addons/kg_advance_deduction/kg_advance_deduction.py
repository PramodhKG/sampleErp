from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import datetime
import time, datetime 
from datetime import * 
import calendar 
import math
from openerp import tools
import netsvc
import openerp
from datetime import datetime


class kg_advance_deduction(osv.osv):

	_name = "kg.advance.deduction"
	_description = "Advance Deduction"
	_order = "date desc"
	
	_columns = {
		
		'date': fields.date('Creation Date', readonly=True),
		'employee_id': fields.many2one('hr.employee','Employee Name', required=True,
				readonly=True, states={'draft':[('readonly',False)]}),
		'emp_name': fields.char('Employee Code', size=128, readonly=True),
		'ded_type': fields.selection([('adv', 'ADVANCE'),('ins1', 'ADVANCE_1'),('ins2', 'ADVANCE-2'),
						('tre', 'TREATMENT'),('rent', 'RENT')], 
						'Cumulative Deduction Type', required=True,	readonly=True, states={'draft':[('readonly',False)]}),
		'tot_amt': fields.float('Total Amount', required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'pay_amt': fields.float('Repay Pay Amount', required=True,
					readonly=True, states={'draft':[('readonly',False)]}),
		'period': fields.integer('Repay Period', required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'cum_date': fields.date('Cumulative Deduction Date',readonly=True, states={'draft':[('readonly',False)]}),
		'state'	: fields.selection([('draft', 'Draft'),('confirm', 'Confirmed'),('approve','Approved'),('cancel', 'Cancelled'),
					('expire', 'Expired')],'Status', readonly=True),
		'expiry': fields.boolean('Expiry'),
		'amt_paid': fields.float('Amount Paid So Far'),
		'allow': fields.boolean('Applicable This Month'),
		'bal_amt': fields.float('Balance Amount'),
		'round_bal': fields.float('Round Balance'),
		'remarks':fields.text('Remarks'),
		'confirm_by' : fields.many2one('res.users', 'Confirmed By', readonly= True),
		'confirm_date':fields.date('Confirmed Date',readonly = True ),
		'approve_date':fields.date('Approved Date',readonly = True),
		'approve_by' : fields.many2one('res.users', 'Approved By', readonly= True),
		'cancel_by' : fields.many2one('res.users', 'Cancel By', readonly= True),
		'cancel_date':fields.date('Cancel Date',readonly = True),
		
		}
		
	_defaults = {
	
		'date': fields.date.context_today,
		'state': 'draft',
		'allow': True,
		
	}
	
	def _check_duplicate_entry(self, cr, uid, ids, context=None):
		ded_obj = self.pool.get('kg.advance.deduction')
		for entry in self.browse(cr, uid, ids):
			dup_ids = ded_obj.search(cr, uid,[('employee_id','=',entry.employee_id.id),
						('ded_type','=',entry.ded_type),('state','=','confirm')])
			print "dup_ids....................", dup_ids
			if len(dup_ids) > 1:
				return False
		return True		
		
	def _zero_amount_check(self, cr, uid, ids, context=None):
		for entry in self.browse(cr, uid, ids):
			print "entry...............", entry, entry.tot_amt
			if entry.tot_amt > 0:
				return True
		return False
		
	def _validation_month_amount(self,cr,uid,ids,context=None):
		for entry in self.browse(cr, uid, ids):
			due_amt = entry.period * entry.pay_amt
			if due_amt > entry.tot_amt:
				return False
		return True
		
		
		
	def confirm_entry(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		timein = datetime.now()
		timein = timein.strftime('%Y-%m-%d')
		self.write(cr,uid,ids,{'state':'confirm','confirm_by' :  uid,'confirm_date': timein,})
		sub = "Advance To "+rec.employee_id.name+" - Waiting For Approval"
		self.ad_mail_content(cr,uid,rec,sub=sub,state=rec.state)
		
	
	
	"""def entry_approve(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids[0])
		amt = rec.tot_amt - rec.pay_amt * rec.period
		date = datetime.now()
		date = date.strftime('%d-%m-%Y')
		self.write(cr,uid,ids,{'state': 'approve' , 'round_bal': amt,'approve_date':date , 'approve_by':uid})"""
	
	def approve_entry(self,cr,uid,ids,context = None):
		rec = self.browse(cr,uid,ids[0])
		amt = rec.tot_amt - rec.pay_amt * rec.period
		timein = datetime.now()
		timein = timein.strftime('%Y-%m-%d')
		self.write(cr, uid, ids, {'state':'approve','round_bal': amt,'approve_date':timein,'approve_by':uid})		
		sub = "Advance To "+rec.employee_id.name+" - Approved By MD"
		self.ad_mail_content(cr,uid,rec,sub=sub,state='approve')
			
				
			
	def cancel_entry(self,cr,uid,ids,context = None):
		rec = self.browse(cr,uid,ids[0])
		timein = datetime.now()
		timein = timein.strftime('%Y-%m-%d')
		self.write(cr, uid, ids, {'state': 'cancel','cancel_date':timein,'cancel_by':uid})
		sub = "Advance To "+rec.employee_id.name+" - Cancelled By MD"
		if not rec.remarks:
			raise openerp.exceptions.Warning(_('Remarks is must !!. Enter cancel remarks in remarks field'))
		else:
			self.ad_mail_content(cr,uid,rec,sub=sub,state=rec.state)	
				
	def ad_mail_content(self,cr,uid,rec,sub,state,context=None):
		
		from_mailid = "erpmail@kgcloud.org"		
		msg = ''
		msg = MIMEMultipart('alternative')
		msg['Subject'] = sub
		res_id = rec.id

		timein = datetime.now()
		timein = timein.strftime('%Y-%m-%d')
		user_rec = self.pool.get('res.users').browse(cr,uid,uid)
		
		emp_name = rec.employee_id.name.encode('utf-8')
		emp_code = rec.employee_id.emp_code.encode('utf-8')
		
		
		if rec.employee_id.branch :
			branch  = rec.employee_id.branch.name.encode('utf-8')
		else:
			branch = ''
		if rec.employee_id.department_id:
			dept_name = rec.employee_id.department_id.name.encode('utf-8')
		else:
			dept_name = ''
		if rec.employee_id.job_id:
			job  = rec.employee_id.job_id.name.encode('utf-8')
		else:
			job = ''
		if rec.remarks:
			remarks  = rec.remarks.encode('utf-8')
		else:
			remarks = ''
			
		tot_amt= str(rec.tot_amt)
		repay_per= str(rec.period)
		repay_amt= str(rec.pay_amt)
		
		conf_by = rec.confirm_by.name
		conf_date = datetime.strptime(rec.confirm_date,'%Y-%m-%d')
		conf_date = conf_date.strftime("%m-%d-%Y")
		
		if state == 'approve':
			app_by = user_rec.name.encode('utf-8')
			app_date = datetime.strptime(timein,'%Y-%m-%d')
			app_date = app_date.strftime('%d-%m-%Y')
			app_date = app_date.encode('utf-8')
		
		if state == 'cancel':
			cancel_by = user_rec.name.encode('utf-8')
			cancel_date = datetime.strptime(timein,'%Y-%m-%d')
			cancel_date = cancel_date.strftime('%d-%m-%Y')
			cancel_date = cancel_date.encode('utf-8')

		
		print rec.state
		
		body_part_1 = """\
				<html>
				<head>
				<style>
				table, th, td {
				border: 1px black;
				border-collapse: collapse;
				}
				th, td {
				padding: 5px;
				}
				</style>
				</head>
					<body>
					"""
				
		body_part_2 = """<table style="width:75%" > 
					<tr style="color:blue;"><td>Employee Name</td><td>:</td><td >"""+emp_name+"""</td></tr>
					<tr style="color:blue;"><td>Employee Code</td><td>:</td><td >"""+emp_code+"""</td></tr>
					<tr style="color:blue;"><td>Department Name</td><td>:</td><td >"""+dept_name+"""</td></tr>
					<tr style="color:blue;"><td>Designation</td><td>:</td><td >"""+job+"""</td></tr>
					<tr style="color:blue;"><td>Branch</td><td>:</td><td >"""+branch+"""</td></tr>
					<tr style="color:blue;"><td>Advance Amount</td><td>:</td><td >"""+tot_amt+"""</td></tr>
					<tr style="color:blue;"><td>Repay Period</td><td>:</td><td >"""+repay_per+"""</td></tr>
					<tr style="color:blue;"><td>Repay amount</td><td>:</td><td >"""+repay_amt+"""</td></tr>						
					<tr style="color:blue;"><td>Remarks</td><td>:</td><td>"""+str(remarks)+"""</td></tr>
					"""
					
		if state == 'confirm':
			body_part_3 = """
						<tr style="color:blue;"><td>Confirmed Date</td><td>:</td><td>"""+conf_date+"""</td></tr>
						<tr style="color:blue;"><td>Confirmed By</td><td>:</td><td>"""+str(conf_by)+"""</td></tr>
					"""
					
		
		elif state == 'approve':
			
			body_part_3 = """
						<tr style="color:blue;"><td>Confirmed Date</td><td>:</td><td>"""+conf_date+"""</td></tr>
						<tr style="color:blue;"><td>Confirmed By</td><td>:</td><td>"""+str(conf_by)+"""</td></tr>
						<tr style="color:blue;"><td>Approved Date</td><td>:</td><td>"""+str(app_date)+"""</td></tr>
						<tr style="color:blue;"><td>Approved By</td><td>:</td><td>"""+str(app_by)+"""</td></tr>
					"""
		
		

		elif state == 'cancel':
			body_part_3 = """
						<tr style="color:blue;"><td>Confirmed Date</td><td>:</td><td>"""+conf_date+"""</td></tr>
						<tr style="color:blue;"><td>Confirmed By</td><td>:</td><td>"""+str(conf_by)+"""</td></tr>
						<tr style="color:blue;"><td>Cancelled  Date</td><td>:</td><td>"""+str(cancel_date)+"""</td></tr>
						<tr style="color:blue;"><td>Cancelled By</td><td>:</td><td>"""+str(cancel_by)+"""</td></tr>
					"""
		
		
		
		body_part_4 = """</table>		   
			<br/>
			<br/>		  			
			<br/>
			<font size="2">** This Mail is auto generated by ERP System.</font></font>
			</body>
		</html>
		"""
	
		html = body_part_1+body_part_2+body_part_3 + body_part_4
		part2 = MIMEText(html, 'html')
		msg.attach(part2)	
		cc_mail_ids = "shubashri.s@kggroup.com,karthikeyan.subramani@kggroup.com"
		if state == "confirm":
			to_mails = "md@crossfieldsindia.com"
		else:
			to_mails = "accounts@crossfieldsindia.com,hr@crossfieldsindia.com"
			
		if to_mails:
			ir_mail_server = self.pool.get('ir.mail_server')
			msg = ir_mail_server.build_email(
					email_from = from_mailid,
					email_to = to_mails,
					subject = sub,
					body = html,
					email_cc = cc_mail_ids,
					object_id = res_id and ('%s-%s' % (res_id, 'kg.advacnce.deduction')),
					subtype = 'html',
					subtype_alternative = 'plain')
			
			res = ir_mail_server.send_email(cr, uid, msg,mail_server_id=1, context=context)
			print "Mail Successfully Sent To -------------->>", to_mails
			
		"""
		# Check Server Connection

		try:
			for i in mail_list:
				server = smtplib.SMTP('10.100.1.209')
				server.sendmail(from_mailid, i ,msg.as_string())
				print " Message............................",msg.as_string()
				print "Successfully sent email ---------------------To.........>>" 
		except Exception:
			pass
		"""
			
		return True			
		
	_constraints = [
		
		(_check_duplicate_entry, 'System not allow to save duplicate entries. Check Employee and Deduction Type !!',['amount']),
		(_zero_amount_check, 'System not allow to save entry with Zero value. !!',['amount']),
		(_validation_month_amount, 'Repay amount and periods are not matching !!',['amount']),
	#	(_approve_entry, 'Repay amount and periods are not matching !!',['amount']),
		
		] 
	
		
	def expire_entry(self, cr, uid, ids,context):
		print "expire_entry..........called................."
		entry = self.browse(cr,uid, ids[0])
		if entry.tot_amt == entry.amt_paid:
			self.write(cr, uid, ids, {'state': 'expire'})
		else:
			pass	
		
	def onchange_employee_code(self, cr, uid, ids, employee_id,emp_name, context=None):
		value = {'emp_name': ''}
		if employee_id:
			emp = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
			value = {'emp_name': emp.emp_code}
		return {'value': value}
		
	def onchange_repay_amount(self,cr,uid,ids ,tot_amt, period,context = None):
		print "onchange				 "
		print "entry..................		 ",tot_amt
		value = {'pay_amt' : (tot_amt/period)}
		return {'value' : value}
		
	def onchange_amount(self, cr, uid,ids,tot_amt,amt_paid, context=None):
		print "onchange_amount.................", tot_amt
		value = {'amt_paid': ''}
		if tot_amt:
			value = {'amt_paid': tot_amt}
		return {'value': value}			


		
	def create(self, cr, uid, vals,context=None):
		
		if vals.has_key('employee_id') and vals['employee_id']:
			emp_rec = self.pool.get('hr.employee').browse(cr,uid,vals['employee_id'])
			
			if emp_rec:
				vals.update({'emp_name':emp_rec.emp_code})		
		order =  super(kg_advance_deduction, self).create(cr, uid, vals, context=context)
		return order
		
	"""def write(self, cr, uid,ids, vals, context=None):
		if vals.has_key('employee_id') and vals['employee_id']:
			emp_rec = self.pool.get('hr.employee').browse(cr,uid,vals['employee_id'])
			if emp_rec:
				vals.update({'emp_name':emp_rec.name})						 
		res = super(kg_advance_deduction, self).write(cr, uid, ids,vals, context)		
		return res
		"""
	def unlink(self, cr, uid, ids, context=None):
		for entry in self.browse(cr, uid, ids, context=context):
			if entry.state == 'confirm':
				raise osv.except_osv(
				_('Invalid Action !'),
				_('You cannot delete this entry which is Confirmed !!'))
		return super(kg_advance_deduction, self).unlink(cr, uid, ids, context)	
	
kg_advance_deduction()
