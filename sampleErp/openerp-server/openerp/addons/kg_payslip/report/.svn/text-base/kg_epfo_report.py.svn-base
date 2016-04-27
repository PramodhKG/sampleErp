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


class kg_epfo_report(osv.osv):

	_name = 'kg.epfo.report'

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
				to_char(emp.res_date,'dd/mm/yyyy') AS res_date,
				emp.res_reason as res_remark,
				emp.gender as sex,
				to_char(emp.cer_dob_date,'dd/mm/yyyy') AS birthday,
				emp.father_name as wi_hus,
				emp.relation as relation,
				con.pf_acc_no as pf_no,
				to_char(con.pf_eff_date,'dd/mm/yyyy') AS eff_date,
				con.wage as basic,								
				att.mon_tot_days as worked,
				dep.name as dep_name				
							   
				FROM  hr_payslip slip
								
				join hr_employee emp on(emp.id=slip.employee_id)
				join hr_contract con on(con.employee_id=slip.employee_id)
				join hr_department dep on(dep.id=slip.dep_id)
				join kg_monthly_attendance att on(att.id=slip.att_id)				
				where slip.state='done' and slip.date_from=%s and slip.date_to=%s
				and con.pf_status=True """%(date_from,date_to)
		
		cr.execute(sql)		
		data = cr.dictfetchall()
		#data.sort(key=lambda data: data['dep_id'])
		print "data <><><><><<><><><><<><><<>.........", data
		for slip in data:	
			
			mon_tot_days = slip['worked']
			one_day_basic = slip['basic'] / 26
			if mon_tot_days < 26:								
				pf_basic = one_day_basic * mon_tot_days				
				basic_amt = (round(pf_basic))
				pf_amt = pf_basic * 12 / 100
				if pf_basic > 6500:
					eps_amt = 6500 * 8.33 / 100
				else:
					eps_amt = pf_basic * 8.33 / 100
			else:
				basic_amt =  slip['basic']
				pf_amt = slip['basic'] * 12 / 100
				if slip['basic'] > 6500:
					eps_amt = 6500 * 8.33 / 100
				else:
					eps_amt = slip['basic'] * 8.33 / 100	
			
			
			pf_amt = (round(pf_amt))
			eps_amt = (round(eps_amt))
			print "pf_amt....................", pf_amt
			slip['basic_amt'] = basic_amt
			slip['epf_amt'] = pf_amt				
			slip['eps_amt'] = eps_amt
			
			slip['diff_amt'] = pf_amt - eps_amt
			slip['nu_amt'] = ''
			slip['relation'] = 'Father'
			if slip['worked'] >= 26:
				slip['ncp_days'] = 0
			else:
				slip['ncp_days'] = 26 - slip['worked']				
			
			month_date = esi_rec.date_from
			a = unidate.datetime.strptime(slip['eff_date'], '%d/%m/%Y').strftime('%Y-%m-%d')
			rep_date = datetime.strptime(month_date,'%Y-%m-%d').date()
			eff_date = datetime.strptime(a,'%Y-%m-%d').date()
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
		sheet1.col(2).width = 5000
		sheet1.col(3).width = 4000
		sheet1.col(4).width = 5000
		sheet1.col(5).width = 5000
		sheet1.col(6).width = 5500
		sheet1.col(7).width = 5000
		sheet1.col(8).width = 4000
		sheet1.col(9).width = 4000
		sheet1.col(10).width = 4000
		sheet1.col(11).width = 4000
		sheet1.col(12).width = 4000
		sheet1.col(13).width = 4000
		sheet1.col(14).width = 4000
		sheet1.col(15).width = 4000
		sheet1.col(16).width = 4000
		sheet1.col(17).width = 4000
		sheet1.col(18).width = 4000
		sheet1.col(19).width = 4000
		sheet1.col(20).width = 4000
		sheet1.col(21).width = 4000
		sheet1.col(22).width = 4000
		sheet1.col(23).width = 4000
		sheet1.col(24).width = 4000
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
		sheet1.write(s1,11,"Refund of Advances",style1)
		sheet1.write(s1,12,"Arrear EPF Wages",style1)
		sheet1.write(s1,13,"Arrear EPF EE Share",style1)
		sheet1.write(s1,14,"Arrear EPF ER Share",style1)
		sheet1.write(s1,15,"Arrear EPS Share",style1)
		sheet1.write(s1,16,"Father's/Husband's Name",style1)
		sheet1.write(s1,17,"Relationship with the Member",style1)
		sheet1.write(s1,18,"Date of Birth",style1)
		sheet1.write(s1,19,"Gender",style1)
		sheet1.write(s1,20,"Date of Joining EPF",style1)
		sheet1.write(s1,21,"Date of Joining EPS",style1)
		sheet1.write(s1,22,"Date of Exit from EPF",style1)
		sheet1.write(s1,23,"Date of Exit from EPS",style1)
		sheet1.write(s1,24,"Reason for Leaving",style1)
		
		"""writing data according to query and filteration in worksheet"""
		print "sheet1........................", sheet1
		for ele in data:			
			sheet1.write(s2,0,ele['pf_no'])
			sheet1.write(s2,1,ele['emp_name'])
			sheet1.write(s2,2,ele['basic_amt'])
			sheet1.write(s2,3,ele['basic_amt'])
			sheet1.write(s2,4,ele['epf_amt'])
			sheet1.write(s2,5,ele['epf_amt'])
			sheet1.write(s2,6,ele['eps_amt'])
			sheet1.write(s2,7,ele['eps_amt'])
			sheet1.write(s2,8,ele['diff_amt'])
			sheet1.write(s2,9,ele['diff_amt'])
			sheet1.write(s2,10,ele['ncp_days'])			
			sheet1.write(s2,11,ele['nu_amt'])			
			sheet1.write(s2,12,ele['nu_amt'])			
			sheet1.write(s2,13,ele['nu_amt'])			
			sheet1.write(s2,14,ele['nu_amt'])			
			sheet1.write(s2,15,ele['nu_amt'])			
			sheet1.write(s2,16,ele['wi_hus'])			
			sheet1.write(s2,17,ele['relation'])			
			sheet1.write(s2,18,ele['birthday'])			
			sheet1.write(s2,19,ele['sex'])			
			sheet1.write(s2,20,ele['eff_date'])			
			sheet1.write(s2,21,ele['eff_date'])			
			sheet1.write(s2,22,ele['res_date'])			
			sheet1.write(s2,23,ele['res_date'])			
			sheet1.write(s2,24,ele['res_remark'])			
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
		return self.write(cr, uid, ids, {'rep_data':out, 'name': 'EPFO_Report'+'.xls','state': 'done'})
		
	def unlink(self, cr, uid, ids,context=None):
		for rec in self.browse(cr, uid, ids):
			print "rec.......", rec
			if rec.state == 'done':
				raise osv.except_osv(_('Unale to Delete !'),_('You can not delete Done state reports !!'))
		return super(kg_epfo_report, self).unlink(cr, uid, ids, context)	
			
kg_epfo_report()