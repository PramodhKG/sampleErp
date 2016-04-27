import time
from lxml import etree
from openerp.osv import fields, osv
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class kg_stock_partial_picking(osv.osv):
	
	_name = "stock.partial.picking"
	_inherit = 'stock.partial.picking'
	
	_columns = {
	
		'move_ids' : fields.one2many('stock.partial.picking.line', 'wizard_id', 'Product Moves', readonly=True),
		
	}
	
	
	def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
		#override of fields_view_get in order to change the label of the process button and the separator accordingly to the shipping type
		if context is None:
			context={}
		res = super(kg_stock_partial_picking, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
		type = context.get('default_type', False)
		if type:
			doc = etree.XML(res['arch'])
			for node in doc.xpath("//button[@name='do_partial']"):
				if type == 'in':
					node.set('string', _('_Update To Stock'))
				elif type == 'out':
					node.set('string', _('_Issue To SubStore'))
			for node in doc.xpath("//separator[@name='product_separator']"):
				if type == 'in':
					node.set('string', _('Receive Products'))
				elif type == 'out':
					node.set('string', _('Deliver Products'))
			res['arch'] = etree.tostring(doc)
		return res
	
	def _partial_move_for(self, cr, uid, move):
		print "_partial_move_for calleeeeeeeeeeeeeeeeefrom KGGGGGGGGGGGGGGGGGGGeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
		partial_move = {
			'product_id' : move.product_id.id,
			'quantity' : move.product_qty if move.state == 'assigned' else 0,
			'grn_qty': move.po_to_stock_qty if move.move_type == 'in' else move.po_to_stock_qty,
			'product_uom' : move.product_uom.id,
			'prodlot_id' : move.prodlot_id.id,
			'move_id' : move.id,
			'location_id' : move.location_id.id,
			'location_dest_id' : move.location_dest_id.id,
		}
		if move.picking_id.type == 'in' and move.product_id.cost_method == 'average':
			partial_move.update(update_cost=True, **self._product_cost_for_average_update(cr, uid, move))
		return partial_move

	def do_partial(self, cr, uid, ids, context=None):
		print "called do_partial++++++from KGGGGGGGGG+++++++++++++++++++++++++++++++"
		assert len(ids) == 1, 'Partial picking processing may only be done one at a time.'
		stock_picking = self.pool.get('stock.picking')
		stock_move = self.pool.get('stock.move')
		uom_obj = self.pool.get('product.uom')
		po_line_obj=self.pool.get('purchase.order.line')
		depindent_line_obj=self.pool.get('kg.depindent.line')
		lot_obj = self.pool.get('stock.production.lot')
		partial = self.browse(cr, uid, ids[0], context=context)
		print "partial --------------------------->>>", partial
		if not partial.move_ids:
			raise osv.except_osv(_('Empty GRN Error !'), _('System not allow to process a empty GRN !!'))	   
		partial_data = {
			'delivery_date' : partial.date
		}
		picking_type = partial.picking_id.type
		
		for wizard_line in partial.move_ids:
			print "wizard_line =============================>>>>", wizard_line
			line_uom = wizard_line.product_uom
			move_id = wizard_line.move_id.id
			move_record = stock_move.browse(cr,uid,move_id)
			print "move_record :::::::::::::::::::::::::::", move_record
		
			rec_qty = move_record.purchase_line_id.received_qty
			if move_record.move_type == 'in' and move_record.purchase_line_id:
				po_line_id = move_record.purchase_line_id
				grn_qty = move_record.po_to_stock_qty
				po_line_qty = move_record.po_qty
				po_line_pending_qty = po_line_qty - grn_qty
				rec_qty += move_record.po_to_stock_qty
				print "po_line_id :", po_line_id, "=====================po_qty", po_line_pending_qty
				po_line_obj.write(cr, uid, [move_record.purchase_line_id.id],
						{
						'pending_qty' : po_line_pending_qty,
						'received_qty' : rec_qty,
						})
				
				# System will create production lot entry automatically
				
				print "difffffffffffffffffffffffffffffffff",move_record.product_id
				product_obj = self.pool.get('product.product')
				product_rec = product_obj.browse(cr,uid,move_record.product_id.id)
				coeff = product_rec.po_uom_coeff
				print "coeff.........................",coeff
				print 
				qty = move_record.purchase_line_id.product_qty * coeff
				price = move_record.purchase_line_id.price_subtotal/qty
				print "price/////////difffffffffff//////////////////////////////",price
	
				print "Price ::::::::::::;;;--------->>>", price
										
				lot_obj.create(cr,uid,
					
					{
					'grn_move':move_record.id,
					'grn_no':move_record.picking_id.name,
					'product_id':move_record.product_id.id,
					'product_uom':move_record.stock_uom.id,
					'product_qty':move_record.product_qty,
					'pending_qty':move_record.product_qty,
					'issue_qty':move_record.product_qty,
					'batch_no':move_record.batch_no,
					'expiry_date':move_record.expiry_date,
					'price_unit':price,
					'po_uom':move_record.product_uom.id,
					'po_qty':move_record.po_to_stock_qty,
					
					})
			
			if move_record.move_type == 'out':
				
				dep_line_obj = self.pool.get('kg.depindent.line')   
				pick_record = move_record.picking_id
				print "pick_record:::::in::::::::", pick_record
				pick_record.write({'state': 'done'})
				cr.execute(""" select stock_picking_id from kg_depline_picking where kg_depline_id = %s """ %(pick_record.id))
				data = cr.dictfetchall()
				print "dep_____________________data",data
				val = [d['stock_picking_id'] for d in data if 'stock_picking_id' in d] 
				print "val...............................",val
				product_id = move_record.product_id.id
				product_obj = self.pool.get('product.product')
				product_record = product_obj.browse(cr, uid, product_id)
				print "product_id....................", product_id
				list_line = dep_line_obj.search(cr,uid,[('id', 'in', val), ('product_id', '=', product_id)],context=context)
				print "list_line....................>>>>>", list_line
				issue_qty = move_record.product_qty
				
				for i in list_line:
					print "IIIIIIIIIIIIIIIIIIIIIIII", i
					bro_record = dep_line_obj.browse(cr, uid,i)
					print "bro_record ;;;;;;;;;;;;;;;;;;;;;;;", bro_record
					orig_depindent_qty = bro_record.qty
					issue_pending_qty = bro_record.issue_pending_qty
					issue_used_qty = issue_qty
					print "issue_used_qty,,,,,,,,,,,,,,,,", issue_used_qty, 
					print "orig_depindent_qty ===============>>", orig_depindent_qty, 'issue_pending_qty ==============>>>', issue_pending_qty
					indent_uom = bro_record.uom.id
					move_uom = move_record.product_uom.id
					print "uom,,,,,,,,,,,,,,,,,,,,..................,,,,,,,,,,,", indent_uom
					print "po_uom,,,,,,,,,,,,,,,,,,,,...........===============>>", move_uom
					if indent_uom != move_uom:
						print "Ifff =====>>> issue_pending_qty", issue_pending_qty					  
						if issue_used_qty <= issue_pending_qty:
							print "IFFFFFFFFFFFFFFFFF Calling"
							pending_depindent_qty = issue_pending_qty - (issue_used_qty * product_record.po_uom_coeff)
							print "dep line id ::::::::::",bro_record
							print "po_qty ::::::::", pending_depindent_qty
							
							sql = """ update kg_depindent_line set issue_pending_qty=%s where id = %s"""%(pending_depindent_qty,bro_record.id)
							cr.execute(sql)
							#dep_line_obj.write(cr,uid, bro_record.id, {'line_state' : 'noprocess'})
							break
						else:
							remain_qty = issue_used_qty - issue_pending_qty
							issue_qty = remain_qty
							print "remain_qty ()(()()))))))))))()()", remain_qty
							pending_depindent_qty =  0.0
							
							print "pending_depindent_qty ::::::::", pending_depindent_qty
							
							sql = """ update kg_depindent_line set issue_pending_qty=%s where id = %s"""%(pending_depindent_qty,bro_record.id)
							cr.execute(sql)
							#dep_line_obj.write(cr,uid, bro_record.id, {'line_state' : 'noprocess'})
							if remain_qty < 0:
								break		   
					
					else:
						print "else =====>>> issue_pending_qty", issue_pending_qty
						if issue_used_qty <= issue_pending_qty:
							print "IFFFFFFFFFFFFFFFFF Calling"
							pending_depindent_qty =  issue_pending_qty - issue_used_qty
							
							print "dep line id ::::::::::",bro_record
							print "po_qty ::::::::", pending_depindent_qty
							sql = """ update kg_depindent_line set issue_pending_qty=%s where id = %s"""%(pending_depindent_qty,bro_record.id)
							cr.execute(sql)
							#dep_line_obj.write(cr,uid, bro_record.id, {'line_state' : 'noprocess'})
							break
						else:
							remain_qty = issue_used_qty - issue_pending_qty
							issue_qty = remain_qty
							print "remain_qty ()(()()))))))))))()()", remain_qty
							pending_depindent_qty =  0.0
							
							print "pending_po_depindent_qty ::::::::", pending_depindent_qty
							
							sql = """ update kg_depindent_line set issue_pending_qty=%s where id = %s"""%(pending_depindent_qty,bro_record.id)
							cr.execute(sql)
							#dep_line_obj.write(cr,uid, bro_record.id, {'line_state' : 'noprocess'})
							if remain_qty < 0:
								break	   
					
				# The below part will update production lot pending qty while issue stock to sub store #
				
				
					
				sql = """ select lot_id from kg_out_grn_lines where grn_id=%s""" %(move_record.id)
				cr.execute(sql)
				data = cr.dictfetchall()
			
				if data:
					print "Wizard data =====================>>>>", data
					val = [d['lot_id'] for d in data if 'lot_id' in d]
					issue_qty = move_record.product_qty
					for i in val:
						lot_rec = lot_obj.browse(cr,uid,i)
						print "lot_rec,,,,,,,,,,,,,,,,,,,,,,,", lot_rec
						move_qty = issue_qty
						print "move_qty move_qty<><><><><>", move_qty
						if move_qty > 0 and move_qty <= lot_rec.pending_qty:
							#move_qty = move_qty - lot_rec.issue_qty
							
							lot_pending_qty = lot_rec.pending_qty - move_qty
							print "lot_pending_qty...........iifff.......", lot_pending_qty
							lot_rec.write({'pending_qty': lot_pending_qty,'issue_qty': 0.0})
							break
						else:
							if move_qty > 0:								
								lot_pending_qty = lot_rec.pending_qty
								print "lot_pending_qty......esss........", lot_pending_qty
								remain_qty =  move_qty - lot_pending_qty
								print "remain_qty..................", remain_qty
								lot_rec.write({'pending_qty': 0.0})
							else:
								print "No Qty"  
						issue_qty = remain_qty
				else:
					print "No GRN entries....................."
							
								
								
							
			else:
				if move_record.move_type == 'cons':
					pick_record = move_record.picking_id
					print "pick_record:::::::::::", pick_record
					pick_record.write({'state': 'done'})
					
					

			#Quantiny must be Positive
			if wizard_line.quantity < 0:
				raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))

			#Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
			qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)
			


			if line_uom.factor and line_uom.factor <> 0:
				if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
					raise osv.except_osv(_('Warning!'), _('The unit of measure rounding does not allow you to ship "%s %s", only rounding of "%s %s" is accepted by the Unit of Measure.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
			if move_id:
				initial_uom = wizard_line.move_id.product_uom
				#qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
				#without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
				#if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
					#raise osv.except_osv(_('Warning!'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only rounding of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
			else:
				seq_obj_name =  'stock.picking.' + picking_type
				move_id = stock_move.create(cr,uid,{'name' : self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
													'product_id': wizard_line.product_id.id,
													'product_qty': wizard_line.quantity,
													'product_uom': wizard_line.product_uom.id,
													'prodlot_id': wizard_line.prodlot_id.id,
													'location_id' : wizard_line.location_id.id,
													'location_dest_id' : wizard_line.location_dest_id.id,
													'picking_id': partial.picking_id.id
													},context=context)
				stock_move.action_confirm(cr, uid, [move_id], context)
			partial_data['move%s' % (move_id)] = {
				'product_id': wizard_line.product_id.id,
				'product_qty': wizard_line.quantity,
				'product_uom': wizard_line.product_uom.id,
				'prodlot_id': wizard_line.prodlot_id.id,
			}
			if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
				partial_data['move%s' % (wizard_line.move_id.id)].update(product_price=wizard_line.cost,
																  product_currency=wizard_line.currency.id)
		
		
		stock_picking.do_partial(cr, uid, [partial.picking_id.id], partial_data, context=context)
		return {'type': 'ir.actions.act_window_close'}
		
		
kg_stock_partial_picking()

class kg_stock_partial_picking_line(osv.TransientModel):
	
	_inherit = 'stock.partial.picking.line'
	
	_columns = {
	
	'grn_qty': fields.float('Quantity'),
	
	
	}
	
	
kg_stock_partial_picking_line()

	
	
	
	
	
	
	
	
	
	
	
	
	
	
	



