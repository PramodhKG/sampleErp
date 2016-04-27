import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_esi_pdf_report(report_sxw.rml_parse):
	
	_name = 'kg.esi.pdf.report'
	_inherit='hr.payslip'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_esi_pdf_report, self).__init__(cr, uid, name, context=context)
		self.query = ""
		self.period_sql = ""
		self.localcontext.update( {
			'time': time,
			'get_filter': self._get_filter,
			'get_start_date':self._get_start_date,
			'get_end_date':self._get_end_date,
			'get_data':self.get_data,
			'locale':locale,
		})
		self.context = context
		
	def get_data(self,form):
		res = {}
		where_sql = []		
				
		if form['pay_sch']:
				where_sql.append("con.sal_date= '%s' "%form['pay_sch'])		
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
					
		
		print "where_sql --------------------------->>>", where_sql	
		
		self.cr.execute('''
		
			  SELECT distinct on (emp.id)
				slip.id AS slip_id,
				emp.id as emp_id,
				emp.emp_code as code,
				emp.name_related as emp_name,
				dep.id as dep_id,
				dep.name as dep_name,
				con.wage AS basic,
				con.esi_acc_no AS esi_no,
				att.mon_tot_days AS worked
				

				FROM  hr_payslip slip
					
				JOIN hr_employee emp ON (emp.id=slip.employee_id)
				JOIN hr_contract con ON(con.employee_id=slip.employee_id)
				JOIN hr_department dep ON(dep.id=slip.dep_id)
				JOIN kg_monthly_attendance att ON(att.id=slip.att_id)			 		 			  

			  where slip.state=%s and slip.date_from >=%s and slip.date_to <=%s and con.esi=True '''+ where_sql + '''
			  order by emp.id''',('done', form['date_from'],form['date_to']))
		
		
		data = self.cr.dictfetchall()
		data.sort(key=lambda data: data['dep_id'])
		print "data <><><><><<><><><><<><><<>.........", data
		esi_amt=0.00
		gran_tot_worked = 0.00
		tot_worked=0.00
		gran_tot_net = 0.00
		tot_net=0.00
		gran_tot_ded = 0.00
		tot_ded=0.00
		gran_tot_com = 0.00
		tot_com=0.00
		gran_tot_esi = 0.00
		tot_esi=0.00
		gran_tot_gross = 0.00
		tot_gross=0.00
		gran_tot_alw = 0.00
		tot_alw=0.00
		gran_tot_basic = 0.00
		tot_basic=0.00
		print "esi",esi_amt
		if data:
			
			for slip in data:
				tot_worked = slip['worked']
				print "tot_worked................",tot_worked
				gran_tot_worked += tot_worked
				slip['total_worked'] = gran_tot_worked
				
				print "slip.................", slip
				# Basic			
				basic_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',slip['slip_id']),
								('code','=','BASIC')])
				print "basicids.....",basic_ids
				if basic_ids:
					basic_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, basic_ids[0])
					basic_amt = basic_rec.amount
					slip['basic'] = round(basic_amt)
				else:
					pass
				
				# Allowance
								
				allowance_ids = self.pool.get('hr.payslip.line').search(self.cr, self.uid,[('slip_id','=',slip['slip_id']),
								('code','=','ALW')])
				if allowance_ids:
					allowance_rec = self.pool.get('hr.payslip.line').browse(self.cr, self.uid, allowance_ids[0])
					alw_amt = allowance_rec.amount
					slip['alw_amt'] = (round(alw_amt))
				else:
					slip['alw_amt']=0
					
				slip['cross'] = slip['basic'] + slip['alw_amt']
				esi_amt = slip['cross'] * (1.75 /100.0)
				slip['esi_amt'] = (round(esi_amt,0))
				com_esi_amt = slip['cross'] * (4.75 / 100.0)
				slip['com_esi_amt'] =  (round(com_esi_amt))
				net = slip['cross'] - slip['esi_amt']
				slip['net'] = (round(net,0))
				
				# net salary grand total
				
				tot_net = slip['net']
				print "tot_net................",tot_net
				gran_tot_net += tot_net
				slip['total_net'] = gran_tot_net
				
				# deduction grand total
				
				tot_ded = slip['esi_amt']
				print "tot_ded................",tot_ded
				gran_tot_ded += tot_ded
				slip['total_ded'] = gran_tot_ded
				
				# 4.75% grand total
				
				tot_com = slip['com_esi_amt']
				print "tot_com................",tot_com
				gran_tot_com += tot_com
				slip['total_com'] = gran_tot_com
				
				# ESI grand total
				
				tot_esi = slip['esi_amt']
				print "tot_esi................",tot_esi
				gran_tot_esi += tot_esi
				slip['total_esi'] = gran_tot_esi
				
				# Gross grand total
				
				tot_gross = slip['cross']
				print "tot_gross................",tot_gross
				gran_tot_gross += tot_gross
				slip['total_gross'] = gran_tot_gross
				
				# allowance grand total
				
				tot_alw = slip['alw_amt']
				print "tot_alw................",tot_alw
				gran_tot_alw += tot_alw
				slip['total_alw'] = gran_tot_alw
				
				# basic grand total
				
				tot_basic = slip['basic']
				print "tot_basic................",tot_basic
				gran_tot_basic += tot_basic
				slip['total_basic'] = gran_tot_basic
				
			else:
				pass
				
			return data
				
		
			
	def _get_filter(self, data):
		if data.get('form', False) and data['form'].get('filter', False):
			if data['form']['filter'] == 'filter_date':
				return _('Date')
			
		return _('No Filter')
		
	def _get_start_date(self, data):
		if data.get('form', False) and data['form'].get('date_from', False):
			return data['form']['date_from']
		return ''
		
	def _get_end_date(self, data):
		if data.get('form', False) and data['form'].get('date_to', False):
			return data['form']['date_to']
		return ''		   
  

report_sxw.report_sxw('report.kg.esi.pdf.report', 'hr.payslip', 
			'addons/kg_payslip/report/kg_esi_pdf_report.rml', 
			parser=kg_esi_pdf_report, header = False)

