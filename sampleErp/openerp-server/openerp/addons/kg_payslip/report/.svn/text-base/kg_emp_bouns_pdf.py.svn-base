import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale
from dateutil import rrule
from datetime import datetime, timedelta
import datetime as idt


class kg_emp_bouns_pdf(report_sxw.rml_parse):
	
	_name = 'kg.emp.bouns.pdf'
	_inherit='hr.employee'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_emp_bouns_pdf, self).__init__(cr, uid, name, context=context)
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
		
		if form['dep_id']:
			for ids2 in form['dep_id']:
				where_sql.append("slip.dep_id = %s"%(ids2))
			
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''			
		
		
		print "where_sql --------------------------->>>", where_sql	
				
		self.cr.execute('''
		
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
				
				
				
				
			where payslip=True '''+ where_sql + ''' 
						order by emp.id limit 5''')
			   
		data=self.cr.dictfetchall()
		data.sort(key=lambda data: data['emp_id'])
		print "data ------------------>>>", data
		if data:
			
			from_date = form['date_from']
			to_date = form['date_to']
			print "from_date...............................", from_date
			print "to_date...............................", to_date
			att_obj = self.pool.get('kg.monthly.attendance')
			
			tot_amt = 0
			gr_amt = 0
			for ele in data:
				ele['basic_amt1'] , ele['basic_amt2'], ele['basic_amt3'], ele['basic_amt4'], ele['basic_amt5'], ele['basic_amt6'] = 0,0,0,0,0,0
				ele['basic_amt7'] , ele['basic_amt8'], ele['basic_amt9'], ele['basic_amt10'], ele['basic_amt11'], ele['basic_amt12'] = 0,0,0,0,0,0
				emp_id = ele['emp_id']
				one_day_basic = ele['basic'] / 26
				print "Looping............", ele				
				
				from_dt = idt.datetime.strptime(from_date, '%Y-%m-%d').strftime('%m/%d/%Y')
				from_dt = (idt.datetime.strptime(from_dt, '%m/%d/%Y'))
				to_dt = idt.datetime.strptime(to_date, '%Y-%m-%d').strftime('%m/%d/%Y')
				to_dt = (idt.datetime.strptime(to_dt, '%m/%d/%Y'))
				
				for dt in rrule.rrule(rrule.MONTHLY, dtstart=from_dt, until=to_dt):
					print "------------------------dt-----", dt					
					att_id = att_obj.search(self.cr, self.uid, [('employee_id','=',emp_id),
								('start_date','=',dt),('state','=','confirm')])
					print "att_id................", att_id
					if att_id:
						att_rec = att_obj.browse(self.cr, self.uid,att_id[0])
						worked = att_rec.mon_tot_days
						print "worked..........................", worked
					else:
						worked = 0				
						
					ele['month'] = dt.strftime('%B')
					print "ele['month'] ----------------------.........", ele['month']					
					if ele['month'] == 'January':
						#ele['month1'] = 'Jan'
						ele['worked1'] = worked
						if worked > 26:							
							basic_amt = 26 * one_day_basic
							ele['basic_amt1'] = basic_amt
						else:
							basic_amt = worked * one_day_basic
							ele['basic_amt1'] = basic_amt
												
					elif ele['month'] == 'February':
						ele['month1'] = 'Feb'
						ele['worked2'] = worked
						if worked > 26:							
							basic_amt = 26 * one_day_basic
							ele['basic_amt2'] = basic_amt
						else:
							basic_amt = worked * one_day_basic
							ele['basic_amt2'] = basic_amt
							
					elif ele['month'] == 'March':
						ele['month1'] = 'Mar'
						ele['worked3'] = worked
						if worked > 26:							
							basic_amt = 26 * one_day_basic
							ele['basic_amt3'] = basic_amt
						else:
							basic_amt = worked * one_day_basic
							ele['basic_amt3'] = basic_amt
					
					elif ele['month'] == 'April':
						ele['month1'] = 'Apr'
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
						
					tot_amt = ele['basic_amt1'] + ele['basic_amt2'] + ele['basic_amt3'] + ele['basic_amt4'] + ele['basic_amt5'] + ele['basic_amt6']+ ele['basic_amt7'] + ele['basic_amt8']+ ele['basic_amt9']+ ele['basic_amt10']+ ele['basic_amt11']+ ele['basic_amt12']				
					
					ele['tot_amt'] = tot_amt
					print "tot_amt.........................", tot_amt
					bouns_amt = tot_amt * 8.33 / 100
					if bouns_amt >= 10000:
						ele['bouns_amt'] = 10000
					else:
						ele['bouns_amt'] = bouns_amt
					
					print "bouns_amt.........................", bouns_amt
				gr_amt += ele['bouns_amt']			
				ele['gr_amt'] = gr_amt
				
			return data
		else:
			print "No Data Available"		
		

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
  

report_sxw.report_sxw('report.kg.emp.bouns.pdf', 'hr.employee', 
			'addons/kg_payslip/report/kg_emp_bouns_pdf.rml',
			parser=kg_emp_bouns_pdf, header = False)
