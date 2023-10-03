from __future__ import absolute_import, unicode_literals
from celery import shared_task
from main.models import Offer, Counter, Stat_10, Stat_24, Offerwall, Active, Account
from django.utils import timezone
import time, requests, traceback, urllib, os, json
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.files import File
import datetime as dt
from tempfile import TemporaryFile





@shared_task
def hourly():
	owals = Offerwall.objects.all()
	try:
		for x in owals:
			act1 = Active.objects.filter(wall=x.id)
			act12 = len(act1)
			if dt.datetime.now().hour == 0:
				Stat_24.objects.filter(unique=x.unique).delete()
			else:
				exst = Stat_24.objects.filter(unique=x.unique, hour=dt.datetime.now().hour)
				if len(exst) > 0:
					exst.delete()
			acc1 = Account.objects.get(unique=x.unique)
			bal = acc1.h_balance

			ba = Stat_24(unique=x.unique, earnings=bal,users=act12, hour=dt.datetime.now().hour)
			ba.save()
			act1.delete()
			acc1.h_balance = 0
			acc1.save()

	except:
		print(traceback.format_exc())


@shared_task
def daily():

	owals = Offerwall.objects.all()
	for x in owals:
		try:
			bal = 0
			users = 0
			for x1 in Stat_24.objects.filter(unique=x.unique):
				bal += x1.earnings
				users += x1.users

			obs = Stat_10.objects.filter(unique=x.unique).order_by('day')
			if len(obs) == 0:
				latest = 0
				newday = 0
			else:
				latest = obs.reverse()[0].day
				print(obs.reverse()[0].day)
				newday = latest+1
			if latest == 9:
				newday -= 1
				print(obs[0].day)
				obs[0].delete()
				for x1 in obs:
					x1.day -= 1
					x1.save()


			ba = Stat_10(unique=x.unique, earnings=bal, users=users, day=newday)
			ba.save()

		except:
			print(traceback.format_exc())


