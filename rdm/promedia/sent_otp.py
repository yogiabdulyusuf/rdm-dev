import requests

data="""
	<mt_data>
		<msg_type>txt</msg_type>
		<username>proM_demo</username>
		<password>WU66yN3rPV</password>
		<priority>1</priority>
		<msisdn_sender>ProMDemo</msisdn_sender>
		<msisdn>{}</msisdn>
		<message>{}</message>
		<dr_url>http://rmd-dev.server007.weha-id.com/api/v1.0/rdm/otp_dr</dr_url>
	</mt_data>
""".format('6281299322716','MTA OTP 9999')

#print(data)
x = requests.get('http://202.53.250.219:29006/sms_gateway/engine/bulk_receiver_api/bulk_mt_receiver_OTP.php', data=data)
print(x.text)
