# -*- coding: utf-8 -*-
##############################################################################
#
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).

#
##############################################################################
import math
import re

from _common import rounding

from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp


class kg_product(osv.osv):
	
	_name = "product.product"
	_inherit = "product.product"
	_columns = {
	
		#'minor_name': fields.many2one('kg.minormaster', 'Minor Name'),

		'capital': fields.boolean('Capital Goods'),
		'abc': fields.boolean('ABC Analysis'),
		'po_uom_coeff': fields.float('PO Coeff', required=True, help="One Purchase Unit of Measure = Value of(PO Coeff)UOM"),
		
		'type': fields.selection([('consu', 'Consumable Items'),('service','Service Items'),('cap','Capital Goods')], 'Product Type', 
				required=True, help="Consumable are product where you don't manage stock, a service is a non-material product provided by a company or an individual."),
		
		
	}
	
	_defaults = {
	
		'po_uom_coeff' : '1.0',
		
	}
	
	"""def write(self,cr,uid,ids,vals,context={}):

		if 'default_code' in vals:
			 raise osv.except_osv(_('Warning !'),_('You can not modify Product code'))
			 
		if 'name' in vals:
			 raise osv.except_osv(_('Warning !'),_('You can not modify Product Name'))		
				
		return super(kg_product, self).write(cr, uid, ids,vals, context)"""
	
	
kg_product()


	

