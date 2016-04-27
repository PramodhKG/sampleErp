{
    'name': 'KG Reports',
    'version': '0.1',
    'author': 'shubashri',
    'category': 'HRM',
    'website': 'http://www.openerp.com',
 
    'depends' : ['base','hr','hr_payroll'],
    'data': ['wizard/kg_employeesal_muster.xml',
			 'wizard/kg_leave_summary_wiz.xml',
			 'wizard/kg_salary_revision_wiz.xml',
			 'wizard/kg_employee_payslip_wiz.xml',
			 'wizard/kg_attendance_wiz.xml',
			 'wizard/kg_monthly_atten_wiz.xml',
			 'wizard/kg_allowance.xml',
			 'wizard/kg_mobile_bills_wiz.xml',
			 'wizard/kg_cumul_ded_wizard.xml',
			 'wizard/kg_emp_sal_details.xml',
			 'wizard/kg_esi_pf_wizard.xml',
			 'reports/kg_excel_pf_report.xml',
			 'reports/kg_excel_esi_report.xml',
			 'wizard/kg_pf_pdf.xml',
			 'wizard/kg_esi_pdf.xml'],
    'auto_install': False,
    'installable': True,
}


