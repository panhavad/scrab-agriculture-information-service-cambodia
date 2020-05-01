#this program will accept the id of the item you want to get the 
import requests
import json
import agents
from proxy import get_proxies
from itertools import cycle

timeout = 3
error_counter = 0
raw_list = []
num_category = 50
price_types = ['RP', 'WP']
refresh_prox_counter = 0
working_prox = []

proxies = get_proxies()
proxy_pool = cycle(proxies)
print("Total Proxies =", len(proxies))

try:
	with open('data/commodity-category.json', 'r') as category_file:
		commodities = category_file.read()
except Exception as e:
	pass

for category_index in range(1, num_category):
	headers = {'User-Agent': agents.get_random_agent()}
	requested_category = requests.get("https://amis.org.kh/api/marketapp/category-commodities?locale=1&categoryCode="+str(category_index),
		headers=headers)
	category_raws = json.loads(requested_category.text)
	if len(category_raws):
		for raw in category_raws:
			raw_list.append(raw) 
	else:
		if error_counter == timeout:
			break
		error_counter += 1

try:
	if  len(json.loads(commodities)) < len(raw_list):
		with open('data/commodity-category.json', 'w+') as category_file:
			category_file.write(json.dumps(raw_list, indent=4, sort_keys=True))
			commodities = category_file.read()
except Exception as e:
	with open('data/commodity-category.json', 'w+') as category_file:
			category_file.write(json.dumps(raw_list, indent=4, sort_keys=True))
			commodities = category_file.read()

for price_type in price_types:
	print('----', price_type, '----')
	for commodity_code in [commodity['commodityCode'] for commodity in json.loads(commodities)]:
		url = "https://amis.org.kh/api/marketapp/commodity-prices?maxAge=5&locale=1&commodityCode="+ str(commodity_code) +"&commodityCode1=0&commodityCode2=0&dataseries="+ price_type
		price_raws = []
		
		print('Processing --', commodity_code)
		
		headers = {'User-Agent': agents.get_random_agent()}

		for i in range(0, len(proxies)):
			try:
				print("Proxy --", proxy)
				requested_commodity_price = requests.get(url, proxies={"http": proxy, "https": proxy}, headers=headers)
				price_raws = json.loads(requested_commodity_price.text)
				break
			except Exception as e:
				proxy = next(proxy_pool)
				print("Skipping. Connnection error")
				if refresh_prox_counter == 10:
					refresh_prox_counter = 0
					proxies = get_proxies()
					print('--------------------------------------------refresh----------------------------------------')
				else:
					refresh_prox_counter += 1
		# try:
		# 	price_raws = json.loads(requested_commodity_price.text)
		# except Exception as e:
		# 	print(requested_commodity_price.text)
		# 	raise e
		# 	exit()
		if len(price_raws):
			commodity_pk = price_raws[0]['code'] + '-' + price_raws[0]['name'].replace(" ","")
			with open('data/'+ price_type +'/'+ commodity_pk +'.json', 'w+') as commodity_price:
				commodity_price.write(json.dumps(price_raws, indent=4, sort_keys=True))
				print(commodity_pk, "-> Saved")
