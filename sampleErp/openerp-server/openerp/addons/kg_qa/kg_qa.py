from osv import fields, osv
import time
from datetime import datetime
import pooler
import netsvc
import sys
import os
from osv import osv,fields
from mx.DateTime import *
from tools.translate import _
import logging
import netsvc
logger = logging.getLogger('server')


class kg_qa(osv.osv):
	
	_name = "kg.qa"
	_description = "KG QA"
	
	_columns = {
	
	'name': fields.char('QA.NO', size=128, required=True, readonly=True),
	'date': fields.date('Date', readonly=True),
	'grn_id': fields.many2one('stock.picking', 'GRN.NO', required=True, readonly=True, states={'draft': [('readonly', False)]}),
	'user_id' : fields.many2one('res.users', 'User', required=True, readonly=True),
	'active': fields.boolean('Active', readonly=True, states={'draft': [('readonly', False)]}),
	'state': fields.selection([('draft', 'Draft'),('confirm', 'Confirmed'),('cancel','Cancel')], 'State'),
	'kg_qa_line': fields.one2many('kg.qa.line', 'kg_qa_id', 'QA Line')
	}
	
	_defaults = {
	
	'name' : '/',
	'date' : fields.date.context_today,
	'active' : 'True',
	'user_id' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
	'state' : 'draft',
	
	}
	
	def draft_qa(self, cr, uid, ids,context=None):
		
		self.write(cr,uid,ids,{'state':'draft'})
		return True
		
	def confirm_qa(self, cr, uid, ids,context=None):
		
		self.write(cr,uid,ids,{'state':'confirm'})
		return True
		
	
	def cancel_qa(self, cr, uid, ids, context=None):
		
		self.write(cr, uid,ids,{'state' : 'cancel'})
		return True
		
	def create(self, cr, uid, vals, context=None):
		
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'kg.qa') or '/'
		order =  super(kg_qa, self).create(cr, uid, vals, context=context)
		return order
		
	def update_qa(self,cr,uid,ids,context={}):
	   
		obj = self.browse(cr,uid,ids[0])
		grn_obj = self.pool.get('stock.picking')
		grn = grn_obj.browse(cr,uid,obj.grn_id.id)
		qa_line_obj = self.pool.get('kg.qa.line')
		qa_lines = []
		for move in grn.move_lines:
			for qa in self.browse(cr,uid,ids):
				line_ids = map(lambda x:x.id,qa.kg_qa_line)
				qa_line_obj.unlink(cr,uid,line_ids)
		
			if int(move.product_qty) <= 0:
				continue
			qa_lines.append((0, 0,  {'kg_stock_move_id':move.id,'product_id':move.product_id.id ,'kg_qa_id':obj.grn_id.id,'received_qty':move.product_qty,'accepted_qty':move.product_qty,'rejected_qty':0.0}))
		if qa_lines:
			self.write(cr,uid,[obj.id],{'kg_qa_line':qa_lines})
		
		return True
		
		
	def confirm_record(self,cr,uid,ids,values_passed=False,context={}):
            wf_service = netsvc.LocalService("workflow")
            obj = self.browse(cr,uid,ids[0])
            stock_pick_obj = self.pool.get('stock.picking')
            stock_move_obj =self.pool.get('stock.move')
            stock_loc_obj =self.pool.get('stock.location')
            vals={}
            #~ Product Product
            product_obj = self.pool.get('product.product')
            po_obj = self.pool.get('purchase.order')
            rejected_move_ids =[]
            accepted_move_ids =[]
            origin = ''
            journal_id = None
            anb_move_ids = []
            back_id = None

            for qa_line in obj.kg_qa_line:
                if type(values_passed) == 'list':
                    for ele in values_passed:
                        if ele['anb_qa_line'] == qa_line.id:
                            qa_line.anb_accepted_qty = ele['anb_accepted_qty']
                            qa_line.anb_rejected_qty = ele['anb_rejected_qty']
                #ele = qa_line.id
                move_data = qa_line.anb_stock_move_id
                #~ Check for product quantity for creating Sale Order
                back_id = move_data.picking_id.id
                
                if move_data.prodlot_id:
                    if move_data.prodlot_id.anb_expiry_date !=  qa_line.anb_expiry_date:              
                    #s = lot_obj.write(cr,uid,[move_data.prodlot_id.id],{'anb_expiry_date':'2013-01-01'})
                        sql="""update stock_production_lot set anb_expiry_date='%s' where id=%s"""%(qa_line.anb_expiry_date,move_data.prodlot_id.id)
                        cr.execute(sql)
                if (qa_line.anb_accepted_qty + qa_line.anb_rejected_qty )  > qa_line.anb_received_qty:
                    print (qa_line.anb_accepted_qty + qa_line.anb_rejected_qty),qa_line.anb_received_qty
                    #~ raise osv.except_osv(
                                #~ _('Qty error!'),
                                #~ _('Sum Greater than Original Qty in QA Master!'))

                if qa_line.anb_rejected_qty > qa_line.anb_received_qty:
                    
                    raise osv.except_osv(
                                _('Could not reject !'),
                                _('Your rejection quantity is greater than original quantity'))

                elif  qa_line.anb_rejected_qty <= 0 and qa_line.anb_accepted_qty <=0 :
                    #skip o qty
                    continue
                    
                else:
                    anb_move_ids.append(move_data.id)
                    
                    #now create rejected move
                    #stock_move_obj.write(cr,uid,[move_data.id],{'anb_rejected_qty':ids['form']['reject%s' %ele]})
                    orig = move_data.product_qty
                    if qa_line.anb_rejected_qty >= 0:
                        r_qty = qa_line.anb_rejected_qty
                        if move_data.location_dest_id.location_id:
                            same_level_reject = stock_loc_obj.search(cr,uid,[('location_id','=',move_data.location_dest_id.location_id.id),('usage','=','reject')])
                            if not same_level_reject:
                                raise osv.except_osv(
                                _('Could not reject !'),
                                _('The rejection location has not been defined, please ask the stores person !'))
                        else:
                            raise osv.except_osv(
                                _('Could not reject !'),
                                _('The location hierarchy is not properly defined, It must have a parent !'))

                        vals =   {'location_id': move_data.location_dest_id.id,
                            'location_dest_id': same_level_reject[0],#TODO,
                            'date_moved': time.strftime('%Y-%m-%d'),
                            #'picking_id': pickid,TODO: do it later part of the code
                            'state': 'done',
                            'product_qty':qa_line.anb_rejected_qty,
                            #'company_id': company_id or res_obj._company_default_get(cr, uid, 'stock.company', context=context)  ,
                            'move_history_ids': [],
                            'name':move_data.product_id.name or 'Reject Prod',
                            'date': (datetime.strptime(move_data.date, '%Y-%m-%d %H:%M:%S')),
                            'anb_sch_id':False,
                            'prodlot_id':move_data.prodlot_id and move_data.prodlot_id.id or False
                            }
                        stock_move_obj.write(cr,uid,[move_data.id],{'anb_rejected_qty':r_qty})
                    
                        rejected_move_ids.append(stock_move_obj.copy(cr,uid,move_data.id,vals))

                    accept_qty = qa_line.anb_accepted_qty
                    if accept_qty > 0:
                        if move_data.location_dest_id.location_id:
                            same_level_acc = stock_loc_obj.search(cr,uid,[('location_id','=',move_data.location_dest_id.location_id.id),('usage','=','internal')])
                            if not same_level_acc:
                                raise osv.except_osv(
                                _('Could not accept !'),
                                _('The accepted location has not been defined, please ask the stores person !'))
                        else:
                            raise osv.except_osv(
                                _('Could not accept !'),
                                _('The location hierarchy is not properly defined, It must have a parent !'))


                        #create accepted
                        vals =   {'location_id': move_data.location_dest_id.id,
                                'location_dest_id':same_level_acc[0],#TODO
                                'date_moved': time.strftime('%Y-%m-%d'),
                                #'picking_id': pickid,TODO: do it later part of the code
                                'state': 'done',
                                'product_qty':accept_qty,

                                #'company_id': company_id or res_obj._company_default_get(cr, uid, 'stock.company', context=context)  ,
                                'move_history_ids': [],
                                'name':move_data.product_id.name or 'Accept Prod',

                                'date': (datetime.strptime(move_data.date, '%Y-%m-%d %H:%M:%S')),
                                'anb_sch_id':False,
                                'prodlot_id':move_data.prodlot_id and move_data.prodlot_id.id or False,
                                }
                        stock_move_obj.write(cr,uid,[move_data.id],{'product_qty':accept_qty,'anb_accepted_qty':accept_qty})
                        accepted_move_ids.append(stock_move_obj.copy(cr,uid,move_data.id,vals))

                    if not origin:
                        origin =  move_data.picking_id.name
                        back_id = move_data.picking_id.id
                        journal_id = move_data.picking_id.stock_journal_id and move_data.picking_id.stock_journal_id.id or False

                #~ Check for Partner Category
            pick_id=  []
            if  rejected_move_ids:
                pick_vals = {
                                        'name': 'Rejected Picking',
                                        'origin': origin or '',
                                        'type': 'internal',
                                        'note': 'Rejected materials',
                                        'move_type': 'direct',#TODO check
                                        #'auto_picking': move[0][1][1] == 'auto',
                                        'stock_journal_id': journal_id,
                                        #'company_id': move[0][1][4] or res_obj._company_default_get(cr, uid, 'stock.company', context=context),
                                        #'address_id': picking.address_id.id,
                                        'invoice_state': 'none',
                                        'backorder_id':back_id,
                                        'qa_type':'reject',
                                        'note':obj.anb_notes,
                                        #'date': picking.date,
                                        'state':'done'
                                    }
                pick_id.append( stock_pick_obj.create(cr, uid, pick_vals))
                #stock_pick_obj.action_confirm(cr,uid,pick_id)

                stock_move_obj.write(cr,uid,rejected_move_ids,{'picking_id':pick_id[-1]})
                wf_service.trg_validate(uid, 'stock.picking', pick_id[-1], 'button_done', cr)

            if  accepted_move_ids:
                pick_vals = {
                                        'name': 'Accepted Picking',
                                        'origin': origin or '',
                                        'type': 'internal',
                                        'note': 'Accepted materials',
                                        'move_type': 'direct',#TODO check
                                        #'auto_picking': move[0][1][1] == 'auto',
                                        'stock_journal_id': journal_id,
                                        #'company_id': move[0][1][4] or res_obj._company_default_get(cr, uid, 'stock.company', context=context),
                                        #'address_id': picking.address_id.id,
                                        'invoice_state': 'none',
                                        #'date': picking.date,
                                        'backorder_id':back_id,
                                        'qa_type':'accept',
                                        'note':obj.anb_notes,
                                        'state':'done'
                                    }
                pick_id.append(stock_pick_obj.create(cr, uid, pick_vals))
                stock_move_obj.write(cr,uid,accepted_move_ids,{'picking_id':pick_id[-1]})
                wf_service.trg_validate(uid, 'stock.picking', pick_id[-1], 'button_done', cr)
            if pick_id:                
                stock_pick_obj.write(cr, uid, pick_id, {'state':'done'})
            if move_data.picking_id.id and move_data.picking_id.anb_mode == 'boe':
                grn = move_data.picking_id.id
                bill_search_ids=[]
                po_search_ids=[]
                ship_search_ids=[]
                bill_search_ids = bill_obj.search(cr,uid,[('anb_grn_id','=', grn)])
                bill_br_lst = bill_obj.browse(cr,uid,bill_search_ids)
                for bill_br in bill_br_lst:
                    ship_search_id = ship_obj.search(cr,uid,[('id','=', bill_br.anb_ship_id.id)])
                    ship_search_ids.append(ship_search_id)
                po_search_ids = po_obj.search(cr,uid,[('anb_shipment_id','=', ship_search_ids)])
                pur_orders = po_obj.browse(cr,uid,po_search_ids) 
                total_lines_with_zero = 0
                for pur_order in pur_orders:
                    for po_line in  pur_order.order_line:
                        if po_line.anb_pending_quantity == 0.0:
                            total_lines_with_zero +=1
                if len(pur_orders[0].order_line) == total_lines_with_zero:
                    po_obj.write(cr,uid,[pur_order.id],{'anb_state':'grn','state':'closed'})
            if move_data.picking_id.id and move_data.picking_id.anb_mode == 'withpo':
                purchase_grn = move_data.picking_id.id
                po_grn_search = po_obj.search(cr,uid,[('anb_grn_id','=', purchase_grn)])
                po = po_obj.browse(cr,uid,po_grn_search)                
                total_lines_with_zero = 0
                for order in po:
                    for line in  order.order_line:
                        if line.anb_pending_quantity == 0.0:
                            total_lines_with_zero +=1
                if len(po[0].order_line) == total_lines_with_zero:
                    po_obj.write(cr,uid,[order.id],{'anb_state':'grn','state':'closed'})
            if back_id:

                wf_service.trg_validate(uid, 'stock.picking', back_id, 'button_done', cr)
            if len(anb_move_ids):
                        stock_move_obj.action_done(cr, uid, anb_move_ids,
                                context=context)            
            self.write(cr,uid,ids,{'state':'done'})
            return True

