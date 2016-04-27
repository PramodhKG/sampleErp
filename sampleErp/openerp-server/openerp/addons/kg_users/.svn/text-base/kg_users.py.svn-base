from functools import partial
import logging
from lxml import etree
from lxml.builder import E

import openerp
from openerp import SUPERUSER_ID
from openerp import pooler, tools
import openerp.exceptions
from openerp.osv import fields,osv
from openerp.osv.orm import browse_record
from openerp.tools.translate import _


class kg_users(osv.osv):

	_name = "res.users"
	_inherit = "res.users"
	_description = "User Managment"
	
	_columns = {
	
	'dep_name' : fields.many2one('kg.depmaster', 'Dep.Name', required=True)
		
	}
		
kg_users()
