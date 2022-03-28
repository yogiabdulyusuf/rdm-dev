<html>
<head>
    <style type="text/css">
    	${css}
    </style>
</head>
<body> 
%for o in objects :
	<h1>General Information</h1>	
	<table>
		<tr><td><b>Report Name</b></td><td>:</td><td>${o.name}</td></tr>
		<tr><td><b>Type</b></td><td>:</td><td>${o.type}</td></tr>
		<tr><td><b>Calculation</b></td><td>:</td><td>${o.calculation}</td></tr>
		<tr><td><b>Description</b></td><td>:</td><td>${o.description}</td></tr>								
		
	</table>
	<h1>Additional Information</h1>
	<table border=1>
		<tr><td width="25%">Start Date</td><td width="25%">${ formatLang(o.start_date, date=True)}</td><td width="25%">Coupon Spend Amount</td><td width="25%">${o.coupon_spend_amount}</td></tr>			
		<tr><td>End Date</td><td>${ formatLang(o.end_date, date=True)}</td><td>Point Spend Amount</td><td>${o.point_spend_amount}</td></tr>
		<tr><td>Last Redeem</td><td>${ formatLang(o.last_redeem, date=True)}</td><td>Point Limit</td><td>${o.limit_point}</td></tr>
		<tr><td>Draw Date</td><td>${ formatLang(o.draw_date, date=True)}</td><td>Point Expired Date</td><td>${ formatLang(o.point_expired_date, date=True)}</td></tr>
	</table>
	<h1>Filters</h1>
	<h3>Segment</h3>
	%for segment_id in o.segment_ids:
		<ul>
			<li>${segment_id.segment_id.name}</li>
		</ul>
	%endfor
	<h3>Gender</h3>
	%for gender_id in o.gender_ids:
		<ul>
			<li>${gender_id.gender_id.name}</li>
		</ul>
	%endfor
	<h3>Religion</h3>
	%for religion_id in o.religion_ids:
		<ul>
			<li>${religion_id.religion_id.name}</li>
		</ul>
	%endfor
	<h3>Ethnic</h3>
	%for ethnic_id in o.ethnic_ids:
		<ul>
			<li>${ethnic_id.ethnic_id.name}</li>
		</ul>
	%endfor
	<h3>Tenant</h3>
	%for tenant_id in o.tenant_ids:
		<ul>
			<li>${tenant_id.tenant_id.name}</li>
		</ul>
	%endfor
	<h3>Marital</h3>
	%for marital_id in o.marital_ids:
		<ul>
			<li>${marital_id.marital_id.name}</li>
		</ul>
	%endfor	
	<h3>Interest</h3>
	%for interest_id in o.interest_ids:
		<ul>
			<li>${interest_id.interest_id.name}</li>
		</ul>
	%endfor	
	<h3>Card Type</h3>
	%for card_type_id in o.card_type_ids:
		<ul>
			<li>${card_type_id.card_type_id.name}</li>
		</ul>
	%endfor	
	<h3>Tenant Category</h3>
	%for tenant_category_id in o.tenant_category_ids:
		<ul>
			<li>${tenant_category_id.tenant_category_id.name}</li>
		</ul>
	%endfor	
	<h3>Participant</h3>	
	%for participant_id in o.ayc_participant_ids:
		<ul>
			<li>${participant_id.participant_id.name}</li>
		</ul>
	%endfor	
	<h1>Rules</h1>
	%for rules_id in o.rules_ids:
		<h3>${rules_id.rules_id.name} (${rules_id.schemas})</h3>
		<ul>
			<li>${rules_id.rules_id.apply_for}</li>
			<li>${rules_id.rules_id.operation}</li>
			<li>${rules_id.rules_id.calculation}</li>
			<li>${rules_id.rules_id.quantity}</li>
		</ul>		
		<br/>
	%endfor
%endfor
</body>
</html>