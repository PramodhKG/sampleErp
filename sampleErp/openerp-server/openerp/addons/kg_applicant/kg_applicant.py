## Employee Master Form Module Customization ##

import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
import netsvc
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import calendar
today = datetime.now()

class kg_applicant(osv.osv):
	
	_name = 'hr.applicant'	
	_inherit = 'hr.applicant'
	
	
	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image)
		return result
	
	def _set_image(self, cr, uid, id, name, value, args, context=None):
		return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

	
	_columns = {
	
	'app_date': fields.date('Date', required=True),
	'app_job':fields.many2one('hr.job','Position Applied for'),
	'dep_id':fields.many2one('hr.department','Department Name'),
	'func_area':fields.char('Functional Area', size=100),
	'exp_year':fields.integer('Years of relevant work experience'),
	
	# Personal Details
	'app_name':fields.char('Name (in full)'),
	'dob':fields.date('Date of Birth(DD MM YYYY)'),
	'pre_loc':fields.char('Present Location(city)'),
	'nationality':fields.many2one('res.country','Nationality'),
	'sex':fields.selection([('male','Male'),('female','Female')],'Sex'),
	'mar_status':fields.selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')], 'Marital Status'),
	
	# Address for Communcation
	
	'pre_add': fields.char('Present Addres'),
	'pre_zip': fields.char('Zip'),
	'pre_city': fields.char('City'),
	'pre_state_id': fields.many2one("res.country.state", 'State'),
	'pre_tele':fields.char('Telephone No'),
	'pre_mob':fields.char('Mobile No'),
	
	'perm_add': fields.char('Permanent Address'),
	'perm_zip': fields.char('Zip',),
	'perm_city': fields.char('City'),
	'perm_state_id': fields.many2one("res.country.state", 'State'),
	'perm_email':fields.char('Email'),
	'perm_tele':fields.char('Telephone No'),
	'perm_mob':fields.char('Mobile No'),
	

	# Family Details
	'family_id':fields.one2many('kg.family.details','applicant_id','Family Id'),
	
	#Languages Known
	'lang_id':fields.one2many('kg.languages','app_id','Language Id'),
	
	#Educational Details
	'edu_id':fields.one2many('kg.edu.details','form_id','Education Id'),
	
	#Award Details
	'award_id':fields.one2many('kg.award.details','entry_id','Award Id'),
	
	#Membership Details
	'member_id':fields.one2many('kg.membership.details','application_id','Application Id'),
	
	
	# image: all image fields are base64 encoded and PIL-supported
	'image': fields.binary("Photo",
		help="This field holds the image used as photo for the employee, limited to 1024x1024px."),
	'image_medium': fields.function(_get_image, fnct_inv=_set_image,
		string="Medium-sized photo", type="binary", multi="_get_image",
		store = {
			'hr.applicant': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
		},
		help="Medium-sized photo of the employee. It is automatically "\
			 "resized as a 128x128px image, with aspect ratio preserved. "\
			 "Use this field in form views or some kanban views."),
	'image_small': fields.function(_get_image, fnct_inv=_set_image,
		string="Smal-sized photo", type="binary", multi="_get_image",
		store = {
			'hr.applicant': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
		},
		help="Small-sized photo of the employee. It is automatically "\
			 "resized as a 64x64px image, with aspect ratio preserved. "\
			 "Use this field anywhere a small image is required."),
			 
	'break':fields.boolean('Was there any break in your education? If yes, please give details.'),
	'break_details':fields.text('Deatails'),
	'emp_sno':fields.integer('S.No'),
	'employed_from':fields.date('From'),
	'employed_to':fields.date('To'),
	'designation':fields.char('Designation'),
	'name_add':fields.text('Name & Address of Employer'),
	'reason_for_end':fields.text('Reason for Ending Assignment'),
	'join_date':fields.date('When Joined'),
	'end_date':fields.date('When Ending'),
	'assignment':fields.text('Assignment'),
	
	
		
	}
	
	def onchange_department(self, cr, uid, ids, app_job):
		result = {'value': {'dep_id': False}}
		if app_job:
			job = self.pool.get('hr.job').browse(cr, uid, app_job)
			result['value'] = {'dep_id': job.department_id.id}
		return result
	
	def case_close_with_emp(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		hr_employee = self.pool.get('hr.employee')
		model_data = self.pool.get('ir.model.data')
		act_window = self.pool.get('ir.actions.act_window')
		emp_id = False
		for applicant in self.browse(cr, uid, ids, context=context):
			address_id = False
			if applicant.partner_id:
				address_id = self.pool.get('res.partner').address_get(cr,uid,[applicant.partner_id.id],['contact'])['contact']
			if applicant.app_job:
				applicant.app_job.write({'no_of_recruitment': applicant.app_job.no_of_recruitment - 1})
				emp_id = hr_employee.create(cr,uid,{'name': applicant.app_name,
													 'job_id': applicant.app_job.id,
													 'permanent_add': applicant.perm_add,
													 'department_id': applicant.dep_id.id,
													 'birthday':applicant.dob,
													 
													 'country_id':applicant.nationality.id,
													 'gender':applicant.sex,
													 'marital':applicant.mar_status,
													 'present_add':applicant.pre_add,
													 'pre_city':applicant.pre_city,
													 'pre_state':applicant.pre_state_id.id,
													 'pre_country':applicant.nationality.id,
													 'work_phone':applicant.perm_tele,
													 'mobile_phone':applicant.perm_mob,
													 'permanent_add':applicant.perm_add,
													 'city':applicant.perm_city,
													 'kg_state':applicant.perm_state_id.id,
													 'country':applicant.nationality.id,
													 
													 })
				
				self.write(cr, uid, [applicant.id], {'emp_id': emp_id}, context=context)
				self.case_close(cr, uid, [applicant.id], context)
			else:
				raise osv.except_osv(_('Warning!'), _('You must define Applied Job for this applicant.'))

		action_model, action_id = model_data.get_object_reference(cr, uid, 'hr', 'open_view_employee_list')
		dict_act_window = act_window.read(cr, uid, action_id, [])
		if emp_id:
			dict_act_window['res_id'] = emp_id
		dict_act_window['view_mode'] = 'form,tree'
		return dict_act_window

kg_applicant()


class kg_family_details(osv.osv):
	
	_name = 'kg.family.details'	
	
	
	_columns = {
	
	's_no': fields.date('S.No'),
	'fam_name':fields.char('Name'),
	'relationship':fields.char('Relationship'),
	'education':fields.char('Education'),
	'occupation':fields.char('Occupation'),
	'applicant_id':fields.many2one('hr.applicant','Applicant Id'),
	
	
	}

kg_family_details()

class kg_languages(osv.osv):
	
	_name = 'kg.languages'	
	
	
	_columns = {
	
	'sno': fields.date('S.No'),
	'lang':fields.char('Language'),
	'r_w_s':fields.boolean('Read, Write & Speak'),
	's_only':fields.boolean('Speak Only'),
	'r_only':fields.boolean('Read Only'),
	'app_id':fields.many2one('hr.applicant','App Id'),
	
	
	}

kg_languages()

class kg_edu_details(osv.osv):
	
	_name = 'kg.edu.details'	
	
	
	_columns = {
	
	'course_name': fields.char('Name of the Course'),
	'place':fields.char('Name of School/College/University & Place'),
	'year_of_passing':fields.char('Year of Passing'),
	'duration':fields.char('Duration of Course'),
	'spec':fields.char('Specilization'),
	'marks':fields.char('% Marks'),
	
	'form_id':fields.many2one('hr.applicant','Form Id'),
	
	
	}

kg_edu_details()

class kg_award_details(osv.osv):
	
	_name = 'kg.award.details'	
	
	
	_columns = {
	
	'date_from': fields.date('Date From'),
	'date_to': fields.date('Date To'),
	'awards':fields.char('Qualification/Awards Obtained'),
	'ins':fields.char('Awarding Institution'),
	'entry_id':fields.many2one('hr.applicant','Entry Id'),
	
	
	}

kg_award_details()


class kg_membership_details(osv.osv):
	
	_name = 'kg.membership.details'	
	
	
	_columns = {
	
	'mem_sno': fields.integer('S No'),
	'org_name': fields.char('Name of the Organization/Association'),
	'duration':fields.integer('Duration'),
	'remarks':fields.text('Remarks'),
	'application_id':fields.many2one('hr.applicant','Application Id'),
	
	
	}

kg_membership_details()






	
	
	

