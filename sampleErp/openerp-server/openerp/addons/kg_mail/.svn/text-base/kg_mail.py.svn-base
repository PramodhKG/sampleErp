from osv import fields,osv
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

class kg_mail(osv.osv):
	
	_name = 'hr.employee'	
	_inherit = 'hr.employee'
	
	_columns = {
	
	'email_field': fields.text('Email Content', size=128),	
	'state': fields.selection([('draft','Draft'),('confirm','Entry Confirmed')], 'Status'),
	
	}

	def confirm_entry(self, cr, uid, ids,context=None):	
		
		entry = self.browse(cr,uid,ids[0])
		obj = self.pool.get('hr.employee')
		name = entry.name
		print name
		code = str(entry.emp_code)
		dept = str(entry.department_id.name)
		mail_id = str(entry.work_email)
		company = str(entry.address_id.name)
		content=str(entry.email_field)

		
		msg="Subject : Welcome To "+company+" \nWe are very pleased to have you as a part of our organisation \nHello "+name+"\nYour ID:  "+code+"\nDepartment : "+dept+"\nEmail address :  "+mail_id+"\nEmail Content   "+content  

		print msg
		
	
		smtpObj = smtplib.SMTP('10.100.1.123')
		smtpObj.sendmail("hr@clinsynccro.com",mail_id, msg)
		print "Successfully sent email"
		

		
		return True	
		
		
	
	
kg_mail()
