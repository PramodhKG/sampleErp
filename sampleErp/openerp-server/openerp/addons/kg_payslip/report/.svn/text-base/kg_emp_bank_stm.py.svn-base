import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_emp_bank_stm(report_sxw.rml_parse):
	
	_name = 'kg.emp.bank.stm'
	_inherit='hr.payslip'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_emp_bank_stm, self).__init__(cr, uid, name, context=context)
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
		
		if form['bank_id']:
			bank_id = form['bank_id']
			where_sql.append("con.bank = %s "%(bank_id[0]))	
				
		if form['dep_id']:
			for ids2 in form['dep_id']:
				dep.append("emp.department_id = %s"%(ids2))
				
		if form['pay_sch']:
				where_sql.append("con.sal_date= '%s' "%form['pay_sch'])
		
				
		if where_sql:
			where_sql = ' and '+' and '.join(where_sql)
		else:
			where_sql=''
					
		if dep:
			dep = 'and ('+' or '.join(dep)
			dep =  dep+')'
		else:
			dep = ''
		
		print "where_sql --------------------------->>>", where_sql			
		print "dep --------------------------->>>", dep		
		
		self.cr.execute('''
		
			  SELECT distinct on (emp.id)
				slip.id AS sl_id,
				slip.dep_id as dep_id,			  
				slip.round_val AS net_sal,			  			  
				emp.emp_code as code,
				emp.name_related as emp_name,				
				dep.name as dep_name,		  
				con.acc_no AS bank_no

				FROM  hr_payslip slip
					
				JOIN hr_employee emp ON (emp.id=slip.employee_id)
				JOIN hr_department dep ON(dep.id=slip.dep_id)
				JOIN hr_contract con ON(con.employee_id=slip.employee_id)
				JOIN res_bank ba ON(ba.id=con.bank)
			 		 			  

			  where slip.state=%s and slip.date_from >=%s and slip.date_to <=%s '''+ where_sql + '''
			   order by emp.id''',('done', form['date_from'],form['date_to']))
		
		data=self.cr.dictfetchall()
		data.sort(key=lambda data: data['dep_id'])
		print "data_sort ------------------------>>>.........", data
		if data:
			gr_total = 0.0
			for ele in data:
				net_amt = ele['net_sal']
				gr_total += net_amt			
			ele['gr_total'] = gr_total
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
  

report_sxw.report_sxw('report.kg.emp.bank.stm', 'hr.payslip', 
			'addons/kg_payslip/report/kg_emp_bank_stm.rml', 
			parser=kg_emp_bank_stm, header = False)
			
"""
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
		sub_net = 0.00		
		gr_net = 0.00
		for position1, item1 in enumerate(data_new):
			data_renew.append({'code':item1['dep_name'],'type':1})
			data_renew.append(item1)
			item1['ser_no']=ser_no
			item1['dep_name'] = " "					
			sub_net = item1['net_sal']
			remove_item_list = []
			for position2, item2 in enumerate(data_new):
				if position1 != position2:
					if item1['dep_id'] == item2['dep_id']:
						item2['dep_name'] = " "
						item2['ser_no']=ser_no+1
						data_renew.append(item2)
						remove_item_list.append(item2)
						ser_no+=1															
						sub_net += item2['net_sal']				
												
			ser_no+=1
			data_renew.append({'code': 'Sub Total', 'sub_net': sub_net})			
						
			gr_net += sub_net				
			for entry in remove_item_list:
				data_new.remove(entry)					
		data_renew.append({'code': 'Grand Total', 'sub_net': gr_net})										
		return data_renew
		"""
