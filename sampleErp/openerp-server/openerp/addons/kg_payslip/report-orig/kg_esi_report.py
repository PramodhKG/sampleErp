import time
from lxml import etree
from osv import fields, osv
from tools.translate import _
import pooler
import logging
import netsvc
logger = logging.getLogger('server')


class kg_esi_report(osv.osv):

	_name = 'kg.esi.report'

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
		'date_from': time.strftime('%Y-%m-%d'),
		'date_to': time.strftime('%Y-%m-%d'),
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
		
		import StringIO
		import base64
		
		try:
			import xlwt
		except:
		   raise osv.except_osv('Warning !','Please download python xlwt module from\nhttp://pypi.python.org/packages/source/x/xlwt/xlwt-0.7.2.tar.gz\nand install it')
		
		esi_rec =self.browse(cr,uid,ids[0])
		date_from = esi_rec.date_from
		date_to = esi_rec.date_to
		date_from = "'"+date_from+"'"
		date_to = 	"'"+date_to+"'"
		
		print "date_from..........."		,date_from
		print "date_to.........",date_to
			
		sql = """		
				SELECT distinct on (emp.id)				
				slip.id AS slip_id,
				emp.name_related as emp_name,				
				con.esi_acc_no as esi_no,								
				dep.id as dep_id,
				dep.name as dep_name,
				att.worked as worked				
							   
				FROM  hr_payslip slip
								
				join hr_employee emp on(emp.id=slip.employee_id)
				join hr_contract con on(con.employee_id=slip.employee_id)
				join kg_monthly_attendance att on(att.id=slip.att_id)
				join hr_department dep on(dep.id=emp.department_id)				
				where slip.state='done' and slip.date_from=%s and slip.date_to=%s
				and con.esi=True """%(date_from,date_to)
		
		cr.execute(sql)		
		data = cr.dictfetchall()
		data.sort(key=lambda data: data['dep_id'])
		print "data <><><><><<><><><><<><><<>.........", data
		for slip in data:
			
			# Basic			
			basic_ids = self.pool.get('hr.payslip.line').search(cr, uid,[('slip_id','=',slip['slip_id']),
							('code','=','BASIC')])
			if basic_ids:
				basic_rec = self.pool.get('hr.payslip.line').browse(cr, uid, basic_ids[0])
				basic_amt = basic_rec.amount
				slip['basic'] = basic_amt
			else:
				pass
			
			# Allowance
							
			allowance_ids = self.pool.get('hr.payslip.line').search(cr, uid,[('slip_id','=',slip['slip_id']),
							('code','=','ALW')])
			if allowance_ids:
				allowance_rec = self.pool.get('hr.payslip.line').browse(cr, uid, allowance_ids[0])
				alw_amt = allowance_rec.amount
				slip['alw_amt'] = alw_amt
			else:
				pass
				
			slip['cross'] = slip['basic'] + slip['alw_amt']
			esi_amt = slip['cross'] * (1.75 /100.0)
			slip['esi_amt'] = (round(esi_amt,2))
			com_esi_amt = slip['cross'] * (4.75 / 100.0)
			slip['com_esi_amt'] =  (round(com_esi_amt,2))
			net = slip['cross'] - slip['esi_amt']
			slip['net'] = (round(net,2))
				
		record={}
		sno=0
		wbk = xlwt.Workbook()
		style1 = xlwt.easyxf('font: bold on,height 240,color_index 0X36;' 'align: horiz center;''borders: left thin, right thin, top thin') 
		s1=0
		
		"""adding a worksheet along with name"""
		
		sheet1 = wbk.add_sheet('ESI Details')
		s2=1
		sheet1.col(0).width = 6000
		sheet1.col(1).width = 8000
		sheet1.col(2).width = 5000
		sheet1.col(3).width = 4000
		sheet1.col(4).width = 4000
		sheet1.col(5).width = 5000
		sheet1.col(6).width = 5500
		sheet1.col(7).width = 4000
		sheet1.col(8).width = 4000
		sheet1.col(9).width = 4000
		sheet1.col(10).width = 8000
		
		""" writing field headings """
		
		sheet1.write(s1,0,"ESI No",style1)
		sheet1.write(s1,1,"Employee Name",style1)
		sheet1.write(s1,2,"Basic",style1)
		sheet1.write(s1,3,"Allowance",style1)
		sheet1.write(s1,4,"Gross",style1)
		sheet1.write(s1,5,"ESI Amount",style1)
		sheet1.write(s1,6,"4.75%",style1)
		sheet1.write(s1,7,"Deduction",style1)
		sheet1.write(s1,8,"Net Salary",style1)
		sheet1.write(s1,9,"No Of Working Days",style1)
		sheet1.write(s1,10,"Department",style1)
		
		"""writing data according to query and filteration in worksheet"""
		print "sheet1........................", sheet1
		for  ele in data:
			
			sheet1.write(s2,0,ele['esi_no'])
			sheet1.write(s2,1,ele['emp_name'])
			sheet1.write(s2,2,ele["basic"])
			sheet1.write(s2,3,ele['alw_amt'])
			sheet1.write(s2,4,ele['cross'])
			sheet1.write(s2,5,ele['esi_amt'])
			sheet1.write(s2,6,ele['com_esi_amt'])
			sheet1.write(s2,7,ele['esi_amt'])
			sheet1.write(s2,8,ele['net'])
			sheet1.write(s2,9,ele['worked'])
			sheet1.write(s2,10,ele['dep_name'])			
			s2+=1
			
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
		return super(kg_esi_report, self).unlink(cr, uid, ids, context)
	
	
			
kg_esi_report()