kg_qa()

class kg_qa_line(osv.osv):
	
	_name = 'kg.qa.line'
	
	_columns = {
	
	'kg_qa_id':fields.many2one('kg.qa', 'Quality Acceptance',required=True),
	'product_id': fields.many2one('product.product', 'Product Name', required=True, readonly=True),
	'received_qty': fields.float('Received Qty', digits=(16,3),readonly=True),
	'accepted_qty': fields.float('Accepted Qty', digits=(16,3)),
	'rejected_qty': fields.float('Rejected Qty', digits=(16,3), states={'draft': [('readonly', False)]} ),
	'kg_stock_move_id':fields.many2one('stock.move',"Stock Move"),
	'note': fields.text('Remarks', readonly=True, states={'draft': [('readonly', False)]})
	
	}
	
	def onchange_accepted(self, cr, uid, ids, received_qty,accepted_qty,rejected_qty):
		   
		if accepted_qty or accepted_qty ==0.00: 
			
			new_rejected_qty = received_qty - accepted_qty
		  
			return{'value':{'rejected_qty':new_rejected_qty}}
		return False
		
	def onchange_rejected(self, cr, uid, ids, received_qty,accepted_qty,rejected_qty):
			   
		if rejected_qty or rejected_qty == 0.00: 
			new_accepted_qty = received_qty - rejected_qty
			return{'value':{'accepted_qty':new_accepted_qty}}
		return False
		
		
	
kg_qa_line()


	
	
