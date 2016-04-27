import time
from lxml import etree
from osv import fields, osv
from tools.translate import _
import pooler
import logging
import netsvc
import calendar
from datetime import datetime
import datetime as unidate
import datetime as lastdate

logger = logging.getLogger('server')


class kg_excel_pf_report(osv.osv):

	_name = 'kg.excel.pf.report'

	_columns = {
	
		'filter': fields.selection([('filter_date', 'Date')], "Filter by", required=True, readonly=True),
		'month': fields.selection([('1','Jan'),('2','Feb'),('3','March'),('4','Apr'),
									('5','May'),('6','June'),('7','July'),('8','Aug'),
									('9','Sep'),('10','Oct'),('11','Nov'),('12','Dec')],'Month', required=True,
									states={'draft':[('readonly',False)]}),
		'year':fields.integer('Year',size = 4,states={'draft':[('readonly',False)]}),
		"rep_data":fields.binary("File",readonly=True),
        "name":fields.char("Filename",16,readonly=True),
        'state': fields.selection([('draft', 'Draft'),('done','Done')], 'Status', readonly=True),
        'date': fields.date('Creation Date'),
		
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
		'month': '1',
		'year': 2014,
		'date': time.strftime('%Y-%m-%d'),
		'state': 'draft',
	}
	   
	def _date_validation_check(self, cr, uid, ids, context=None):
		for val_date in self.browse(cr, uid, ids, context=context):
			if val_date.date_from <= val_date.date_to:
				return True
		return False
 
	_constraints = [
		#(_date_validation_check, 'You must select an correct Start Date and End Date !!', ['Valid_date']),
	  ]
	  
		
	def produce_xls(self, cr, uid, ids, context={}):
		
		import StringIO
		import base64
		
		try:
			import xlwt
		except:
		   raise osv.except_osv('Warning !','Please download python xlwt module from\nhttp://pypi.python.org/packages/source/x/xlwt/xlwt-0.7.2.tar.gz\nand install it')
		
		pf_rec =self.browse(cr,uid,ids[0])
		month = pf_rec.month
		year = pf_rec.year
		#date_from = "'"+date_from+"'"
		#date_to = 	"'"+date_to+"'"
		
		print "date_from..........."		,month
		print "date_to.........",year
			
		sql = """		
				SELECT distinct on (emp.id)				
						slip.id AS slip_id,
						emp.name_related as emp_name,
						to_char(emp.join_date,'dd/mm/yyyy') AS res_date,
						emp.res_reason as res_remark,
						emp.gender as gender,
						to_char(emp.cer_dob_date,'dd/mm/yyyy') AS birthday,
						emp.father_name as father_name,
						emp.relation as relation,
						con.pf_acc_no as pf_no,
						to_char(con.pf_eff_date,'dd/mm/yyyy') AS eff_date,
						con.wage as basic,								
						att.worked as worked,
						dep.name as dep_name				
									   
						FROM  hr_payslip slip
										
						left join hr_employee emp on(emp.id=slip.employee_id)
						left join hr_contract con on(con.employee_id=slip.employee_id)
						left join kg_salary_detail det on (con.id = det.salary_id)
						left join hr_department dep on(dep.id=slip.dep_id)
						left join kg_monthly_attendance att on(att.employee_id=slip.employee_id)				
						where slip.state='done' and extract(month from slip.date_from) =%s and extract(year from slip.date_to) =%s
						and con.pf_status=True"""%(month,year)
		
		cr.execute(sql)		
		data = cr.dictfetchall()
		#data.sort(key=lambda data: data['dep_id'])
		print "data <><><><><<><><><><<><><<>.........", data
		epf_wages = 0.00
		pf_amt = 0.00
		eps_amt = 0.00
		i=0
		
		slip_obj = self.pool.get('hr.payslip.line')
		emp_con_obj = self.pool.get('kg.employee.contribution')
		#emp_line_obj = self.pool.get('kg.employee.contribution.line')		
		#emp_con_ids = emp_con_obj.search(cr,uid,[('active','=',True)])
		#emp_con_lin = emp_con_rec.search(cr,uid,['cont_line_entry','=',emp_con_ids[0]])
		
		
		for slip in data:			
			
			sal_basic_ids = slip_obj.search(cr,uid,[('slip_id','=',slip['slip_id']),('code','=','BASIC')])
			sal_da_ids = slip_obj.search(cr,uid,[('slip_id','=',slip['slip_id']),('code','=','DA')])
			sal_pf_ids = slip_obj.search(cr,uid,[('slip_id','=',slip['slip_id']),('code','=','PF')])
			
			srch_basic_rec = slip_obj.browse(cr,uid,sal_basic_ids[0])
			srch_da_rec = slip_obj.browse(cr,uid,sal_da_ids[0])
			if sal_pf_ids:
				srch_pf_rec = slip_obj.browse(cr,uid,sal_pf_ids[0])
			
			
			epf_wages = srch_basic_rec.amount + srch_da_rec.amount
			if sal_pf_ids:
				pf_amt = srch_pf_rec.amount
			else:
				pf_amt = 0.00
			eps_amt = (epf_wages * 8.33)/100
			acc_amt_1 = (epf_wages * 1.1)/100
			acc_amt_2 = (epf_wages * 0.5)/100
			acc_amt_3 = (epf_wages * 0.01)/100
			
			
			"""while (len(emp_con_lin) > i):
				emp_con_rec = emp_line_obj.browse(cr,uid,emp_con_lin[i])
				if emp_con_rec.emp_contribution == 'pf':
					if emp_con_rec.cont_type == 'fixed_amt':
						emp_con_per = emp_con_rec.contribution_percentage
					else:
						emp_con_per = emp_con_rec.contribution_percentage / 100"""
			
			
			print "pf_amt           ",pf_amt
			worked = slip['worked']
			print "salip    ",slip['eff_date']
			
			pf_amt = (round(pf_amt))
			eps_amt = (round(eps_amt))
			print "pf_amt....................", pf_amt
			slip['epf_wages'] = epf_wages
			slip['epf_amt'] = pf_amt				
			slip['eps_amt'] = eps_amt
			
			slip['diff_amt'] = pf_amt - eps_amt
			slip['nu_amt'] = ''
			slip['relation'] = 'Father'
			if slip['worked'] >= 26:
				slip['ncp_days'] = 0
			else:
				slip['ncp_days'] = 26 - slip['worked']	
				
			slip['acc_amt_1'] = acc_amt_1			
			slip['acc_amt_2'] = acc_amt_2
			slip['acc_amt_3'] = acc_amt_3			
			
			month_date = pf_rec.month
			year = pf_rec.year
			a = unidate.datetime.strptime(slip['eff_date'], '%d/%m/%Y').strftime('%Y-%m')
			rep_date = datetime.strptime(month_date,'%m')
			eff_date = datetime.strptime(a,'%m')
			#rep_date = pf_rec.date_from
			#eff_date = slip['eff_date']
			
			if rep_date != eff_date:
				slip['wi_hus'] = ''
				slip['relation'] = ''
				slip['birthday'] = ''
				slip['sex'] = ''
				slip['eff_date'] = ''
			else:
				pass
				
			if slip['res_remark'] and slip['res_remark'] == 'a':
				slip['res_remark'] = 'A'
			elif slip['res_remark'] and slip['res_remark'] == 'b':
				slip['res_remark'] = 'B'
			elif slip['res_remark'] and slip['res_remark'] == 'c':
				slip['res_remark'] = 'C'
			elif slip['res_remark'] and slip['res_remark'] == 'd':
				slip['res_remark'] = 'D'
			else:
				slip['res_remark'] = ''
					
				
		record={}
		sno=0
		wbk = xlwt.Workbook()
		style1 = xlwt.easyxf('font: bold on,height 240,color_index 0X36;' 'align: horiz center;''borders: left thin, right thin, top thin') 
		s1=0
		
		"""adding a worksheet along with name"""
		
		sheet1 = wbk.add_sheet('EPFO Details')
		s2=1
		sheet1.col(0).width = 6000
		sheet1.col(1).width = 8000
		sheet1.col(2).width = 8000
		sheet1.col(3).width = 8000
		sheet1.col(4).width = 8000
		sheet1.col(5).width = 8000
		sheet1.col(6).width = 8000
		sheet1.col(7).width = 8000
		sheet1.col(8).width = 8000
		sheet1.col(9).width = 8000
		sheet1.col(10).width = 8000
		sheet1.col(11).width = 8000
		sheet1.col(12).width = 8000
		sheet1.col(13).width = 8000
		sheet1.col(14).width = 8000
		sheet1.col(15).width = 8000
		sheet1.col(16).width = 8000
		sheet1.col(17).width = 8000
		sheet1.col(18).width = 8000
		sheet1.col(19).width = 8000
		sheet1.col(20).width = 8000
		sheet1.col(21).width = 8000
		sheet1.col(22).width = 8000
		sheet1.col(23).width = 8000
		sheet1.col(24).width = 8000
		sheet1.col(25).width = 8000
		sheet1.col(26).width = 8000
		sheet1.col(27).width = 8000
		sheet1.col(28).width = 8000
		""" writing field headings """
		
		sheet1.write(s1,0,"MEMBER ID",style1)
		sheet1.write(s1,1,"MEMBER Name",style1)
		sheet1.write(s1,2,"EPF WAGES",style1)
		sheet1.write(s1,3,"EPS WAGES",style1)
		sheet1.write(s1,4,"EPF Contribution(EE Share)due",style1)
		sheet1.write(s1,5,"EPF Contribution(EE Share)being remitted",style1)
		sheet1.write(s1,6,"EPS Contribution due",style1)
		sheet1.write(s1,7,"EPS Contribution being remitted",style1)
		sheet1.write(s1,8,"Diff EPF and EPS Contribution(ER Share)due",style1)
		sheet1.write(s1,9,"Diff EPD and EPS Contribution(ER Share )Being remitted",style1)
		sheet1.write(s1,10,"NCP days",style1)
		sheet1.write(s1,11,"A/c 2 1.1%",style1)
		sheet1.write(s1,12,"A/c 21 0.5%",style1)
		sheet1.write(s1,13,"A/c 22 0.01%",style1)
		sheet1.write(s1,14,"Refund of Advances",style1)
		sheet1.write(s1,15,"Arrear EPF Wages",style1)
		sheet1.write(s1,16,"Arrear EPF EE Share",style1)
		sheet1.write(s1,17,"Arrear EPF ER Share",style1)
		sheet1.write(s1,18,"Arrear EPS Share",style1)
		sheet1.write(s1,19,"Father's/Husband's Name",style1)
		sheet1.write(s1,20,"Relationship with the Member",style1)
		sheet1.write(s1,21,"Date of Birth",style1)
		sheet1.write(s1,22,"Gender",style1)
		sheet1.write(s1,23,"Date of Joining EPF",style1)
		sheet1.write(s1,24,"Date of Joining EPS",style1)
		sheet1.write(s1,25,"Date of Exit from EPF",style1)
		sheet1.write(s1,26,"Date of Exit from EPS",style1)
		sheet1.write(s1,27,"Reason for Leaving",style1)
		
		"""writing data according to query and filteration in worksheet"""
		print "sheet1........................", sheet1
		for ele in data:			
			print "ele data   ",ele['pf_no']
			sheet1.write(s2,0,ele['pf_no'])
			sheet1.write(s2,1,ele['emp_name'])
			sheet1.write(s2,2,ele['epf_wages'])
			sheet1.write(s2,3,ele['epf_wages'])
			sheet1.write(s2,4,ele['epf_amt'])
			sheet1.write(s2,5,ele['epf_amt'])
			sheet1.write(s2,6,ele['eps_amt'])
			sheet1.write(s2,7,ele['eps_amt'])
			sheet1.write(s2,8,ele['diff_amt'])
			sheet1.write(s2,9,ele['diff_amt'])
			sheet1.write(s2,10,ele['ncp_days'])			
			sheet1.write(s2,11,ele['acc_amt_1'])			
			sheet1.write(s2,12,ele['acc_amt_2'])			
			sheet1.write(s2,13,ele['acc_amt_3'])			
			sheet1.write(s2,14,ele['nu_amt'])			
			sheet1.write(s2,15,ele['nu_amt'])			
			sheet1.write(s2,16,ele['nu_amt'])			
			sheet1.write(s2,17,ele['nu_amt'])			
			sheet1.write(s2,18,ele['nu_amt'])			
			sheet1.write(s2,19,ele['wi_hus'])			
			sheet1.write(s2,20,ele['relation'])			
			sheet1.write(s2,21,ele['birthday'])			
			sheet1.write(s2,22,ele['sex'])			
			sheet1.write(s2,23,ele['eff_date'])			
			sheet1.write(s2,24,ele['eff_date'])			
			sheet1.write(s2,25,ele['res_date'])			
			sheet1.write(s2,26,ele['res_date'])				
			sheet1.write(s2,27,ele['res_remark'])				
			s2+=1
			
			print "ele data   ",ele['res_date']
		#sheet1.write(s2+1,2,"Total",style1)
		#sheet1.write(s2+1,3,ele['esi_no'])
		
		"""Parsing data as string """
		#cur_mon = time.strftime('%Y-%B')
		file_data=StringIO.StringIO()
		o=wbk.save(file_data)		
		"""string encode of data in wksheet"""		
		out=base64.encodestring(file_data.getvalue())
		"""returning the output xls as binary"""
		
		return self.write(cr, uid, ids, {'rep_data':out, 'name': 'EPFO_Excel_Report'+'.xls','state': 'done'})
		
	def unlink(self, cr, uid, ids,context=None):
		for rec in self.browse(cr, uid, ids):
			print "rec.......", rec
			if rec.state == 'done':
				raise osv.except_osv(_('Unale to Delete !'),_('You can not delete Done state reports !!'))
		return super(kg_excel_pf_report, self).unlink(cr, uid, ids, context)
			
kg_excel_pf_report()
