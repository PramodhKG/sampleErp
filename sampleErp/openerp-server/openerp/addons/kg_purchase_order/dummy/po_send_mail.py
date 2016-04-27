from datetime import *
import time
from osv import fields, osv
from tools.translate import _
import netsvc
import decimal_precision as dp
from itertools import groupby
from datetime import datetime, timedelta,date


def send_email(self, cr, uid, ids):
		logger.info('[KG ERP] Class: anb_sales_sale_line, Method: send_email called...')
		so_line_browse = self.browse(cr, uid, ids)	
		so_browse = so_line_browse[0].order_id 
		if so_browse.partner_id.email:
			all_so_lines = self.search(cr, uid, [('order_id', '=', so_line_browse[0].order_id.id)])  
			all_so_lines_browse = self.browse(cr, uid, all_so_lines)		
			part_address = self.pool.get('res.partner.address')  
			part_address_search = part_address.search(cr, uid, [('partner_id','=',so_browse.partner_id.id)])		
			partner_address_browse = part_address.browse(cr, uid, part_address_search)
			body_part_1 = """\
			<html>
				<body>
					<p>
						<h1><center><b>Anabond Limited</b></center></h1><br />
						<center>No 15, 2nd Cross Street</center><br />
						<center>Indira Nagar Adyar, Chennai - 600020<br /></center>
					</p>
					<hr>			
				<center>OrderAcknowledgement</center><br/>"""	 
				
			date_order = str(so_browse.date_order)	
			date_order = date_order.split("-")	
			date_order = date_order[2]+"/"+date_order[1]+"/"+date_order[0]
			
			body_part_2 = """Our Ref.: """+so_browse.name+"""<br/>
							 Date: """+date_order+"""
							<br/>
							<br/>
							<br/>
							"""  
			body_part_3 = """For<br/>
							&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""+so_browse.partner_id.name or ''+"""<br/>
							&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""+partner_address_browse[0].street or ''+"""<br/>
							&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""+partner_address_browse[0].street2 or ''+"""<br/>
							&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""+partner_address_browse[0].country_id.name or ''+"""<br/>
							&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""+str(partner_address_browse[0].zip) or '' +"""<br/>
							<br/>
							<br/>
							<br/>
							""" 
							
			if so_browse.anb_purchase_order_num:
				po_no = so_browse.anb_purchase_order_num
			else:
				po_no = "-"
				
			body_part_4 = """Dear Sir,<br/>
				&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Sub: Supply of Materials<br/>
				&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ref: Your P.O.No. """+po_no+"""<br/>		
			"""  
			body_part_5 = """<p>We acknowledge with thanks the receipt of your above referred Purchase Order and thank you very much for the same. We wish to inform you that the
				following materials will be despatched on or before due date mentioned below:-
				(Subject to your Payment Outstanding Position)</p>"""	  
			body_part_6 = """<table border='1'> 
					<tr>
						<th colspan='2'>SL.No</th>
						<th colspan='2'>Product Description</th>
						<th colspan='2'>Order Qty</th>
						<th colspan='2'>Uom</th>
						<th colspan='2'>Due Date</th>
					</tr>"""				
			body_part_7 = ""
			for position, so_line in enumerate(all_so_lines_browse):
					due_date = so_browse.date_order
					due_date = datetime.strptime(due_date,"%Y-%m-%d")
					due_date = due_date+timedelta(days=so_line.delay)			  
					due_date = datetime.strftime(due_date,"%Y-%m-%d")			  
					due_date = str(due_date).split("-")				  
					due_date = due_date[2]+"/"+due_date[1]+"/"+due_date[0]
					body_part_7 += """<tr>
						<td colspan='2'>"""+str(position+1)+"""</td>
						<td colspan='2'>"""+so_line.product_id.name_template+"""</td>
						<td colspan='2'>"""+str(so_line.product_uos_qty)+"""</td>
						<td colspan='2'>"""+so_line.product_uos.name+"""</td>
						<td colspan='2'>"""+due_date+"""</td>
					</tr>
					"""  
			body_part_8 = """</table>		   
				<br/>
				<br/>		  
				The despatch details will be sent to you,no sooner you order is executed.<br/>
				
				<br/>
				<br/>
					Thanking You
				<br/>
				<br/>
					Very Cordially Yours<br/>
				For<b>Anabond Limited</b><br/>
				<br/>
				<br/>
				Authorised Signatory<br/>
				<br/>
				<br/>
				Note: This is a computer generate output,does not require signature
				</body>
			</html>
			"""
			smtp_obj = self.pool.get('anb.smtp')
			smtp_server_sr = smtp_obj.search(cr, uid, [('priority','=',1)])	  
			smtp_server_br = smtp_obj.browse(cr, uid, smtp_server_sr)   
			if smtp_server_br:
				me = 'anabond@amachu.com'
				you = 'shree@amachu.com'
				msg = MIMEMultipart('alternative')
				msg['Subject'] = "[Anabond] Sale Order Acknowledgement"
				msg['From'] = me
				msg['To'] = you
				html = body_part_1+body_part_2+body_part_3+body_part_4+body_part_5+body_part_6+body_part_7+body_part_8
				part2 = MIMEText(html, 'html')
				msg.attach(part2)
				s = smtplib.SMTP(smtp_server, smtp_port)
				login = s.login(smtp_email, smtp_password)
				mailsend = s.sendmail(me, you, msg.as_string())
				s.quit()
				logger.info('[Anabond ERP] Email sent sucessfully...')
				return True
			else:
				self.write(cr,uid,ids,{'state':'done'})
				logger.info('[Anabond ERP] Email not sent since SMTP server isn\'t defined...')		  
				return False
		else:
			logger.info('[Anabond ERP] Email not sent since Partner doesn\'t have e-mail id...')			
			return False
