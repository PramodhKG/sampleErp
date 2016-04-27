import time
from lxml import etree
from osv import fields, osv
from tools.translate import _
import pooler
import logging
import netsvc
import datetime
import StringIO
import base64
import mimetypes
import datetime as lastdate
import calendar

logger = logging.getLogger('server')


class kg_banklist_text_report(osv.osv):

	_name = 'kg.banklist.text.report'

	_columns = {
	
		'filter': fields.selection([('filter_date', 'Date')], "Filter by", required=True, readonly=True),
		'date_from': fields.date("Start Date",required=True, readonly=True,
					states={'draft':[('readonly',False)]}),
		'date_to': fields.date("End Date",required=True, readonly=True,
				states={'draft':[('readonly',False)]}),
		"rep_data":fields.binary("File"),
        "name":fields.char("Filename",16,readonly=True),
        'state': fields.selection([('draft', 'Draft'),('done','Done')], 'Status', readonly=True),
        'date': fields.date('Creation Date'),
        'bank_id': fields.many2one('res.bank', 'Bank Name', required=True,
						readonly=True, states={'draft':[('readonly',False)]}),
		'pay_sch': fields.selection([('5th','5th Pay Day'),('7th','7th Pay Day')], 'PaySchedule Selection',
						required=True, readonly=True, states={'draft':[('readonly',False)]}),
		
		}
		
	def _get_last_month_first(self, cr, uid, context=None):
		
		today = lastdate.date.today()
		print "today-----------", today
		first = lastdate.date(day=1, month=today.month, year=today.year)
		mon = today.month - 1
		if mon == 0:
			mon = 12
		else:
			mon = mon
		tot_days = calendar.monthrange(today.year,mon)[1]
		test = first - lastdate.timedelta(days=tot_days)
		res = test.strftime('%Y-%m-%d')
		print "---------------",res
		return res
		
	def _get_last_month_end(self, cr, uid, context=None):
		today = lastdate.date.today()
		first = lastdate.date(day=1, month=today.month, year=today.year)
		last = first - lastdate.timedelta(days=1)
		res = last.strftime('%Y-%m-%d')
		return res
		
		
	_defaults = {
	
		'filter': 'filter_date', 
		'date_from': _get_last_month_first,
		'date_to': _get_last_month_end,
		'date': time.strftime('%Y-%m-%d'),
		'state': 'draft',
	}
	   
	def _date_validation_check(self, cr, uid, ids, context=None):
		for val_date in self.browse(cr, uid, ids, context=context):
			if val_date.date_from <= val_date.date_to:
				return True
		return False
 
	_constraints = [
		(_date_validation_check, 'You must select an correct Start Date and End Date !!', ['Valid_date']),
	  ]
	  
		
	def produce_text_report(self, cr, uid, ids, context={}):
		
		bank_rec =self.browse(cr,uid,ids[0])
		date_from = bank_rec.date_from
		date_to = bank_rec.date_to
		date_from = "'"+date_from+"'"
		date_to = 	"'"+date_to+"'"
		pay_sch = bank_rec.pay_sch
		sch = "'"+pay_sch+"'"
		
		
		print "date_from..........."		,date_from
		print "date_to.........",date_to
			
		sql = """		
				SELECT distinct on (emp.id)
				slip.id AS sl_id,			  
				slip.round_val AS net_sal,			  			  
				emp.name_related as emp_name,
				con.acc_no AS bank_no

				FROM  hr_payslip slip
					
				JOIN hr_employee emp ON (emp.id=slip.employee_id)
				JOIN hr_contract con ON(con.id=slip.contract_id)
			 		 			  

				where slip.state='done' and slip.date_from >=%s and slip.date_to <=%s and
					con.bank=%s and con.sal_date=%s""" %(date_from,
								date_to,bank_rec.bank_id.id,sch)
						
		
		cr.execute(sql)		
		data = cr.dictfetchall()
		print "data ::::::::::::::=====>>>>", data
		file_path = open("/home/sengottuvelu/Projects/KG_HRM/bank_list.txt", 'w')
		gran_tot = 0.0
		for val in data:
			acc_no = val['bank_no']
			str_acc_no = str(acc_no)
			new_acc_no = str_acc_no.zfill(12)
			val['bank_no'] = new_acc_no
			amt = val['net_sal']
			amt = int(amt)
			str_amt = str(amt)			
			new_amt = str_amt.zfill(8)
			val['net_amt'] = new_amt
			name = val['emp_name']
			new_name = name.ljust(30)
			val['emp_name'] = new_name
			new_acc_no = str(new_acc_no)
			new_amt = str(new_amt)
			list_data = new_acc_no + new_name + new_amt
			file_path.write(list_data + '\n')
								
		file_path.close()		
		self.write(cr, uid, ids, {'name': 'Bank_list'+'.txt','rep_data':file_path ,'state': 'done'})		
		return data	
		
		
	def unlink(self, cr, uid, ids,context=None):
		for rec in self.browse(cr, uid, ids):
			print "rec.......", rec
			if rec.state == 'done':
				raise osv.except_osv(_('Unable to Delete !'),_('You can not delete Done state reports !!'))
		return super(kg_banklist_text_report, self).unlink(cr, uid, ids, context)	
			
kg_banklist_text_report()