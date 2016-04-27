from openerp.osv import fields, osv
from openerp.tools.translate import _

class so2_service_bill(osv.osv_memory):

	def _get_journal(self, cr, uid, context=None):
		res = self._get_journal_id(cr, uid, context=context)
		if res:
			return res[0][0]
		return False

	def _get_journal_id(self, cr, uid, context=None):
		if context is None:
			context = {}

		model = context.get('active_model')
		print "model ------------->>>", model
		if not model or 'kg.service.order' not in model:
			return []

		model_pool = self.pool.get(model)
		journal_obj = self.pool.get('account.journal')
		res_ids = context and context.get('active_ids', [])
		vals = []
		so_obj = model_pool.browse(cr, uid, res_ids, context=context)

		for so in so_obj:
			if not so.service_order_line:
				continue
			#src_usage = pick.move_lines[0].location_id.usage
			#dest_usage = pick.move_lines[0].location_dest_id.usage
			#type = pick.type
			journal_type = 'purchase'			
			value = journal_obj.search(cr, uid, [('type', '=',journal_type )])
			for jr_type in journal_obj.browse(cr, uid, value, context=context):
				t1 = jr_type.id,jr_type.name
				if t1 not in vals:
					vals.append(t1)
		return vals

	_name = "so2.service.bill"
	_description = "SO Bill Creation"

	_columns = {
	
		'journal_id': fields.selection(_get_journal_id, 'Destination Journal',required=True),
		'invoice_date': fields.date('Invoice Date'),
		'sup_inv_no': fields.char('Supplier Invoice No', size=128),
		'sup_inv_date': fields.date('Supplier Invoice Date'),
	}

	_defaults = {
		'journal_id' : _get_journal,
	}

	def view_init(self, cr, uid, fields_list, context=None):
		if context is None:
			context = {}
		res = super(so2_service_bill, self).view_init(cr, uid, fields_list, context=context)
		so_obj = self.pool.get('kg.service.order')
		count = 0
		active_ids = context.get('active_ids',[])
		print "active_ids ==============>>>>",active_ids
		return res

	def open_invoice(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		invoice_ids = []
		data_pool = self.pool.get('ir.model.data')
		res = self.create_invoice(cr, uid, ids, context=context)
		invoice_ids += res.values()
		inv_type = context.get('inv_type', False)
		print "inv_type ^^^^^^^^^^^^^^^^^^", inv_type
		action_model = False
		action = {}
		if inv_type == "in_invoice":
			action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree2")
		
		if action_model:
			action_pool = self.pool.get(action_model)
			action = action_pool.read(cr, uid, action_id, context=context)
			action['domain'] = "[('id','in', ["+','.join(map(str,invoice_ids))+"])]"
		return action

	def create_invoice(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		#picking_pool = self.pool.get('kg.service.order')
		so_obj = self.pool.get('kg.service.order')
		#onshipdata_obj = self.read(cr, uid, ids, ['journal_id', 'group', 'invoice_date'])
		so_wiz_obj = self.read(cr, uid, ids, ['journal_id', 'invoice_date','sup_inv_no','sup_inv_date'])
		print "so_wiz_obj ------------------>>>",so_wiz_obj
		if context.get('new_picking', False):
			so_wiz_obj['id'] = so_wiz_obj.new_picking
			so_wiz_obj[ids] = so_wiz_obj.new_picking
		print "context................", context
		print "so_wiz_obj................", so_wiz_obj
		context['date_inv'] = so_wiz_obj[0]['invoice_date']
		context['sup_inv_no'] = so_wiz_obj[0]['sup_inv_no']
		context['sup_inv_date'] = so_wiz_obj[0]['sup_inv_date']
		active_ids = context.get('active_ids', [])
		print "active_ids :::::::::::::::::::",active_ids
		active_picking = so_obj.browse(cr, uid, context.get('active_id',False), context=context)
		print "active_picking ====================>>", active_picking
		inv_type = 'in_invoice'
		context['inv_type'] = inv_type
		if isinstance(so_wiz_obj[0]['journal_id'], tuple):
			so_wiz_obj[0]['journal_id'] = so_wiz_obj[0]['journal_id'][0]
		res = so_obj.action_invoice_create(cr, uid, active_ids,
			  journal_id = so_wiz_obj[0]['journal_id'],
			  type = inv_type,
			  context=context)
		print "RES *********************** RES *********", res
		return res

so2_service_bill()

