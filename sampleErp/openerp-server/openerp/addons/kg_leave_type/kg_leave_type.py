from openerp import addons
from openerp.osv import fields, osv
from openerp import tools

class kg_leave_type(osv.osv):
    _name = 'hr.holidays.status'
    _description = "Leave"
    _inherit= 'hr.holidays.status'
   
    _columns = {
        
        'double_validation': fields.boolean('Apply Double Validation', invisible=True,help="When selected, the Allocation/Leave Requests for this type require a second validation to be approved."),
        'color_name': fields.selection([('red', 'Red'),('blue','Blue'), ('lightgreen', 'Light Green'), ('lightblue','Light Blue'), ('lightyellow', 'Light Yellow'), ('magenta', 'Magenta'),('lightcyan', 'Light Cyan'),('black', 'Black'),('lightpink', 'Light Pink'),('brown', 'Brown'),('violet', 'Violet'),('lightcoral', 'Light Coral'),('lightsalmon', 'Light Salmon'),('lavender', 'Lavender'),('wheat', 'Wheat'),('ivory', 'Ivory')],'Color in Report', invisible=True,required=True, help='This color will be used in the leaves summary located in Reporting\Leaves by Department.'),
        'active': fields.boolean('Active', invisible=True,help="If the active field is set to false, it will allow you to hide the leave type without removing it."),
        }

kg_leave_type()

