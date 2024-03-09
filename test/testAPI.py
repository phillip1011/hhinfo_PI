import requests
headers = {'Content-Type': 'application/json'}

request_string = "ip=10.8.1.252:4661"
request_string = "ip="

api_url_base = "http://35.221.198.141:80/api/v1/data/device"

response = requests.get(api_url_base,params=request_string, headers=headers, timeout=3) 

print (response.text)


