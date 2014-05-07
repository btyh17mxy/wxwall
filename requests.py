import json
import requests
url = 'https://mp.weixin.qq.com/cgi-bin/login?lang=zh_CN'
payload = {}
payload['username'] = 'btyh17mxy@gmail.com'
payload['imgcode'] = ''
payload['f'] = 'json'
payload['pwd'] = '4f65517f1bd05369567631bb2d34553e'
headers = {}
headers['x-requested-with'] = 'XMLHttpRequest'
headers['referer'] = 'https://mp.weixin.qq.com/cgi-bin/loginpage?t=wxm2-login&lang=zh_CN'
r = requests.post(url, data = payload, headers = headers)
print r.text
# OUT: {"base_resp":{"ret":0,"err_msg":"ok"},"redirect_url":"\/cgi-bin\/home?t=home\/index&lang=zh_CN&token=1225292380"}

c = r.cookies
for key in c.keys():
    print c[key]

# OUT: 3077564127
# OUT: 3077564127
# OUT: AgSgs/KByj4FmadXmDK8d69z
# OUT: UDR6NWZFSGNGSFRjMkEwWU9zNkFCTWJfdDZ6V1ZpdjZxS280dWdCMXNJODBMVzQ2MzlINF9VVWkyMTFSN1J6OWJTTnc0OFV3SXhDdDZxZUFaUERvUDczeW56eTZyS0c2enFDanpHUE50bFJlTWlSQngrdDlRNHdjZzlIRGppZUQ=
# OUT: gh_8248b59fba21
