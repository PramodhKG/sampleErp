import time
from lxml import etree
from osv import fields, osv
from tools.translate import _
import pooler
import logging
import netsvc
logger = logging.getLogger('server')


class kg_esi_wizard(osv.osv_memory):

	_name = 'kg.esi.wizard'

	_columns = {
	
		'dep_id':fields.many2many('hr.department','kg_esi_dep','wiz_id','dep_id','ESI Name'),
		'filter': fields.selection([('filter_date', 'Date')], "Filter by", required=True),
		'date_from': fields.date("Start Date"),
		'date_to': fields.date("End Date"),
		"rep_data":fields.binary("File",readonly=True),
        "name":fields.char("Filename",16,readonly=True),
		
		}
		
		
	_defaults = {
	
		'filter': 'filter_date', 
		'date_from': time.strftime('%Y-%m-%d'),
		'date_to': time.strftime('%Y-%m-%d'),
	}
	   
	def _date_validation_check(self, cr, uid, ids, context=None):
		for val_date in self.browse(cr, uid, ids, context=context):
			if val_date.date_from <= val_date.date_to:
				return True
		return False
 
	_constraints = [
		(_date_validation_check, 'You must select an correct Start Date and End Date !!', ['Valid_date']),
	  ]
	  
	  
	def _build_contexts(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
		result = {}
		result['date_from'] = 'date_from' in data['form'] and data['form']['date_from'] or False
		result['date_to'] = 'date_to' in data['form'] and data['form']['date_to'] or False
		if data['form']['filter'] == 'filter_date':
			result['date_from'] = data['form']['date_from']
			result['date_to'] = data['form']['date_to']
		return result
		
	def date_indian_format(self,date_pyformat):
		date_contents = date_pyformat.split("-")
		date_indian = date_contents[2]+"/"+date_contents[1]+"/"+date_contents[0]
		return date_indian
	  
	def check_report(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		data = {}
		data['ids'] = context.get('active_ids', [])
		data['model'] = context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(cr, uid, ids, [])[0]
		used_context = self._build_contexts(cr, uid, ids, data, context=context)
		data['form']['used_context'] = used_context
		return self._print_report(cr, uid, ids,data,context=context)
		
	def pre_print_report(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
		data['form'].update(self.read(cr, uid, ids, [], context=context)[0])
		return data	
			
	def produce_xls(self, cr, uid, ids, context={}):
		
		import StringIO
		import base64
		try:
			import xlwt
		except:
		   raise osv.except_osv('Warning !','Please download python xlwt module from\nhttp://pypi.python.org/packages/source/x/xlwt/xlwt-0.7.2.tar.gz\nand install it')
		wiz=self.browse(cr,uid,ids[0])
		where_sql = []
		
		if wiz.dep_id:
			for ids1 in wiz.dep_id:
				where_sql.append("emp.department_id = %s"%(ids1))			 
	   
		if where_sql:
			where_sql = ' and '+' and '.join(where_sql)
			
		else:
			where_sql=''		
		
		print "where_sql..................................", where_sql
			
		cr.execute('''
		
				SELECT 				
				slip.id AS slip_id,
				emp.name_related as emp_name,
				con.esi_acc_no as esi_no,
				con.wage as basic,
				con.allowance as allo,
				dep.name as dep_name,
				att.worked as worked				
							   
				FROM  hr_payslip slip
								
				join hr_employee emp on(emp.id=slip.employee_id)
				join hr_contract con on(con.employee_id=slip.employee_id)
				join kg_monthly_attendance att on(att.id=slip.att_id)
				join hr_department dep on(dep.id=emp.department_id)
				
				where slip.date_from >=%s and slip.date_to <=%s and slip.state = 'done' '''+ where_sql + '''
				''',(wiz.date_from,wiz.date_to))
				
		data = cr.dictfetchall()
		print "data <><><><><<><><><><<><><<>.........", data
		tot=0
		record={}
		sno=0
		wbk = xlwt.Workbook()
		style1 = xlwt.easyxf('font: bold on,height 240,color_index 0X36;' 'align: horiz center;''borders: left thin, right thin, top thin') 
		s1=0
		
		"""adding a worksheet along with name"""
		
		sheet1 = wbk.add_sheet('ESI Details')
		s2=1
		sheet1.col(0).width = 6000
		sheet1.col(1).width = 10000
		sheet1.col(2).width = 5000
		sheet1.col(3).width = 4000
		sheet1.col(4).width = 4000
		sheet1.col(5).width = 5000
		sheet1.col(6).width = 5500
		sheet1.col(7).width = 4000
		sheet1.col(8).width = 4000
		sheet1.col(9).width = 4000
		
		""" writing field headings """
		
		sheet1.write(s1,0,"ESI No",style1)
		sheet1.write(s1,1,"Employee Name",style1)
		sheet1.write(s1,2,"Basic",style1)
		sheet1.write(s1,3,"Allowance",style1)
		sheet1.write(s1,4,"Gross",style1)
		sheet1.write(s1,5,"ESI Amount",style1)
		sheet1.write(s1,6,"Deduction",style1)
		sheet1.write(s1,7,"Net Salary",style1)
		sheet1.write(s1,8,"No Of Working Days",style1)
		sheet1.write(s1,9,"Department",style1)
		
		"""writing data according to query and filteration in worksheet"""
		print "sheet1........................", sheet1
		for  ele in data:
			#print "ele////////////////////////",ele
			sheet1.write(s2,0,ele['esi_no'])
			sheet1.write(s2,1,ele['emp_name'])
			sheet1.write(s2,2,ele["basic"])
			sheet1.write(s2,3,ele['allo'])
			sheet1.write(s2,4,ele['esi_no'])
			sheet1.write(s2,5,ele['esi_no'])
			sheet1.write(s2,6,ele['esi_no'])
			sheet1.write(s2,7,ele['esi_no'])
			sheet1.write(s2,8,ele['worked'])
			sheet1.write(s2,9,ele['dep_name'])			
			s2+=1
			
		sheet1.write(s2+1,2,"Total",style1)
		sheet1.write(s2+1,3,ele['esi_no'])
		
		"""Parsing data as string """
		
		file_data=StringIO.StringIO()
		o=wbk.save(file_data)		
		"""string encode of data in wksheet"""		
		out=base64.encodestring(file_data.getvalue())
		#print "out ;;;;;;;;;;;;;;;;;;;;;;;;;-----", out		
		"""returning the output xls as binary"""
		print "ids......................"		, ids
		return self.write(cr, uid, ids, {'rep_data':out, 'name':'Test'+'.xls'})
		#return {'type': 'ir.actions.report.xml','rep_data':out, 'name':'Test'+'.xls'} 
		
		
	def _print_report(self, cr, uid, ids, data, context=None):
		if context is None:
			context = {}
		data = self.pre_print_report(cr, uid, ids, data, context=context)
		data['form'].update(self.read(cr, uid, ids)[0])
		if data['form']:
			date_from = str(data['form']['date_from'])
			date_to = str(data['form']['date_to'])
			data['form']['date_from_ind'] = self.date_indian_format(date_from)			
			data['form']['date_to_ind'] = self.date_indian_format(date_to)
			return {'type': 'ir.actions.report.xml', 'report_name': 'kg.otdays', 'datas': data}
			
kg_esi_wizard()