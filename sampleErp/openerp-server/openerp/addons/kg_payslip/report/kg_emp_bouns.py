import time
from lxml import etree
from tools.translate import _
import pooler
import logging
import netsvc
import calendar
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale
from dateutil import rrule
from datetime import datetime, timedelta
import datetime as idt
from openerp.osv import osv, fields


logger = logging.getLogger('server')


class kg_emp_bouns(osv.osv):

	_name = 'kg.emp.bouns'

	_columns = {
	
		'filter': fields.selection([('filter_date', 'Date')], "Filter by", required=True, readonly=True),
		'date_from': fields.date("Start Date",required=True, readonly=True,
					states={'draft':[('readonly',False)]}),
		'date_to': fields.date("End Date",required=True, readonly=True,
				states={'draft':[('readonly',False)]}),
		"rep_data":fields.binary("File",readonly=True),
        "name":fields.char("Filename",16,readonly=True),
        'state': fields.selection([('draft', 'Draft'),('done','Done')], 'Status', readonly=True),
        'date': fields.date('Creation Date'),
		
		}
		
	
		
	_defaults = {
	
		'filter': 'filter_date', 
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
	  
		
	def produce_xls(self, cr, uid, ids, context={}):
		
		bouns_rec = self.browse(cr, uid, ids[0])
		
		from_date = bouns_rec.date_from
		to_date = bouns_rec.date_to
		
		
		import StringIO
		import base64
		
		try:
			import xlwt
		except:
		   raise osv.except_osv('Warning !','Please download python xlwt module from\nhttp://pypi.python.org/packages/source/x/xlwt/xlwt-0.7.2.tar.gz\nand install it')	
			
		sql = """		
				SELECT distinct on (emp.id)				
				emp.id as emp_id,
				emp.name_related as name,
				emp.emp_code as code,
				con.wage as basic,
				con.allowance as alw

				FROM  hr_employee emp
				
				JOIN hr_contract con ON(con.employee_id=emp.id)
				JOIN kg_monthly_attendance att ON(att.employee_id=emp.id)
				JOIN hr_payslip slip ON(slip.employee_id=emp.id)								
				where payslip=True order by emp.id limit 5 """
		
		cr.execute(sql)		
		data = cr.dictfetchall()
		#data.sort(key=lambda data: data['dep_id'])
		print "data <><><><><<><><><><<><><<>.........", data
		
		#from_date = form['date_from']
		#to_date = form['date_to']
		print "from_date...............................", from_date
		print "to_date...............................", to_date
		att_obj = self.pool.get('kg.monthly.attendance')
		
		for ele in data:
			emp_id = ele['emp_id']
			one_day_basic = ele['basic'] / 26
			print "Looping............", ele
			ele['name'] = ele['name']				
			ele['code'] = ele['code']				
			
			from_dt = idt.datetime.strptime(from_date, '%Y-%m-%d').strftime('%m/%d/%Y')
			from_dt = (idt.datetime.strptime(from_dt, '%m/%d/%Y'))
			to_dt = idt.datetime.strptime(to_date, '%Y-%m-%d').strftime('%m/%d/%Y')
			to_dt = (idt.datetime.strptime(to_dt, '%m/%d/%Y'))
			
			for dt in rrule.rrule(rrule.MONTHLY, dtstart=from_dt, until=to_dt):
				print "------------------------dt-----", dt					
				att_id = att_obj.search(cr, uid, [('employee_id','=',emp_id),
							('start_date','=',dt),('state','=','confirm')])
				print "att_id................", att_id
				if att_id:
					att_rec = att_obj.browse(cr, uid,att_id[0])
					worked = att_rec.mon_tot_days
					print "worked..........................", worked
				else:
					worked = 0				
					
				ele['month'] = dt.strftime('%B')
				print "ele['month'] ----------------------.........", ele['month']
				ele['worked1'] = 0					
				ele['worked2'] = 0					
				ele['worked3'] = 0					
				ele['worked4'] = 0					
				ele['worked5'] = 0					
				ele['worked6'] = 0					
				ele['worked7'] = 0					
				ele['worked8'] = 0					
				ele['worked9'] = 0					
				ele['worked10'] = 0					
				ele['worked11'] = 0					
				ele['worked12'] = 0					
				ele['amt'] = 0
				ele['bouns_amt'] = 0
				if ele['month'] == 'January':
					ele['worked1'] = worked
					ele['month'] = 'Jan'
					if worked > 26:							
						basic_amt = 26 * one_day_basic
						ele['basic_amt1'] = basic_amt
					else:
						basic_amt = worked * one_day_basic
						ele['basic_amt1'] = basic_amt
											
				elif ele['month'] == 'February':
					ele['month'] = 'Feb'
					ele['worked2'] = worked
					if worked > 26:							
						basic_amt = 26 * one_day_basic
						ele['basic_amt2'] = basic_amt
					else:
						basic_amt = worked * one_day_basic
						ele['basic_amt2'] = basic_amt
						
				elif ele['month'] == 'March':
					ele['month'] = 'Mar'
					ele['worked3'] = worked
					if worked > 26:							
						basic_amt = 26 * one_day_basic
						ele['basic_amt3'] = basic_amt
					else:
						basic_amt = worked * one_day_basic
						ele['basic_amt3'] = basic_amt
				
				elif ele['month'] == 'April':
					ele['month'] = 'Apr'
					ele['worked4'] = worked
					if worked > 26:							
						basic_amt = 26 * one_day_basic
						ele['basic_amt4'] = basic_amt
					else:
						basic_amt = worked * one_day_basic
						ele['basic_amt4'] = basic_amt
						
				elif ele['month'] == 'May':
					ele['worked5'] = worked
					if worked > 26:							
						basic_amt = 26 * one_day_basic
						ele['basic_amt5'] = basic_amt
					else:
						basic_amt = worked * one_day_basic
						ele['basic_amt5'] = basic_amt
						
				elif ele['month'] == 'June':
					ele['worked6'] = worked
					if worked > 26:							
						basic_amt = 26 * one_day_basic
						ele['basic_amt6'] = basic_amt
					else:
						basic_amt = worked * one_day_basic
						ele['basic_amt6'] = basic_amt
						
				elif ele['month'] == 'July':
					ele['worked7'] = worked
					if worked > 26:							
						basic_amt = 26 * one_day_basic
						ele['basic_amt7'] = basic_amt
					else:
						basic_amt = worked * one_day_basic
						ele['basic_amt7'] = basic_amt
						
				elif ele['month'] == 'August':
					ele['worked8'] = worked
					if worked > 26:							
						basic_amt = 26 * one_day_basic
						ele['basic_amt8'] = basic_amt
					else:
						basic_amt = worked * one_day_basic
						ele['basic_amt8'] = basic_amt
						
				elif ele['month'] == 'September':
					ele['worked9'] = worked
					if worked > 26:							
						basic_amt = 26 * one_day_basic
						ele['basic_amt9'] = basic_amt
					else:
						basic_amt = worked * one_day_basic
						ele['basic_amt9'] = basic_amt
						
				elif ele['month'] == 'October':
					ele['worked10'] = worked
					if worked > 26:							
						basic_amt = 26 * one_day_basic
						ele['basic_amt10'] = basic_amt
					else:
						basic_amt = worked * one_day_basic
						ele['basic_amt10'] = basic_amt
						
				elif ele['month'] == 'November':
					ele['worked11'] = worked
					if worked > 26:							
						basic_amt = 26 * one_day_basic
						ele['basic_amt11'] = basic_amt
					else:
						basic_amt = worked * one_day_basic
						ele['basic_amt11'] = basic_amt
						
				elif ele['month'] == 'December':
					ele['worked12'] = worked
					if worked > 26:							
						basic_amt = 26 * one_day_basic
						ele['basic_amt12'] = basic_amt
					else:
						basic_amt = worked * one_day_basic
						ele['basic_amt12'] = basic_amt
				else:
					print "No months"
			
		
				
		record={}
		sno=0
		wbk = xlwt.Workbook()
		style1 = xlwt.easyxf('font: bold on,height 240,color_index 0X36;' 'align: horiz center;''borders: left thin, right thin, top thin') 
		s1=0
		
		"""adding a worksheet along with name"""
		
		sheet1 = wbk.add_sheet('Bouns Report')
		s2=1
		s3=2
		sheet1.col(0).width = 8000
		sheet1.col(1).width = 5000
		sheet1.col(2).width = 4000
		sheet1.col(3).width = 4000
		sheet1.col(4).width = 5000
		sheet1.col(5).width = 5500
		sheet1.col(6).width = 4000
		sheet1.col(7).width = 4000
		sheet1.col(8).width = 4000
		sheet1.col(9).width = 8000
		sheet1.col(10).width = 8000
		sheet1.col(11).width = 8000
		sheet1.col(12).width = 8000
		sheet1.col(13).width = 8000
		sheet1.col(14).width = 8000
		sheet1.col(15).width = 8000
		
		
		sheet1.write(s1,0,"Employee Yearly Bouns Report",style1)

		""" writing field headings """
		
		sheet1.write(s2,0,"Employee Code",style1)
		sheet1.write(s2,1,"Employee Name",style1)
		sheet1.write(s2,2,"Jan",style1)
		sheet1.write(s2,3,"Feb",style1)
		sheet1.write(s2,4,"Mar",style1)
		sheet1.write(s2,5,"Apr",style1)
		sheet1.write(s2,6,"May",style1)
		sheet1.write(s2,7,"Jun",style1)
		sheet1.write(s2,8,"Jul",style1)
		sheet1.write(s2,9,"Aug",style1)
		sheet1.write(s2,10,"Sep",style1)
		sheet1.write(s2,11,"Oct",style1)
		sheet1.write(s2,12,"Nov",style1)
		sheet1.write(s2,13,"Dec",style1)
		sheet1.write(s2,14,"Total Amt",style1)
		sheet1.write(s2,15,"Bouns Amt",style1)
		
		
		"""writing data according to query and filteration in worksheet"""
		print "sheet1........................", sheet1
		for  ele in data:
			print "ele--------------------->>>", ele
			sheet1.write(s3,0,ele['code'])
			sheet1.write(s3,1,ele["name"])
			sheet1.write(s3,2,ele['month'])
			sheet1.write(s3,3,ele['worked2'])
			sheet1.write(s3,4,ele['worked3'])
			sheet1.write(s3,5,ele['worked4'])
			sheet1.write(s3,6,ele['worked5'])
			sheet1.write(s3,7,ele['worked6'])
			sheet1.write(s3,8,ele['worked7'])
			sheet1.write(s3,9,ele['worked8'])			
			sheet1.write(s3,10,ele['worked9'])
			sheet1.write(s3,11,ele['worked10'])
			sheet1.write(s3,12,ele['worked11'])
			sheet1.write(s3,13,ele['worked12'])
			sheet1.write(s3,14,ele['amt'])
			sheet1.write(s3,15,ele['bouns_amt'])
			
			s3+=1
			
		#sheet1.write(s2+1,2,"Total",style1)
		#sheet1.write(s2+1,3,ele['esi_no'])
		
		"""Parsing data as string """
		cur_mon = time.strftime('%Y-%B')
		file_data=StringIO.StringIO()
		o=wbk.save(file_data)		
		"""string encode of data in wksheet"""		
		out=base64.encodestring(file_data.getvalue())
		"""returning the output xls as binary"""
		return self.write(cr, uid, ids, {'rep_data':out, 'name': 'ESI_Report'+'.xls','state': 'done'})
		
	def unlink(self, cr, uid, ids,context=None):
		for rec in self.browse(cr, uid, ids):
			print "rec.......", rec
			if rec.state == 'done':
				raise osv.except_osv(_('Unale to Delete !'),_('You can not delete Done state reports !!'))
		return super(kg_emp_bouns, self).unlink(cr, uid, ids, context)
	
	
			
kg_emp_bouns()