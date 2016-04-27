import math
import re
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp
import netsvc
import datetime
import calendar

class kg_holiday_master(osv.osv):

	_name = "kg.holiday.master"
	_description = 'Enables you to View The Gvt Holidays'
	_columns = {
				'from_date':fields.date('Valid From'),
				'to_date':fields.date('Valid Till'),
				'active':fields.boolean('Active'),
				'expiry_date':fields.date('Expiry Date'),
				'state': fields.selection([('draft', 'To Submit'),('confirm', 'To Approve'),('validate', 'Approved')],
						'Status', readonly=True, track_visibility='onchange'),
				'line_id':fields.one2many('kg.holiday.master.line','line_entry','Line id'),
				'branch':fields.many2one('kg.branch','Branch')
				}

	_defaults = {
		'state': 'draft',
		'active': True
				}
	
	
	def approve_entry(self, cr, uid, ids,context=None):		
		self.write(cr,uid,ids,{'state':'validate'})
		return True
		
	def confirm_entry(self, cr, uid, ids, context=None):
		
		entry = self.browse(cr,uid,ids[0])
		print "entry-----------",entry
		entry_obj = self.pool.get('kg.holiday.master')
		
		start_date = entry.from_date
		end_date = entry.to_date
		branch = entry.branch
		entry_id=entry.id	
		
		duplicate_ids= entry_obj.search(cr, uid, [('from_date','=',start_date),('to_date','=',end_date),
												  ('branch','=',branch),('id' ,'!=', entry_id)])
		print "du[plicate..............",duplicate_ids
		
		
		if duplicate_ids:
			dup_rec = entry_obj.browse(cr,uid,duplicate_ids[0])
			print "dup_rec...............",dup_rec
			today_date = datetime.date.today()
			print "today_date....................",today_date
			dup_rec.write({'active': False})
			dup_rec.write({'expiry_date':today_date})
		self.write(cr,uid,ids,{'state':'confirm'})	
		return True
		
		
	def draft_entry(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'draft'})
		return True

kg_holiday_master()

class kg_holiday_master_line(osv.osv):
	
	_name = "kg.holiday.master.line"
	_description = "Holiday Master Line"
	
	_columns = {

	'line_entry':fields.many2one('kg.holiday.master','Line Entry'),
	'leave_date':fields.date('Date'),
	'note':fields.text('Description')
	
	}
	
kg_holiday_master_line()	

