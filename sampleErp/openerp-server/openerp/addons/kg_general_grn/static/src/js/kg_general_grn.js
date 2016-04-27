openerp.kg_general_grn = function (instance)
{  
var _t = instance.web._t;
	_lt = instance.web._lt;
var QWeb = instance.web.qweb;	
	instance.kg_general_grn = {};
    instance.web.form.widgets.add('star', 'instance.kg_general_grn.Mywidget');
    instance.kg_general_grn.Mywidget = instance.web.form.FieldChar.extend(
        {
        template : "star",
        init: function () {
            this._super.apply(this, arguments);

        },
        start: function (ids) {
			var model= new instance.web.Model("kg.general.grn")
			model.call("expiry_alert",[ids]).then(function (i) {
				var title="<div class='grad3'><center><font color='white'>Today Expiry Reminders</font></center></div>"
				var body="<div class='sub'>"+
							"<table id='table1'>"+
							"<tr><th>Product Name</th><th>GRN No</th><th>Expiry Date</th><th>Batch No</th></tr>"
				alert(i);
				n=i.length;
				if (n!=0){
					var body_1 = ''				
					for(var m=0;m<n;m++) {
						body_1 += "<tr><td>"+i[m][0]+"</td><td>"+i[m][1]+"</td><td>"+i[m][2]+"</td><td>"+i[m][3]+"</td></tr>"
					}
					body_1 += "</table>"+
								"</div>"
					body = body + body_1
					var self = this;
					var x=true
					var tiry=instance.webclient.notification.warn(_t(title), _t(body), x);
					setTimeout(function() {tiry.close();}, 9000)
					//To display the POP-up for every 'N' seconds
					this.__blur_timeout = setInterval(function () {
					var tiry=instance.webclient.notification.warn(_t(title), _t(body), x);
					setTimeout(function() {tiry.close();}, 9000)
					}, 45000);


																
				}
				else{
					alert('null');
				}	
			});

			
		},
    });
};


