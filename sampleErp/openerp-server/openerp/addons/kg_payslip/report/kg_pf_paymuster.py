import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_pf_paymuster(report_sxw.rml_parse):
	
	_name = 'kg.pf.paymuster'
	_inherit='hr.payslip'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_pf_paymuster, self).__init__(cr, uid, name, context=context)
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
		dep = []		
				
		if form['dep_id']:
			for ids2 in form['dep_id']:
				where_sql.append("emp.department_id = %s"%(ids2))
		
		if form['pay_sch']:
				where_sql.append("con.sal_date= '%s' "%form['pay_sch'])
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
					
		
		print "where_sql --------------------------->>>", where_sql	
		
		self.cr.execute('''
		
			  SELECT distinct on (emp.id)
				slip.id AS sl_id,
				emp.id as emp_id,
				emp.emp_code as code,
				emp.name_related as emp_name,
				dep.id as dep_id,
				dep.name as dep_name,
				con.id as con_id,		  
				con.wage AS basic,
				att.mon_tot_days AS worked

				FROM  hr_payslip slip
					
				JOIN hr_employee emp ON (emp.id=slip.employee_id)
				JOIN hr_department dep ON(dep.id=emp.department_id)
				JOIN hr_contract con ON(con.employee_id=slip.employee_id)
				JOIN kg_monthly_attendance att ON(att.id=slip.att_id)			 		 			  

			  where slip.state=%s and slip.date_from >=%s and slip.date_to <=%s and con.pf_status=True '''+ where_sql + '''
			   order by emp.id''',('done', form['date_from'],form['date_to']))
		
		data=self.cr.dictfetchall()
		data.sort(key=lambda data: data['dep_id'])
		print "data_sort ------------------------>>>.........", data		
		data_emp_grouped = []
				
		for pos, sm in enumerate(data):
			data_emp_grouped.insert(pos, [sm])
			rem_list = []
			for pos1, sm1 in enumerate(data):
				if not pos == pos1:
					if sm['dep_id'] == sm1['dep_id']:
						data_emp_grouped[pos].append(sm1)
						rem_list.append(sm1)
			for item in rem_list:
				data.remove(item)
						
		data_new = []
		print "data_emp_grouped...........................",data_emp_grouped
		for item in data_emp_grouped:
			data_new += item					
		print "data_new **************************...",data_new
				
		data_renew = []	
		ser_no=1
		sub_basic = 0.00
		sub_ear = 0.00
		sub_pf = 0.00
		gr_basic = 0.00
		gr_ear = 0.00
		gr_pf = 0.00
		gr_net = 0.00
		for position1, item1 in enumerate(data_new):
			data_renew.append({'code':item1['dep_name'],'type':1})
			data_renew.append(item1)
			item1['ser_no']=ser_no
			item1['dep_name'] = " "
			basic = item1['basic']
			one_day_basic = basic / 26
			slip_basic = one_day_basic * item1['worked']
			item1['slip_basic'] = slip_basic
			con_rec = self.pool.get('hr.contract').browse(self.cr, self.uid,item1['con_id'])
			if con_rec.pf_status == True:
				if item1['worked'] > 26:							
					pf_amt = basic * (12 /100.0)						
					item1['pf_amt'] = pf_amt
				else:
					pf_basic = one_day_basic * item1['worked']
					pf_amt = pf_basic * (12 /100.0)						
					item1['pf_amt'] = pf_amt
			else:
				item1['pf_amt'] = 0.00	
			sub_basic = item1['basic']
			sub_ear = item1['slip_basic']
			sub_pf = item1['pf_amt']
			remove_item_list = []
			for position2, item2 in enumerate(data_new):
				if position1 != position2:
					if item1['dep_id'] == item2['dep_id']:
						item2['dep_name'] = " "
						item2['ser_no']=ser_no+1
						data_renew.append(item2)						
						basic = item2['basic']
						one_day_basic = basic / 26
						worked = item2['worked']						
						slip_basic = one_day_basic * worked
						item2['slip_basic'] = slip_basic
						con_rec = self.pool.get('hr.contract').browse(self.cr, self.uid,item2['con_id'])
						if con_rec.pf_status == True:
							if worked > 26:							
								pf_amt = basic * (12 /100.0)						
								item2['pf_amt'] = pf_amt
							else:
								pf_basic = one_day_basic * worked
								pf_amt = pf_basic * (12 /100.0)						
								item2['pf_amt'] = pf_amt
						else:
							item2['pf_amt'] = 0.00
							
						remove_item_list.append(item2)
						ser_no+=1
						sub_basic += item2['basic']
						sub_pf += item2['pf_amt']
						sub_ear += item2['slip_basic']
												
			ser_no+=1
			data_renew.append({'dep_name': 'Sub Total', 'sub_basic': sub_basic,
								'sub_ear': sub_ear, 'sub_pf': sub_pf, 'sub_net': sub_ear - sub_pf})	
			
			gr_basic += sub_basic
			gr_ear += sub_ear
			gr_pf += sub_pf
			gr_net = gr_ear - gr_pf			
			
			for entry in remove_item_list:
				data_new.remove(entry)
					
		data_renew.append({'dep_name': 'Grand Total', 'sub_basic': gr_basic,
								'sub_ear': gr_ear, 'sub_pf': gr_pf, 'sub_net': gr_net})
								
		# Grand total for basic
		tot_bp_amt = val['basic_amt']
		print "tot_bp_amt................",tot_bp_amt
		gran_tot_bp += tot_bp_amt
		val['total_bp'] = gran_tot_bp
										
		return data_renew
	

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
  

report_sxw.report_sxw('report.kg.pf.paymuster', 'hr.payslip', 
			'addons/kg_payslip/report/kg_pf_paymuster.rml', 
			parser=kg_pf_paymuster, header = False)
