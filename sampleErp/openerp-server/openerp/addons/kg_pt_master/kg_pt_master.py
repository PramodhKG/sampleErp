from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import datetime
import calendar
import openerp

class kg_pt_master(osv.osv):
	_name = 'kg.pt.master'
	_columns = {
				'created_date':fields.datetime('Creation Date',readonly=True),
				'created_by':fields.many2one('res.users','Created By',readonly=True),
				'active':fields.boolean('Active'),
				'expiry_date':fields.datetime('Expiry Date'),
				'state': fields.selection([('draft', 'To Submit'),('confirm', 'To Approve'),('validate', 'Approved')],
						'Status', readonly=True, track_visibility='onchange'),
				'pt_line':fields.one2many('kg.pt.master.line','pt_line','Line id',readonly=True ,states = {'draft': [('readonly', False)]})
				}

	_defaults = {
		'state': 'draft',
		'active': True,
		'created_date': lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'created_by': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
				}
	
	
	def approve_entry(self, cr, uid, ids,context=None):		
		self.write(cr,uid,ids,{'state':'validate'})
		return True
		
	def confirm_entry(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		print "entry-----------",entry
		entry_obj = self.pool.get('kg.pt.master')
		start_date = entry.created_date
		entry_id=entry.id	
		duplicate_ids= entry_obj.search(cr, uid, [('id' ,'!=', entry_id)])
		print "duplicate..............",duplicate_ids
		if duplicate_ids:
			dup_rec = entry_obj.browse(cr,uid,duplicate_ids[0])
			print "dup_rec...............",dup_rec
			today_date = datetime.datetime.today()
			print "today_date....................",today_date
			dup_rec.write({'active': False})
			dup_rec.write({'expiry_date':today_date})
		self.write(cr,uid,ids,{'state':'validate'})	
		return True

	def draft_entry(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'draft'})
		return True
		
	def _check_entry_line(self, cr, uid, ids, context=None):
		entry = self.browse(cr,uid,ids[0])
		if not entry.pt_line:
			return False
		else:
			for line in entry.pt_line:
				if (line.min_value == 0.00) or (line.max_value == 0.00):
					raise openerp.exceptions.Warning(_('Min Value and Max value should not be Empty!!.Please Enter The Values !!!'))
				if line.min_value >= line.max_value:
					raise openerp.exceptions.Warning(_('Min Value must be less than Max value!!.Please Enter The Values Correctly!!!'))
		return True
	
	_constraints = [
		
		(_check_entry_line, 'Line entry can not be empty !!',['Line Entry']),
				
		]
	
kg_pt_master()

class kg_pt_master_line(osv.osv):
	
	_name = 'kg.pt.master.line'		
	_columns = {
				'pt_line':fields.many2one('kg.pt.master','Line Entry'),
				'min_value':fields.float('Min Value',required = True),
				'max_value':fields.float('Max Value',required=True),
				'pt_value':fields.float('PT Value',required=True)
	}
	
kg_pt_master_line()