@shared_task
def c_offer():
	print('hit')
	while True:
		try:
			r = requests.get('https://api.adgatemedia.com/v2/offers?aff=75284&api_key=AA&wall_code=ZZ')
			objs = Offer.objects.all()
			ids = {}
			for x in objs:
				ids[x.id] = x.reward
			onrate = Counter.objects.get(name='rate').value
			adgat1 = []
			for x in r.json()['data']:
				if type(x['categories']) == dict:
					catsList = list(x['categories'].values())
				else:
					catsList = x['categories']
				print(catsList)
				adgat1.append(str(x['id']))
				x['payout'] = round((float(x['payout'])) * onrate, 7)
				gofr = False
				if str(x['id']) + "adgate" not in ids.keys():
					gofr = True
				elif float(ids[str(x['id']) + "adgate"]) != float(x['payout']):
					print(float(ids[str(x['id']) + "adgate"]))
					print(float(x['payout']))
					print('-----')
					Offer.objects.get(id=str(x['id']) + "adgate").delete()
					gofr = True
				elif x['mobile_only']:
					if 'iPad' not in catsList and 'iPhone' not in catsList and 'Android' not in catsList:
						Offer.objects.get(id=str(x['id']) + "adgate").delete()
						gofr = True

				if gofr:
					if float(x['payout']) <= 0:
						continue
					if x['mobile_only']:
						if 'iPad' not in catsList and 'iPhone' not in catsList and 'Android' not in catsList:
							catsList.append('Android')
							catsList.append('iPad')
							catsList.append('iPhone')
						filt = 'mobile'
					elif 'survey' in catsList or 'survey' in x['adgate_rewards']['requirements']:
						filt = 'survey'
					elif 'Credit Card Required' in catsList:
						filt = 'purchase'
					elif 'Lead Gen' in catsList or 'Email Submits' in catsList:
						filt = 'oneclick'
					else:
						filt = None
					#x['creatives']['icon']
					# try:
					# 	pc1 = requests.get(x['creatives']['icon']).content
					# except:
					# 	pc1 = ''
					# try:
					# 	#pic1 = requests.get(x['Offer']['icon']).content
					# 	result = urllib.urlretrieve(x['creatives']['icon'])
					# 	pic1 = File(open(result[0], 'rb'), str(x['id']) + 'adgate')
					# except:
					# 	pic1 = ''

					image_content = ContentFile(
					requests.get(x['creatives']['icon']).content)
					try:
						newOf = Offer(wall='adgate', name=x['adgate_rewards']['anchor'], date=timezone.now(), filter=filt,
									  id=str(x['id']) + 'adgate', reward=x['payout'], url=x['click_url'],  categories=catsList, countries=str(x['countries']),
									  description=x['adgate_rewards']['description'],
									  requirements=x['adgate_rewards']['requirements'])
						fullname = os.path.join(settings.MEDIA_ROOT, 'offers/', str(x['id']) + '0.png')
						if os.path.exists(fullname):
							os.remove(fullname)

						newOf.pic.save(str(x['id']) + '0.png', image_content, save=True)
						newOf.save()

					except:
						print(str(x['id']) + "adgate" not in ids.keys())
						print(float(ids[str(x['id']) + "adgate"]))
						print(float(x['payout']))
						print('-----')
						continue

			adgem1 = []
			r = requests.get('https://api.adgem.com/v1/all/campaigns?&appid=%s&token=%s' % (adgem_app, adgem_tok))
			for x in r.json()['data']:
				# print(r.json()['data'][x])
				x1 = x
				x = r.json()['data'][x]
				adgem1.append(str(x1))
				gofr = False
				rewa = round(float(x['Offer']['payout_usd'] * onrate), 7)
				if str(x1) + 'adgem' not in ids.keys():
					gofr = True
				elif float(ids[x1 + "adgem"]) != rewa:
					print('adgem')
					print(float(ids[x1 + "adgem"]))
					print(rewa)
					print('-----')
					gofr = True
					Offer.objects.get(id=str(x1) + 'adgem').delete()
				if gofr:

					if rewa <= 0:
						continue
					if x['Offer']['category_1'] == 'app':
						filt = 'mobile'
					elif x['Offer']['category_1'] == 'survey':
						filt = 'survey'
					elif x['Offer']['category_1'] == 'paid' or x['Offer']['category_1'] == 'trial':
						filt = 'purchase'
					elif x['Offer']['category_1'] == 'user_info_request':
						filt = 'oneclick'
					else:
						filt = None
					cats = []
					if x['OS']['android']:
						cats.append('Android')
					if x['OS']['ios']:
						cats.append('iPhone')
						cats.append('iPad')
					if len(cats) == 3 and filt != 'mobile' and x['Offer']['category_2'] != 'app':
						cats = []
						if filt is not None:
							cats.append(filt.capitalize())

					conts = []
					if x['Country']['include'] == []:
						conts.append('All')
					else:
						for b in x['Country']['include'].keys():
							conts.append(b)

					# try:
					# 	#pic1 = requests.get(x['Offer']['icon']).content
					# 	result = urllib.urlretrieve(x['Offer']['icon'])
					# 	pic1 = File(open(result[0], 'rb'), str(x1) + 'adgem')
					# except:
					# 	pic1 = ''
					image_content = ContentFile(
						requests.get(x['Offer']['icon']).content)

					newOf = Offer(wall='adgem', name=x['Offer']['name'], date=timezone.now(), filter=filt,
								  id=str(x1) + 'adgem',
								  reward=rewa, url=x['Offer']['tracking_url'],
								  categories=str(cats), countries=str(conts),
								  description=x['Offer']['description'],
								  requirements=x['Offer']['instructions'])
					fullname = os.path.join(settings.MEDIA_ROOT, 'offers/', str(x1) + '1.png')
					if os.path.exists(fullname):
						os.remove(fullname)

					newOf.pic.save(str(x1) + '1.png',image_content,save=True)
					newOf.save()


			r = requests.get(
				'http://www.offertoro.com/api/?pubid=FF&appid=AA&secretkey=ZZ',
				headers={
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					'Accept-Encoding': "gzip, deflate",
					'Accept-Language': 'en-US,en;q=0.5',
					'Host': 'www.offertoro.com',
					'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0'
				})
			ld = json.loads(str(r.text))
			offertoro = []
			for x in ld['response']['offers']:
				offertoro.append(str(x['offer_id']))
				x['payout'] = round(float(x['payout']) * onrate, 7)
				gofr = False
				if str(x['offer_id']) + "toro" not in ids.keys():
					gofr = True
				elif float(ids[str(x['offer_id']) + "toro"]) != float(x['payout']):
					print('toro')
					print(float(ids[str(x['offer_id']) + "toro"]))
					print(float(x['payout']))
					print('-----')
					Offer.objects.get(id=str(x['offer_id']) + "toro").delete()
					gofr = True
				if gofr:
					if float(x['payout']) <= 0:
						continue

					cats21 = []
					filt = ''
					if 'Mobile Apps' not in x['category']:
						filt = 'mobile'
						if 'android' in x['device']:
							cats21.append('Android')
						if 'iphone_ipad' in x['device']:
							cats21.append('iPhone')
							cats21.append('iPad')
						elif 'iphone' in x['device']:
							cats21.append('iPhone')
						elif 'ipad' in x['device']:
							cats21.append('iPad')
					else:
						cats21.append('')

					if filt == '':
						if 'survey' in x['category'].lower():
							filt = 'survey'
						else:
							filt = None
					# x['creatives']['icon']
					# try:
					# 	pc1 = requests.get(x['creatives']['icon']).content
					# except:
					# 	pc1 = ''
					# try:
					# 	#pic1 = requests.get(x['Offer']['icon']).content
					# 	result = urllib.urlretrieve(x['creatives']['icon'])
					# 	pic1 = File(open(result[0], 'rb'), str(x['id']) + 'adgate')
					# except:
					# 	pic1 = ''

					#[USER_ID]
					mlink = x['offer_url_easy']
					image_content = ContentFile(
						requests.get(x['image_url']).content)
					newOf = Offer(wall='toro', name=x['offer_name'], date=timezone.now(), filter=filt,
								  id=str(x['offer_id']) + 'toro', reward=x['payout'], url=mlink,
								  categories=cats21, countries=str(x['countries']),
								  description='',
								  requirements=x['call_to_action'])
					fullname = os.path.join(settings.MEDIA_ROOT, 'offers/', str(x['offer_id']) + '3.png')
					if os.path.exists(fullname):
						os.remove(fullname)

					newOf.pic.save(str(x['offer_id']) + '3.png', image_content, save=True)
					newOf.save()

			rems = 0
			for x in objs:
				if str(x.id).replace('adgate', '') not in adgat1 and str(x.id).replace('adgem', '') not in adgem1 and str(x.id).replace('ayet', '') not in ayet1 and str(x.id).replace('toro', '') not in offertoro:
					x.delete()
					rems+=1
			print(rems)
			print('-------------------------------------------------------')



			print('Done')
			break
		except:
			print('Offer Grab Error')
			print(traceback.format_exc())
			time.sleep(60)


#c_offer()
