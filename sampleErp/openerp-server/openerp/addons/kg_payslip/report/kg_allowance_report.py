import time
from report import report_sxw
from reportlab.pdfbase.pdfmetrics import stringWidth
import locale


class kg_allowance_report(report_sxw.rml_parse):
	
	_name = 'kg.allowance.report'
	_inherit='kg.allowance.deduction'   

	def __init__(self, cr, uid, name, context=None):
		if context is None:
			context = {}
		super(kg_allowance_report, self).__init__(cr, uid, name, context=context)
		self.query = ""
		self.period_sql = ""
		self.localcontext.update( {
			'tim.e': time,
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
		pay_type = []	   
		
		if form['type']:
			ids = form['type'][0]
			where_sql.append("entry.type = %s" %(ids))
			
		if form['pay_type']:
			for ids in form['pay_type']:
				pay_type.append("entry.pay_type = %s"%(ids))
			
				
		if where_sql:
			where_sql = ' and '+' or '.join(where_sql)
		else:
			where_sql=''
			
		if pay_type:
			pay_type = 'and ('+' or '.join(pay_type)
			pay_type =  pay_type+')'
		else:
			pay_type = ''
		
		print "where_sql --------------------------->>>", where_sql 
		print "pay_type --------------------------->>>", pay_type		   
				
		self.cr.execute('''
		
			SELECT
				entry.id as entry_id,
				entry.type as rule_id,
				entry.pay_type as sub_id,
				line.amount as amt,
				line.employee_id as emp_id,
				rule.name as rule_name,
				emp.emp_code as code,
				emp.name_related as emp_name

				FROM  kg_allowance_deduction entry				  
				
				JOIN kg_allowance_deduction_line line ON(line.entry_id=entry.id)								  
				JOIN hr_employee emp ON (emp.id=line.employee_id)
				JOIN hr_salary_rule rule ON(rule.id=entry.pay_type)
				
			where entry.state!=%s and entry.start_date >=%s and entry.end_date <=%s '''+ where_sql + 
				pay_type + ''' order by emp.id''',('cancel', form['date_from'],form['date_to']))
			   
		data=self.cr.dictfetchall()
		data.sort(key=lambda data: data['sub_id'])
		print "data_sort ------------------------>>>.........", data	

		if data:			
			data_emp_grouped = []			   
			for pos, sm in enumerate(data):
				data_emp_grouped.insert(pos, [sm])
				rem_list = []
				for pos1, sm1 in enumerate(data):
					if not pos == pos1:
						if sm['sub_id'] == sm1['sub_id']:
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
			sub_tot = 0.00
			gr_tot = 0.00
			for position1, item1 in enumerate(data_new):
				print"pos,it",position1, item1
				data_renew.append({'code':item1['rule_name'],'type':1})
				data_renew.append(item1)
				item1['ser_no']=ser_no
				item1['rule_name'] = " "
				sub_tot = item1['amt']
				remove_item_list = []
				for position2, item2 in enumerate(data_new):
					print"pos,it,,,,,,,,,,,,,,,,,,,,,,,",position2, item2
					if position1 != position2:
						if item1['sub_id'] == item2['sub_id']:
							item2['rule_name'] = " "
							item2['ser_no']=ser_no+1
							data_renew.append(item2)
							remove_item_list.append(item2)
							ser_no+=1
							sub_tot += item2['amt'] 
													
				ser_no+=1
				data_renew.append({'code': 'Sub Total', 'sub_tot': sub_tot,})		   
				gr_tot += sub_tot   
				for entry in remove_item_list:
					data_new.remove(entry)
			data_renew.append({'code': 'Grand Total', 'sub_tot': gr_tot,})				  
			return data_renew 
		
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
  

report_sxw.report_sxw('report.kg.allowance.report', 'hr.payslip', 
			'addons/kg_payslip/report/kg_allowance_report.rml', 
			parser=kg_allowance_report, header = False)
