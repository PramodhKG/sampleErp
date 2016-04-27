import time
from lxml import etree
from osv import fields, osv
from tools.translate import _
import pooler
import logging
import netsvc
import datetime as lastdate
import calendar

logger = logging.getLogger('server')


class customer_report(osv.osv):

	_name = 'customer.report'

	_columns = {
	
		'groupby':fields.many2one('res.partner.category','GroupBy',readonly=True,
					states={'draft':[('readonly',False)]}),
		'state_id':fields.many2one('res.country.state','State',readonly=True,
					states={'draft':[('readonly',False)]}),
		'country':fields.many2one('res.country','Country',readonly=True,
					states={'draft':[('readonly',False)]}),
		"rep_data":fields.binary("File",readonly=True),
        'state': fields.selection([('draft', 'Draft'),('done','Done')], 'Status', readonly=True),

		
		}
		
	_defaults = {
		'state': 'draft',
	}
	   
	def produce_xls(self, cr, uid, ids, context={}):
		
		import StringIO
		import base64
		
		try:
			import xlwt
		except:
		   raise osv.except_osv('Warning !','Please download python xlwt module from\nhttp://pypi.python.org/packages/source/x/xlwt/xlwt-0.7.2.tar.gz\nand install it')
		   
		cust_rec =self.browse(cr,uid,ids[0])
		group_id=cust_rec.groupby
		
		sql = """		
				SELECT distinct on (cust.id)
				cust.name as name,
				cust.phone as phone,
				cust.street as street,
				cust.street2 as street1,
				cust.city as city,
				cust.zip as zip,
				cust.website as website,
				cust.sp_size as sp_size,
				cust.sale_type as sale_type,
				cust.contact_person as contact_person,
				cust.function as job,
				cust.mobile as mobile,
				cust.fax as fax,
				cust.email as email,
				cust.capacity as capacity,
				cust.agent as agent,
				cust.abc as abc,
				cust.cst as cst,
				cust.ecc as ecc,
				cust.division as division,
				cust.range as range,
				cust.trade as trade,
				cust.vat as vat,
				cust.gst as gst,
				cust.ecc_range as ecc_range,
				state.name as state_name,
				country.name as country_name
											   
				FROM res_partner cust
								
				join res_country_state state on(state.id=cust.state_id)
				join res_country country on(country.id=cust.country_id)
				
				"""
		
		cr.execute(sql)		
		data = cr.dictfetchall()
		#data.sort(key=lambda data: data['state_id'])
		print "data <><><><><<><><><><<><><<>.........", data
		
		record={}
		sno=0
		wbk = xlwt.Workbook()
		style1 = xlwt.easyxf('font: bold on,height 240,color_index 0X36;' 'align: horiz center;''borders: left thin, right thin, top thin') 
		s1=0
		
		"""adding a worksheet along with name"""
		
		sheet1 = wbk.add_sheet('Customer Details')
		s2=1
		sheet1.col(0).width = 6000
		sheet1.col(1).width = 8000
		sheet1.col(2).width = 5000
		sheet1.col(3).width = 4000
		sheet1.col(4).width = 4000
		sheet1.col(5).width = 5000
		sheet1.col(6).width = 5500
		sheet1.col(7).width = 4000
		sheet1.col(8).width = 4000
		sheet1.col(9).width = 4000
		sheet1.col(10).width = 8000
		sheet1.col(11).width = 8000
		sheet1.col(12).width = 4000
		sheet1.col(13).width = 4000
		sheet1.col(14).width = 4000
		sheet1.col(15).width = 4000
		sheet1.col(16).width = 4000
		sheet1.col(17).width = 4000
		sheet1.col(18).width = 8000
		sheet1.col(19).width = 4000
		sheet1.col(20).width = 4000
		sheet1.col(21).width = 4000
		sheet1.col(22).width = 4000
		sheet1.col(23).width = 4000
		sheet1.col(24).width = 8000
		sheet1.col(25).width = 8000
		sheet1.col(26).width = 4000
		
		
		
		
		
		""" writing field headings """
		
		sheet1.write(s1,0,"Name",style1)
		sheet1.write(s1,1,"Street1",style1)
		sheet1.write(s1,2,"Street2",style1)
		sheet1.write(s1,3,"City",style1)
		sheet1.write(s1,4,"State",style1)
		sheet1.write(s1,5,"Zip",style1)
		sheet1.write(s1,6,"Country",style1)
		sheet1.write(s1,7,"Website",style1)
		sheet1.write(s1,8,"Spindles Size",style1)
		sheet1.write(s1,9,"Type of Sale",style1)
		sheet1.write(s1,10,"Contact Person",style1)
		sheet1.write(s1,11,"Job Position",style1)
		sheet1.write(s1,12,"Phone",style1)
		sheet1.write(s1,13,"Mobile",style1)
		sheet1.write(s1,14,"Fax",style1)
		sheet1.write(s1,15,"Email",style1)
		sheet1.write(s1,16,"Capacity Spindlage",style1)
		sheet1.write(s1,17,"Direct Agent",style1)
		sheet1.write(s1,18,"ABC",style1)
		sheet1.write(s1,19,"CST-TIN No",style1)
		sheet1.write(s1,20,"ECC No",style1)
		sheet1.write(s1,21,"Division",style1)
		sheet1.write(s1,22,"Product Range/Selling",style1)
		sheet1.write(s1,23,"Trade Consumer",style1)
		sheet1.write(s1,24,"VAT-TIN",style1)
		sheet1.write(s1,25,"CST/GST No",style1)
		sheet1.write(s1,26,"Range",style1)
		
		
		"""writing data according to query and filteration in worksheet"""
		print "sheet1........................", sheet1
		for  ele in data:
			
			sheet1.write(s2,0,ele['name'])
			sheet1.write(s2,1,ele['street'])
			sheet1.write(s2,2,ele['street1'])
			sheet1.write(s2,3,ele['city'])
			sheet1.write(s2,4,ele['state_name'])
			sheet1.write(s2,5,ele['zip'])
			sheet1.write(s2,6,ele['country_name'])
			sheet1.write(s2,7,ele['website'])
			sheet1.write(s2,8,ele['sp_size'])
			sheet1.write(s2,9,ele['sale_type'])
			sheet1.write(s2,10,ele['contact_person'])
			sheet1.write(s2,11,ele['job'])
			sheet1.write(s2,12,ele['phone'])
			sheet1.write(s2,13,ele['mobile'])
			sheet1.write(s2,14,ele['fax'])
			sheet1.write(s2,15,ele['email'])
			sheet1.write(s2,16,ele['capacity'])
			sheet1.write(s2,17,ele['agent'])
			sheet1.write(s2,18,ele['abc'])
			sheet1.write(s2,19,ele['cst'])
			sheet1.write(s2,20,ele['ecc'])
			sheet1.write(s2,21,ele['division'])
			sheet1.write(s2,22,ele['range'])
			sheet1.write(s2,23,ele['trade'])
			sheet1.write(s2,24,ele['vat'])
			sheet1.write(s2,25,ele['gst'])
			sheet1.write(s2,26,ele['ecc_range'])																							
			s2+=1
		
		
		"""Parsing data as string """
		cur_mon = time.strftime('%Y-%B')
		file_data=StringIO.StringIO()
		o=wbk.save(file_data)		
		"""string encode of data in wksheet"""		
		out=base64.encodestring(file_data.getvalue())
		"""returning the output xls as binary"""
		return self.write(cr, uid, ids, {'rep_data':out, 'name': 'Customer_Report'+'.xls','state': 'done'})
		
	def unlink(self, cr, uid, ids,context=None):
		for rec in self.browse(cr, uid, ids):
			print "rec.......", rec
			if rec.state == 'done':
				raise osv.except_osv(_('Unable to Delete !'),_('You can not delete Done state reports !!'))
		return super(customer_report, self).unlink(cr, uid, ids, context)
	
	
			
customer_report()

