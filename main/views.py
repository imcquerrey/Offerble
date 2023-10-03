from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from datetime import datetime
#from django.contrib.gis.geoip2 import GeoIP2
import requests, traceback, time, threading,hashlib,os,binascii, random, string, smtplib, base64, json
from main.models import Offer, US_ValidPostBack, Client_InvalidPostBack, Client_ValidPostBack, Offerwall, Invoice, Stat_10, Stat_24, Account, Mobile, Featured, S_Invoice, Counter, Active, Clicked
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ipware import get_client_ip
import ast
import urllib.parse as urlparse
from urllib.parse import parse_qs
import ipaddress
from django.template.defaulttags import register
from django.core.exceptions import *
from random import randint

@register.filter
def get_item(dictionary, key):
	return dictionary[key]

siteloc = '/var/www/mysite/'


def hash_password(password):
	"""Hash a password for storing."""
	salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
	pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
								salt, 100000)
	pwdhash = binascii.hexlify(pwdhash)
	return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
	"""Verify a stored password against one provided by user"""
	salt = stored_password[:64]
	stored_password = stored_password[64:]
	pwdhash = hashlib.pbkdf2_hmac('sha512',
								  provided_password.encode('utf-8'),
								  salt.encode('ascii'),
								  100000)
	pwdhash = binascii.hexlify(pwdhash).decode('ascii')
	return pwdhash == stored_password


def index(request):
	try:
		v = request.session['email']
		acc = Account.objects.get(email=v)
		return redirect('/dashboard')
	except:
		pass

	return render(request, 'main/index.html', {})

def dashboard(request):
	try:
		v = request.session['email']
		acc = Account.objects.get(email=v)
	except:
		return redirect('/')

	stat10 = Stat_10.objects.filter(unique=acc.unique).order_by('day')
	stat10_user = []
	stat10_earn = []
	for x in stat10:
		stat10_user.append(x.users)
		stat10_earn.append(x.earnings)
	for x in range(10-len(stat10_user)):
		stat10_user.append(0)
		stat10_earn.append(0)

	stat24 = Stat_24.objects.filter(unique=acc.unique).order_by('hour')
	stat24_user = []
	stat24_earn = []
	for x in stat24:
		stat24_user.append(x.users)
		stat24_earn.append(x.earnings)
	for x in range(24 - len(stat24_user)):
		stat24_user.append(0)
		stat24_earn.append(0)
	stat24_user.insert(0, 'Hourly Active')
	stat24_earn.insert(0, 'Total Earnings')
	stat10_user.insert(0, 'Daily Active Users')
	stat10_earn.insert(0, 'Total Earnings')




	return render(request, 'main/dashboard.html', {'rev': format(acc.balance, '.2f'), 'clicks': acc.clicks, 'conv': acc.conversions, 'rpc': format(acc.rpc, '.2f'), 'stat10_earn': str(stat10_earn), 'stat10_user': stat10_user, 'stat24_earn': stat24_earn, 'stat24_user': stat24_user })

def apps(request):
	if request.method == 'GET':
		try:
			v = request.session['email']
			acc = Account.objects.get(email=v)
		except:
			return redirect('/')
		walls = Offerwall.objects.filter(unique=acc.unique)

		return render(request, 'main/apps.html', {'walls': walls})
	elif request.method == 'POST':
		try:
			v = request.session['email']
			acc = Account.objects.get(email=v)
		except:
			return redirect('/')

		id1 = str(request.POST.get('id1', '')).lower().strip()
		name = str(request.POST.get('name', '')).strip()
		postback = str(request.POST.get('postback', '')).strip()
		curname = str(request.POST.get('curname', '')).strip()
		curnames = str(request.POST.get('cursname', '')).strip()
		curaname = str(request.POST.get('curaname', '')).strip()
		curmulti = str(request.POST.get('curmulti', '')).strip()
		del1 = str(request.POST.get('del1', '')).strip()
		serc = str(request.POST.get('serc', '')).strip()
		try:
			if id1 == 'null':
				nwall = Offerwall(unique= acc.unique,name=name, postback=postback, currency_name=curname, currencys_name=curnames, currency_abr=curaname, currency_mult=curmulti, secret=serc)
				nwall.save()
				return JsonResponse({'status': 'success', 'message': ''})
			else:
				owall = Offerwall.objects.get(id=int(id1))
				if 'del' == del1:
					owall.delete()
				else:
					owall.name = name
					owall.postback = postback
					owall.currency_name = curname
					owall.currencys_name = curnames
					owall.currency_abr = curaname
					owall.currency_mult = float(curmulti)
					owall.save()
				return JsonResponse({'status': 'success', 'message': ''})
		except:
			return JsonResponse({'status': 'failure', 'message': 'Not all fields were properly filled'})


def handler404(request, exception=None):
	return redirect('/')

def privacy(request):
	return render(request, 'main/privacy.html', {})

def profile(request):
	try:
		v = request.session['email']
		acc = Account.objects.get(email=v)
	except:
		return redirect('/')
	return render(request, 'main/profile.html', {})


def activeoffers(request):
	if request.method == 'GET':
		try:
			v = request.session['email']
			acc = Account.objects.get(email=v)
		except:
			return redirect('/')

		country = "US"
		try:
			feat = Featured.objects.get(unique=acc.unique)
			feat1 = True
		except:
			feat1 = False


		offerz = Offer.objects.order_by('orderit')
		offerz1 = offerz.values()
		if feat1:
			idsz = []
			for x in offerz1:
				x['pic'] = 'http://127.0.0.1:8000/media/offers/null/' + x['pic']
				x['reward'] = round((x['reward']), 3)
				x['mn'] = str(random.randint(000000, 999999))
				if x['id'] in feat.value:
					x['featured'] = True
					x['fea'] = 2
				elif x['featured']:
					x['featured'] = False
					x['fea'] = 1
				else:
					x['fea'] = 0
				idsz.append(x['id'])
			js = ast.literal_eval(feat.value)
			js1= ast.literal_eval(feat.value)
			for x in js1.keys():
				if x not in idsz:
					del js[x]
			feat.value = str(js)
			feat.save()
		else:
			for x in offerz1:
				x['pic'] = 'http://127.0.0.1:8001/media/offers/null/' + x['pic']
				x['reward'] = round((x['reward']), 3)
				x['mn'] = str(random.randint(000000, 999999))
				if x['featured']:
					x['fea'] = 1
					x['featured'] = False
				else:
					x['fea'] = 0

		offerz1 = sorted(offerz1, key=lambda k: k['fea'], reverse=True)

		return render(request, 'main/active.html', {'offers': offerz1})
	elif request.method == 'POST':
		try:
			v = request.session['email']
			acc = Account.objects.get(email=v)
		except:
			return redirect('/')
		meth1 = json.loads(request.POST.get('feat', ''))
		try:
			fc = Featured.objects.get(unique=acc.unique)
			olddict = ast.literal_eval(str(fc.value).strip())
			#olddict2 = ast.literal_eval(str(fc.value).strip())
			for x in meth1.keys():
				if str(meth1[x]).lower() == 'true':
					olddict[x] = meth1[x]
				else:
					del olddict[x]
			# for x in olddict2.keys():
			# 	if x not in meth1:
			# 		del olddict[x]

			fc.value = str(olddict)
			fc.save()
		except:
			print(traceback.format_exc())
			fc = Featured(unique=acc.unique, value=str(meth1))
			fc.save()

		return JsonResponse({'status': 'success', 'message': "Saved"})


def payments(request):
	if request.method == 'GET':
		try:
			v = request.session['email']
			acc = Account.objects.get(email=v)
		except:
			return redirect('/')

		inv = S_Invoice.objects.filter(unique=acc.unique).values()
		invs = Invoice.objects.filter(unique=acc.unique)
		for x in inv:
			if x['method'] == 'wire':
				if x['acc_type'] == 'Business':
					x['opp'] = 'Personal'
				else:
					x['opp'] = 'Business'
					x['acc_type'] = 'Personal'
		return render(request, 'main/payments.html', {'bal': format(acc.balance, '.2f'), 'saved': inv, 'invoices': invs})
	elif request.method == 'POST':
		try:
			v = request.session['email']
			acc = Account.objects.get(email=v)
		except:
			return redirect('/')
		sav = str(request.POST.get('save', ''))
		meth1 = str(request.POST.get('method', '')).lower().strip()
		if 'us' == meth1:
			email = str(request.POST.get('email', '')).lower().strip()
			amount = str(request.POST.get('amount', '')).strip()
			fname = str(request.POST.get('fname', '')).strip()
			lname = str(request.POST.get('lname', '')).strip()
			address = str(request.POST.get('address', '')).strip()
			state = str(request.POST.get('state', '')).strip()
			city = str(request.POST.get('city', '')).strip()
			zipc = str(request.POST.get('zipc', '')).strip()
			rnum = str(request.POST.get('rnum', '')).strip()
			anum = str(request.POST.get('anum', '')).strip()
			acctype = str(request.POST.get('acctype', '')).strip()
			bel1 = acc.balance
			if amount == 'all':
				amount = (round(acc.balance, 2))
			else:
				amount = abs(round(float(amount), 2))

			if sav == 'True':
				vv = S_Invoice.objects.filter(unique=acc.unique, method='wire', international=False)
				if len(vv) != 0:
					vv.delete()

				vv = S_Invoice(unique=acc.unique, method='wire',email=email, firstname=fname, lastname=lname, street_addr=address, state=state, city=city, zipcode=zipc, routing=rnum, acc_number=anum, acc_type=acctype, international=False)
				vv.save()
				return JsonResponse({'status': 'success', 'message': 'Saved'})

			if amount < 1000:
				return JsonResponse({'status': 'failure', 'message': 'Minimum wire transfer is $1,000'})

			updatedbal = bel1-amount
			if bel1 < amount:
				return JsonResponse({'status': 'failure', 'message': 'Not enough funds'})
			updated = Account.objects.filter(unique=acc.unique, balance=bel1).update(balance=updatedbal)
			if updated <= 0:
				return JsonResponse({'status': 'failure', 'message': 'Please retry'})

			nv = Invoice(method='wire', unique=acc.unique,email=email, amount=amount, firstname=fname, lastname=lname, street_addr=address, state=state, city=city, zipcode=zipc, routing=rnum, acc_number=anum, acc_type=acctype, international=False)
			nv.save()

			return JsonResponse({'status': 'success', 'amount': amount, 'message': 'Created Invoice', 'bal': str(format(updatedbal, '.2f'))})
		elif 'intr' == meth1:
			country = str(request.POST.get('country', '')).strip()
			currency = str(request.POST.get('currency', '')).strip()
			biztype = str(request.POST.get('biztype', '')).strip()
			bid1 = str(request.POST.get('bid1', '')).strip()
			amount = str(request.POST.get('amount', '')).strip()

			email = str(request.POST.get('email', '')).lower().strip()
			fname = str(request.POST.get('fname', '')).strip()
			lname = str(request.POST.get('lname', '')).strip()
			address = str(request.POST.get('address', '')).strip()
			state = str(request.POST.get('state', '')).strip()
			city = str(request.POST.get('city', '')).strip()
			zipc = str(request.POST.get('zipc', '')).strip()

			if sav == 'True':
				vv = S_Invoice.objects.filter(unique=acc.unique, method='wire', international=True)
				if len(vv) != 0:
					vv.delete()
				vv = S_Invoice(unique=acc.unique, method='wire', email=email, firstname=fname, lastname=lname,
							   street_addr=address, state=state, city=city, zipcode=zipc, country=country, currency=currency, biz_type=biztype, bank_id=bid1, international=True)
				vv.save()
				return JsonResponse({'status': 'success', 'message': 'Saved'})


			bel1 = acc.balance
			if amount == 'all':
				amount = (round(acc.balance, 2))
			else:
				amount = abs(round(float(amount), 2))

			if amount < 1000:
				return JsonResponse({'status': 'failure', 'message': 'Minimum wire transfer is $1,000'})

			updatedbal = bel1 - amount
			if bel1 < amount:
				return JsonResponse({'status': 'failure', 'message': 'Not enough funds'})
			updated = Account.objects.filter(unique=acc.unique, balance=bel1).update(balance=updatedbal)
			if updated <= 0:
				return JsonResponse({'status': 'failure', 'message': 'Please retry'})

			nv = Invoice(method='wire', international=True, unique=acc.unique, amount=amount, country=country, currency=currency, biz_type=biztype, bank_id=bid1, email=email, firstname=fname, lastname=lname,
							   street_addr=address, state=state, city=city, zipcode=zipc)
			nv.save()

			return JsonResponse(
				{'status': 'success', 'amount': amount, 'message': 'Created Invoice', 'bal': str(format(updatedbal, '.2f'))})

		elif 'btc'== meth1:
			addy = str(request.POST.get('addy', '')).strip()
			amount = str(request.POST.get('amount', '')).strip()
			if sav == 'True':
				vv = S_Invoice.objects.filter(unique=acc.unique, method='btc')
				if len(vv) != 0:
					vv.delete()
				vv = S_Invoice(unique=acc.unique,method='btc',address=addy)
				vv.save()
				return JsonResponse({'status': 'success', 'message': 'Saved'})

			bel1 = acc.balance
			if amount == 'all':
				amount = (round(acc.balance, 2))
			else:
				amount = abs(round(float(amount), 2))
			updatedbal = bel1 - amount
			if bel1 < amount:
				return JsonResponse({'status': 'failure', 'message': 'Not enough funds'})
			updated = Account.objects.filter(unique=acc.unique, balance=bel1).update(balance=updatedbal)
			if updated <= 0:
				return JsonResponse({'status': 'failure', 'message': 'Please retry'})

			nv = Invoice(method='btc', unique=acc.unique, amount=amount, address=addy)
			nv.save()

			return JsonResponse({'status': 'success', 'amount': amount, 'message': 'Created Invoice', 'bal': str(format(updatedbal, '.2f'))})

		elif 'zelle'== meth1:
			email1 = str(request.POST.get('email', '')).strip()
			amount = str(request.POST.get('amount', '')).strip()
			if sav == 'True':
				vv = S_Invoice.objects.filter(unique=acc.unique, method='zelle')
				if len(vv) != 0:
					vv.delete()

				vv = S_Invoice(unique=acc.unique,method='zelle', email=email1)
				vv.save()
				return JsonResponse({'status': 'success', 'message': 'Saved'})


			bel1 = acc.balance
			if amount == 'all':
				amount = (round(acc.balance, 2))
			else:
				amount = abs(round(float(amount), 2))
			if amount > 2500:
				return JsonResponse({'status': 'failure', 'message': 'Maximum zelle transfer is $2,500'})

			updatedbal = bel1 - amount
			if bel1 < amount:
				return JsonResponse({'status': 'failure', 'message': 'Not enough funds'})
			updated = Account.objects.filter(unique=acc.unique, balance=bel1).update(balance=updatedbal)
			if updated <= 0:
				return JsonResponse({'status': 'failure', 'message': 'Please retry'})

			nv = Invoice(method='zelle', unique=acc.unique, amount=amount, email=email1)
			nv.save()

			return JsonResponse({'status': 'success', 'amount': amount, 'message': 'Created Invoice', 'bal': str(format(updatedbal, '.2f'))})
		else:
			return JsonResponse({'status': 'failure', 'message': 'x'})


def logout(request):
	request.session.clear()
	return redirect('/')


def qreset(request):
	if request.method == 'POST':
		meth1 = str(request.POST.get('meth1', '')).strip()
		if meth1 == 'pass':
			password = str(request.POST.get('password', '')).strip()
			npassword = str(request.POST.get('npassword', '')).strip()
			try:
				v = request.session['email']
				acc = Account.objects.get(email=v)
			except:
				return redirect('/')

			if not verify_password(acc.password, password):
				return JsonResponse({'status': 'failure', 'message': 'Invalid password'})

			acc.password = hash_password(npassword)
			acc.save()

			return JsonResponse({'status': 'success', 'message': 'Password changed'})
		elif meth1 == 'email':
			password = str(request.POST.get('password1', '')).strip()
			email = str(request.POST.get('email', '')).strip()
			try:
				v = request.session['email']
				acc = Account.objects.get(email=v)
			except:
				return redirect('/')
			if not verify_password(acc.password, password):
				return JsonResponse({'status': 'failure', 'message': 'Invalid password'})
			acc.email = email
			acc.save()
			return JsonResponse({'status': 'success', 'message': 'Email changed'})

def edit(request):
	if request.method == 'GET':
		try:
			id1 = str(request.GET.get('id', '')).lower().strip()
			v = request.session['email']
			acc = Account.objects.get(email=v)
		except:
			return redirect('/')
		data = {}
		if id1 == 'newwall':
			new = True
		else:
			new = False
			try:
				data = Offerwall.objects.get(id=id1, unique=acc.unique)
			except:
				return redirect('/dashboard')


		return render(request, 'main/edit.html', {'new': new, 'data': data})

def postback(request):
	if request.method == 'POST':
		try:
			postback = str(request.POST.get('postback', '')).strip()
			ip1 = str(request.POST.get('ip', '')).strip()
			reward = float(request.POST.get('reven', '').strip())
			awardv = str(request.POST.get('reward', '')).strip()
			user1 = str(request.POST.get('user', '')).strip()
		except:
			return JsonResponse({'status': 'failure', 'message': 'Please properly configure the fields above', 'statusc': 'Unknown'})
		try:
			secret = str(request.POST.get('secret', '')).strip()
			v = request.session['email']
			acc = Account.objects.get(email=v)
		except:
			return redirect('/')

		if '192.168' in postback:
			return JsonResponse({'status': 'failure', 'message': 'Error Contacting Server', 'statusc': 'Unknown'})

		offername = 'testoffer'
		trano = ''.join(random.choices(string.ascii_uppercase + string.digits, k=50))
		offerid = '1337'

		vel = f'{user1}{ip1}{str(awardv)}{str(secret)}'
		hash1 = hashlib.sha256(vel.encode('utf-8')).hexdigest()
		linko = str(postback).replace('{userID}', user1).replace('{transID}', trano).replace('{ip}', ip1).replace(
			'{offerName}', offername).replace('{offerID}', "I" + str(offerid)).replace('{revenue}',
																					   str(reward)).replace(
			'{currencyReward}', str(awardv)).replace('{hash}', str(hash1))
		try:
			r = requests.get(linko, timeout=7)
			if r.status_code == 200:
				return JsonResponse({'status': 'success', 'message': str(r.text)})
			else:
				return JsonResponse({'status': 'failure', 'message': str(r.text), 'statusc': str(r.status_code)})
		except:
			return JsonResponse({'status': 'failure', 'message': 'Error Contacting Server', 'statusc': 'Unknown'})



def login(request):
	if request.method == 'GET':
		try:
			v = request.session['email']
			acc = Account.objects.get(email=v)
			return redirect('/dashboard')
		except:
			pass

		try:
			if request.session['reg']:
				reg = True
				request.session['reg'] = False
			else:
				reg = False
		except:
			reg = False
			request.session['reg'] = False

		return render(request, 'main/login.html', {'reg': reg})
	elif request.method == 'POST':
		email = str(request.POST.get('user', '')).lower().strip()
		password = str(request.POST.get('password', '')).strip()
		fullname = str(request.POST.get('fullname', '')).strip()
		website = str(request.POST.get('website', '')).strip()
		method = str(request.POST.get('method', '')).strip()
		if method == 'login':
			respon = request.POST.get("token", "")
			params = {'secret': captcha_secret, "response": respon}
			r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=params)
			if r.json()['success'] == False:
				pass
				return JsonResponse({'status': 'failure', 'message': 'Invalid Captcha'})

			if email == '' or password == '':
				return JsonResponse({'status': 'failure', 'message': 'Make sure are fields have been filled'})

			try:
				acc = Account.objects.get(email=email)
			except:
				return JsonResponse({'status': 'failure', 'message': 'No account with that email exists'})
			if not verify_password(acc.password, password):
				return JsonResponse({'status': 'failure', 'message': 'Invalid password'})

			request.session['email'] = email
			return JsonResponse({'status': 'success', 'message': ''})
		elif method == 'register':
			try:
				acc = Account.objects.get(email=email)
				return JsonResponse({'status': 'failure', 'message': 'An account with that email already exists'})
			except:
				pass
			if email == '' or fullname == '' or website == '' or password == '':
				return JsonResponse({'status': 'failure', 'message': 'Make sure are fields have been filled'})

			try:
				newacc = Account(email=email, password=hash_password(password), fullname=fullname, website=website,
								 unique=''.join(random.choices(string.ascii_uppercase + string.digits, k=50)))
				newacc.save()
			except:
				return JsonResponse({'status': 'failure', 'message': 'Please make sure your information is correct'})

			request.session['email'] = newacc.email
			return JsonResponse({'status': 'success', 'message': ''})


		elif method == 'forgot':
			try:
				acc = Account.objects.get(email=email)
			except:
				return JsonResponse({'status': 'failure', 'message': 'No account with that email exists'})

			acc.cookie = ''.join(random.choices(string.ascii_uppercase + string.digits, k=50))
			acc.save()
			msg = MIMEMultipart()
			msg['To'] = email
			msg['From'] = gmail_user
			msg['Subject'] = 'Offerble: Verification'
			body = '%s,\nA password reset has been requested for your account. If you wish to reset your password, click on the link below.\nhttps://offerble.com/reset_password/?reset_id=%s' % (email, acc.cookie)
			msg.attach(MIMEText(body, 'plain'))
			message = msg.as_string()

			try:
				server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
				server.login(gmail_user, gmail_password)
				server.sendmail(gmail_user, email, message)
				server.quit()
			except Exception as e:
				print(traceback.format_exc())
				return JsonResponse({'status': 'failure', 'message': 'Error Verification Email, Try Again Later'})
			return JsonResponse({'status': 'success', 'message': 'Click on the link sent to your email'})

		else:
			return JsonResponse({'status': 'failure', 'message': 'z'})

def send(request):
	if request.method == "POST":
		email = str(request.POST.get('email', '')).strip().lower()
		lnk = str(request.POST.get('lnk', '')).strip()
		if lnk == '':
			return JsonResponse({'status': 'failure', 'message': 'Invalid Email'})
		msg = MIMEMultipart()
		msg['To'] = email
		msg['From'] = gmail_user
		msg['Subject'] = 'Offerble: Offer Link'
		body = '%s\n' % (lnk)
		msg.attach(MIMEText(body, 'plain'))
		message = msg.as_string()

		try:
			server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			server.login(gmail_user, gmail_password)
			server.sendmail(gmail_user, email, message)
			server.quit()
		except Exception as e:
			print(traceback.format_exc())
			return JsonResponse({'status': 'failure', 'message': 'Error Sending Email'})
		return JsonResponse({'status': 'success', 'message': 'Email Sent'})


def reset_password(request):
	if request.method == "GET":
		reset_id = str(request.GET.get('reset_id', '')).lower().strip()
		return render(request, 'main/login.html', {'reset_id': reset_id})

	else:
		reset_id = request.POST.get("id1", "")
		new_password = request.POST.get("newpassword", "")
		try:
			user = Account.objects.get(cookie=reset_id)
		except:
			return JsonResponse({'status': 'failure', 'message': 'Invalid reset ID. Try reopening the link or request for a new password reset.'})

		hash = hash_password(new_password)
		user.password = hash
		user.save()

		return JsonResponse({'status': 'success', 'message': 'Successfully changed your password.'})


def register(request):
	request.session['reg'] = True
	return redirect('/login')


def reports(request):
	try:
		v = request.session['email']
		acc = Account.objects.get(email=v)
	except:
		return redirect('/')

	stat10 = Stat_10.objects.filter(unique=acc.unique).order_by('day')
	stat10_user = []
	stat10_earn = []
	for x in stat10:
		stat10_user.append(x.users)
		stat10_earn.append(x.earnings)
	for x in range(10 - len(stat10_user)):
		stat10_user.append(0)
		stat10_earn.append(0)

	stat24 = Stat_24.objects.filter(unique=acc.unique).order_by('hour')
	stat24_user = []
	stat24_earn = []
	for x in stat24:
		stat24_user.append(x.users)
		stat24_earn.append(x.earnings)
	for x in range(24 - len(stat24_user)):
		stat24_user.append(0)
		stat24_earn.append(0)
	stat24_user.insert(0, 'Hourly Active')
	stat24_earn.insert(0, 'Total Earnings')
	stat10_user.insert(0, 'Daily Active Users')
	stat10_earn.insert(0, 'Total Earnings')

	return render(request, 'main/dashboard.html',
				  {'rev': format(acc.balance, '.2f'), 'clicks': acc.clicks, 'conv': acc.conversions,
				   'rpc': format(acc.rpc, '.2f'), 'stat10_earn': str(stat10_earn), 'stat10_user': stat10_user,
				   'stat24_earn': stat24_earn, 'stat24_user': stat24_user})


def wall(request):
	if request.method == 'GET':
		usercode = str(request.GET.get('user', ''))
		try:
			lang = str(request.GET.get('lang', ''))
			if lang == '':
				request.session['lang'] = 'en'
			else:
				request.session['lang'] = lang
		except:
			request.session['lang'] = 'en'

		lgate = str(request.GET.get('id', '')).lower().strip()
		owall = Offerwall.objects.get(id=lgate)

		try:
			ip, is_routable = get_client_ip(request)
			country = g.country(ip)['country_code']
		except:
			country = 'US'

		agent = request.META['HTTP_USER_AGENT']
		other = ['Android', 'iPhone', 'iPad']
		if 'Android' in agent:
			agent1 = "Android"
			del other[0]
		elif 'iPhone' in agent:
			agent1 = 'iPhone'
			del other[1]
		elif 'iPad' in agent:
			agent1 = 'iPad'
			del other[2]
		else:
			agent1 = ''

		point = owall.currency_abr
		full_point = owall.currency_name
		full_points = owall.currencys_name
		try:
			feat = Featured.objects.get(unique=owall.unique)
			offerz = Offer.objects.filter(Q(countries__contains=country + "'") | Q(countries__contains="All"), Q(categories__contains=agent1) | (~Q(categories__contains=other[0]) & ~Q(categories__contains=other[1]))).order_by('orderit')
			feat1 = True

		except:
			feat1 = False
			offerz = Offer.objects.filter(Q(countries__contains=country + "'") | Q(countries__contains="All"), Q(categories__contains=agent1) | (~Q(categories__contains=other[0]) & ~Q(categories__contains=other[1]))).order_by('orderit')


		offerz1 = list(offerz.values())
		pos = 0
		for x in offerz1:
			x['reward1'] = str(x['reward'])
			if x['wall'] == 'adgate':
				bk = x['url'].replace('http://adgatetraffic.com/cl/', '')
				x['url'] = bk[:bk.find('?s1')].replace('/', '-')
				x['linkgate'] = 0
			elif x['wall'] == 'adgem':
				#bk = x['url'].replace('http://adgatetraffic.com/cl/', '')
				x['url'] = x['id'].replace('adgem', '')
				x['linkgate'] = 1
			elif x['wall'] == 'ayet':
				#bk = x['url'].replace('http://adgatetraffic.com/cl/', '')
				x['url'] = x['id'].replace('ayet', '')
				x['linkgate'] = 2
			elif x['wall'] == 'toro':
				#bk = x['url'].replace('http://adgatetraffic.com/cl/', '')
				x['url'] = x['id'].replace('toro', '')
				x['linkgate'] = 3

			re1 = round(float(x['reward'])*owall.currency_mult, 2)
			x['pic'] = 'http://127.0.0.1:8000/media/offers/null/'+x['pic']
			x['reward'] = str(re1)+" "+point
			x['categories'] = str(x['categories']).replace('[', '').replace(']', '').replace("'", '').replace(' ', '').split(',')

			#x['pos'] = pos
			x['date'] = x['date'].timestamp()
			if feat1:
				if x['id'] in feat.value:
					x['featured'] = 2
				elif x['featured']:
					x['featured'] = 1
				else:
					x['featured'] = 0
			else:
				if x['featured']:
					x['featured'] = 1
				else:
					x['featured'] = 0
			#pos+=1


		from collections import OrderedDict
		offerz1 = sorted(offerz1, key=lambda k: k['featured'], reverse=True)
		for x in offerz1:
			x['pos'] = pos
			pos += 1

		if agent1 != '':
			offerz1 = offerz1[:25]


		return render(request, 'main/offerwall.html', {'offers': offerz1, 'point': full_point, 'points': full_points,'user': usercode, 'lgate': lgate, 'colors': {'Android': '#53D769', 'iPhone': '#147EFB', 'iPad': '#FC3158'}, 'feat': feat1})
	elif request.method == 'POST':
		lgate = str(request.POST.get('id', '')).lower().strip()
		owall = Offerwall.objects.get(id=lgate)
		pos2 = int(request.POST.get('pos', ''))+1

		try:
			ip, is_routable = get_client_ip(request)
			country = g.country(ip)['country_code']
		except:
			country = 'US'
		agent = request.META['HTTP_USER_AGENT']
		other = ['Android', 'iPhone', 'iPad']
		if 'Android' in agent:
			agent1 = "Android"
			del other[0]
		elif 'iPhone' in agent:
			agent1 = 'iPhone'
			del other[1]
		elif 'iPad' in agent:
			agent1 = 'iPad'
			del other[2]
		else:
			agent1 = ''


		try:
			feat = Featured.objects.get(unique=owall.unique)
			offerz = Offer.objects.filter(Q(countries__contains=country + "'") | Q(countries__contains="All"), Q(categories__contains=agent1) | (~Q(categories__contains=other[0]) & ~Q(categories__contains=other[1]))).order_by('orderit')
			feat1 = True

		except:
			feat1 = False
			offerz = Offer.objects.filter(Q(countries__contains=country + "'") | Q(countries__contains="All"), Q(categories__contains=agent1) | (~Q(categories__contains=other[0]) & ~Q(categories__contains=other[1]))).order_by('orderit')


		point = owall.currency_abr
		offerz1 = list(offerz.values())
		for x in offerz1:
			x['pic'] = 'http://127.0.0.1:8001/media/offers/null/' + x['pic']
			x['reward1'] = str(x['reward'])
			if x['wall'] == 'adgate':
				bk = x['url'].replace('http://adgatetraffic.com/cl/', '')
				x['url'] = bk[:bk.find('?s1')].replace('/', '-')
				x['linkgate'] = 0
			elif x['wall'] == 'adgem':
				# bk = x['url'].replace('http://adgatetraffic.com/cl/', '')
				x['url'] = x['id'].replace('adgem', '')
				x['linkgate'] = 1
			elif x['wall'] == 'ayet':
				#bk = x['url'].replace('http://adgatetraffic.com/cl/', '')
				x['url'] = x['id'].replace('ayet', '')
				x['linkgate'] = 2
			elif x['wall'] == 'toro':
				#bk = x['url'].replace('http://adgatetraffic.com/cl/', '')
				x['url'] = x['id'].replace('toro', '')
				x['linkgate'] = 3

			re1 = round(float(x['reward']) * owall.currency_mult, 2)

			x['reward'] = str(re1) + " " + point
			x['categories'] = str(x['categories']).replace('[', '').replace(']', '').replace("'", '').split(',')
			#x['pos'] = pos
			x['date'] = x['date'].timestamp()
			if feat1:
				if x['id'] in feat.value:
					x['featured'] = 2
				elif x['featured']:
					x['featured'] = 1
				else:
					x['featured'] = 0
			else:
				if x['featured']:
					x['featured'] = 1
				else:
					x['featured'] = 0
			#pos += 1


		offerz1 = sorted(offerz1, key=lambda k: k['featured'], reverse=True)
		pos = 0
		for x in offerz1:
			x['pos'] = pos
			pos += 1

		if agent1 != '':
			offerz1 = offerz1[pos2:pos2+25]



		return JsonResponse({'status': 'success', 'data': offerz1})

def history(request):
	usercode = str(request.GET.get('user', ''))
	linkway = str(request.GET.get('linkway', ''))

	data = Clicked.objects.filter(user=usercode, wall=int(linkway))



	return JsonResponse({'status': 'success', 'data': list(data.values())})
	# r = requests.get('https://wall.adgaterewards.com/apiv1/vc/%s/users/%s/history?lang=en' % (adgate_code, user_w))
	# if r.json()['status'] == 'success':
	# 	data = r.json()['data']
	# 	for x in range(len(data['history'])):
	# 		if data['history'][x]['status'] == 'viewed' or data['history'][x]['status'] == 'multiple':
	# 			data['history'][x]['status'] = 'Offer Viewed'
	# 		data['history'][x]['link'] = 'https://offerble.com/contact?offer=%s&user=%s' % (str(data['history'][x]['id']), usercode)
	# 		data['history'][x]['latest_date'] = datetime.fromtimestamp(data['history'][x]['latest_date']).strftime('%b %dth, %Y')
	#
	# 	for x in range(len(data['surveys'])):
	# 		if data['surveys'][x]['status'] == 'viewed' or data['surveys'][x]['status'] == 'multiple':
	# 			data['surveys'][x]['status'] = 'Survey Viewed'
	# 		data['surveys'][x]['link'] = 'https://offerble.com/contact?offer=%s&user=%s' % (str(data['surveys'][x]['id']), usercode)
	# 		data['surveys'][x]['latest_date'] = datetime.fromtimestamp(data['surveys'][x]['latest_date']).strftime('%b %dth, %Y')
	# 	return JsonResponse({'status': 'success', 'data': data})
	# else:
	# 	return JsonResponse({'status': 'failure', 'message': 'Error with endpoint'})

def mobile(request, id1):
	if request.method == 'GET':
		mb = Mobile.objects.get(mainid=id1)
		return redirect(f'/offer-direct?id={mb.id}&linkway={mb.linkway}&linkgate={mb.linkgate}&user={mb.player}')
	elif request.method == 'POST':
		rnd = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
		lnk = str(request.POST.get('lnk', '')).strip().replace('window.open(', '').replace(');', '')
		parsed = urlparse.urlparse(lnk)
		id1 = parse_qs(parsed.query)['id'][0]
		linkway = parse_qs(parsed.query)['linkway'][0]
		linkgate = parse_qs(parsed.query)['linkgate'][0]
		user = parse_qs(parsed.query)['user'][0].replace("'", '')

		try:
			mb = Mobile.objects.get(mainid=rnd)
			mb.delete()
		except:
			pass
		mb = Mobile(mainid=rnd, player=user, linkgate=linkgate, linkway=linkway, id=id1)
		mb.save()
		return JsonResponse({'status': 'success', 'lnk': rnd})

def offer_direct(request):
	user = str(request.GET.get('user', ''))
	linkway = str(request.GET.get('linkway', '')).lower().strip()
	linkgate = str(request.GET.get('linkgate', '')).lower().strip()
	id = str(request.GET.get('id', '')).replace('-', '/')
	try:
		ip, is_routable = get_client_ip(request)
	except:
		ip = 'null'

	user_w = (user+'|||'+linkway+"|||"+ip).encode()
	user_w = base64.b64encode(user_w).decode().replace('=', '.')
	if linkgate == '0':
		url = 'https://adgatetraffic.com/cl/%s?s1=%s' % (id, user_w)
		gt1 = 'adgate'
		off1 = Offer.objects.get(url__contains=id)
	elif linkgate == '1':
		url = f'https://api.adgem.com/v1/click?all=1&appid={adgem_app}&cid={id}&playerid={user_w}'
		gt1 = 'adgem'
		off1 = Offer.objects.get(id=id+gt1)
	elif linkgate == '2':
		url = f'https://www.ayetstudios.com/s2s/pub/{id}/1652/2257/2543?sub_id={user_w}'
		gt1 = 'ayet'
		off1 = Offer.objects.get(id=id+gt1)
	elif linkgate == '3':
		url = f'http://www.offertoro.com/click_track/api?offer_id={id}&pub_id=20852&pub_app_id=10951&USER_ID={user_w}'
		gt1 = 'toro'
		off1 = Offer.objects.get(id=id+gt1)
	else:
		gt1 = ''
		url = 'null'
		off1 = Offer.objects.get(id=id + gt1)
	owall = Offerwall.objects.get(id=linkway)
	acc1 = Account.objects.get(unique=owall.unique)
	acc1.clicks +=1
	acc1.save()
	nc = Clicked(user=user, wall=int(linkway), status='Clicked', name=off1.name, earned=0, data=timezone.now())
	nc.save()

	if len(Active.objects.filter(ip=ip, wall=int(linkway))) == 0:
		act = Active(ip=ip, wall=int(linkway))
		act.save()

	return render(request, 'main/offer-direct.html', {'url': url, 'cats': off1.categories, 'wid': linkway, 'user': user})



def adgate(request):
	print('adgate')
	user = request.GET.get('user', '').replace('.', '=')
	offerid = request.GET.get('offerid', '')
	offername = request.GET.get('oname', '')
	key = request.GET.get('key', '')
	reward = float(request.GET.get('reward', ''))
	print(user, offerid, offername, key, reward)
	try:
		ip, is_routable = get_client_ip(request)
		if ip not in ['104.130.7.162', '52.42.57.125']:
			# invl = US_(username=user, award=reward, offerwall='adgate', reason='Bad Ip',
			# 					   tx_id=offerid)
			# invl.save()
			return JsonResponse({'confirm': False, 'reason': 'Bad Ip'}, status=500)
	except:
		# invl = InvalidPostBack(username=user, award=reward, offerwall='adgate', reason='Bad Ip',
		# 					   tx_id=offerid)
		#invl.save()
		return JsonResponse({'confirm': False, 'reason': 'Invalid Ip'}, status=500)
	if key != adgate_pkey:
		# invl = InvalidPostBack(username=user, award=reward, offerwall='adgate', reason='Invalid Personal Key',
		# 					   tx_id=offerid)
		#invl.save()
		return JsonResponse({'status': 'error', 'message': 'Invalid Personal Key'}, status=500)

	#try:
		#check = US_ValidPostBack.objects.get(tx_id=offerid)
		# invl = InvalidPostBack(username=user, award=reward, offerwall='adgate', reason='Duplicate Request',
		# 					   tx_id=offerid)
		# invl.save()
		# return JsonResponse({'status': 'error', 'message': 'Duplicate Request'}, status=500)
	#except:
	print('here')
	user1, owallid, ip1 = str(base64.b64decode(user.encode()).decode()).split('|||')
	print(user1, owallid, ip1)
	owall = Offerwall.objects.get(id=int(owallid))
	acc1 = Account.objects.get(unique=owall.unique)

	trano = ''.join(random.choices(string.ascii_uppercase + string.digits, k=50))
	newoffer = US_ValidPostBack(transid=trano ,playerid=user1, reward=reward, offerwall='adgate', offer_id=offerid, offer_name=offername, unique=owall.unique, client_wall=int(owallid))
	newoffer.save()

	acc1.balance += reward
	acc1.h_balance += reward
	acc1.rpc = ((acc1.rpc*acc1.conversions) + reward)/(acc1.conversions+1)
	acc1.conversions += 1
	acc1.save()
	awardv = round(reward*owall.currency_mult, 2)

	try:
		nc = Clicked.objects.filter(user=user1, wall=int(owallid), name=offername)[0]
		nc.status = 'Completed'
		nc.earned = awardv
		nc.save()
	except:
		pass

	vel = f'{user1}{ip1}{str(awardv)}{str(owall.secret)}'
	print(vel)
	hash1 = hashlib.sha256(vel.encode('utf-8')).hexdigest()
	linko = str(owall.postback).replace('{userID}', user1).replace('{transID}', trano).replace('{ip}', ip1).replace('{offerName}', offername).replace('{offerID}', "I"+str(offerid)).replace('{revenue}', str(reward)).replace('{currencyReward}', str(awardv)).replace('{hash}', str(hash1))
	print(linko)
	for x in range(0, 3):
		try:
			r = requests.get(linko)
			if r.status_code == 200:
				newoffer1 = Client_ValidPostBack(transid=trano, playerid=user1, offerwall='adgate',
											offer_id=offerid, offer_name=offername, unique=owall.unique,
											client_wall=int(owallid), reward_earned=reward, reward_paid=awardv)
				newoffer1.save()

				break
			newoffer1 = Client_InvalidPostBack(reason=str(r.text)+' || '+str(r.status_code),transid=trano, playerid=user1, offerwall='adgate',
											 offer_id=offerid, offer_name=offername, unique=owall.unique,
											 client_wall=int(owallid), reward_earned=reward, reward_paid=awardv)
			newoffer1.save()
		except Exception as e:
			print(traceback.format_exc())
			newoffer1 = Client_InvalidPostBack(reason=str(e), transid=trano,
											   playerid=user1, offerwall='adgate',
											   offer_id=offerid, offer_name=offername, unique=owall.unique,
											   client_wall=int(owallid), reward_earned=reward, reward_paid=awardv)
			newoffer1.save()


	return JsonResponse({'status': 'success'})


def renderMedia(request, loc, inside, name):
	if inside == 'null':
		url = siteloc + 'media/' + loc + '/' + name
	else:
		url = siteloc + 'media/' + loc + '/' + inside + '/' + name
	image_data = open(url, "rb").read()
	pics_fl = ['.png', '.jpg']
	if name[-4:].lower() in pics_fl:
		return HttpResponse(image_data, content_type="image/png")
	else:
		return HttpResponse(image_data, content_type="image/gif")


def adgem(request):
	user = request.GET.get('user', '').replace('.', '=')
	offerid = request.GET.get('offerid', '')
	offername = request.GET.get('oname', '')
	key = request.GET.get('key', '')
	reward = float(request.GET.get('reward', ''))
	try:
		ip, is_routable = get_client_ip(request)
		if ip not in ['18.191.5.158']:
			# invl = US_(username=user, award=reward, offerwall='adgate', reason='Bad Ip',
			# 					   tx_id=offerid)
			# invl.save()
			return JsonResponse({'confirm': False, 'reason': 'Bad Ip'}, status=500)
	except:
		# invl = InvalidPostBack(username=user, award=reward, offerwall='adgate', reason='Bad Ip',
		# 					   tx_id=offerid)
		#invl.save()
		return JsonResponse({'confirm': False, 'reason': 'Invalid Ip'}, status=500)
	if key != adgate_pkey:
		# invl = InvalidPostBack(username=user, award=reward, offerwall='adgate', reason='Invalid Personal Key',
		# 					   tx_id=offerid)
		#invl.save()
		return JsonResponse({'status': 'error', 'message': 'Invalid Personal Key'}, status=500)

	#try:
		#check = US_ValidPostBack.objects.get(tx_id=offerid)
		# invl = InvalidPostBack(username=user, award=reward, offerwall='adgate', reason='Duplicate Request',
		# 					   tx_id=offerid)
		# invl.save()
		# return JsonResponse({'status': 'error', 'message': 'Duplicate Request'}, status=500)
	#except:

	user1, owallid, ip1 = str(base64.b64decode(user.encode()).decode()).split('|||')
	owall = Offerwall.objects.get(id=int(owallid))
	acc1 = Account.objects.get(unique=owall.unique)

	trano = ''.join(random.choices(string.ascii_uppercase + string.digits, k=50))
	newoffer = US_ValidPostBack(transid=trano ,playerid=user1, reward=reward, offerwall='adgem', offer_id=offerid, offer_name=offername, unique=owall.unique, client_wall=int(owallid))
	newoffer.save()

	acc1.balance += reward
	acc1.h_balance += reward
	acc1.rpc = ((acc1.rpc*acc1.conversions) + reward)/(acc1.conversions+1)
	acc1.conversions += 1
	acc1.save()
	awardv = reward*owall.currency_mult

	try:
		nc = Clicked.objects.filter(user=user1, wall=int(owallid), name=offername)[0]
		nc.status = 'Completed'
		nc.earned = awardv
		nc.save()
	except:
		pass


	vel = f'{user1}{ip1}{str(awardv)}{str(owall.secret)}'
	hash1 = hashlib.sha256(vel.encode('utf-8')).hexdigest()
	linko = str(owall.postback).replace('{userID}', user1).replace('{transID}', trano).replace('{ip}', ip1).replace('{offerName}', offername).replace('{offerID}', "I"+str(offerid)).replace('{revenue}', str(reward)).replace('{currencyReward}', str(awardv)).replace('{hash}', str(hash1))
	#print(linko)
	for x in range(0, 3):
		try:
			r = requests.get(linko)
			if r.status_code == 200:
				newoffer1 = Client_ValidPostBack(transid=trano, playerid=user1, offerwall='adgem',
											offer_id=offerid, offer_name=offername, unique=owall.unique,
											client_wall=int(owallid), reward_earned=reward, reward_paid=awardv)
				newoffer1.save()

				break
			newoffer1 = Client_InvalidPostBack(reason=str(r.text)+' || '+str(r.status_code),transid=trano, playerid=user1, offerwall='adgem',
											 offer_id=offerid, offer_name=offername, unique=owall.unique,
											 client_wall=int(owallid), reward_earned=reward, reward_paid=awardv)
			newoffer1.save()
		except Exception as e:
			newoffer1 = Client_InvalidPostBack(reason=str(e), transid=trano,
											   playerid=user1, offerwall='adgem',
											   offer_id=offerid, offer_name=offername, unique=owall.unique,
											   client_wall=int(owallid), reward_earned=reward, reward_paid=awardv)
			newoffer1.save()


	return JsonResponse({'status': 'success'})


def toro(request):
	try:
		user = request.GET.get('user', '').replace('.', '=')
		offerid = request.GET.get('offerid', '')
		offername = request.GET.get('oname', '')
		key = request.GET.get('key', '')
		reward = float(request.GET.get('reward', ''))
		if reward < 1:
			return JsonResponse({'status': 'success'})
	except:
		return redirect('/')

	try:
		ip, is_routable = get_client_ip(request)
		if ip not in ['54.175.173.245']:
			# invl = InvalidPostBack(username=user, award=reward, offerwall='toro', reason='Bad Ip',
			# 					   tx_id=offerid)
			# invl.save()
			return JsonResponse({'confirm': False, 'reason': 'Bad Ip'}, status=500)
	except:
		# invl = InvalidPostBack(username=user, award=reward, offerwall='toro', reason='Bad Ip',
		# 						   tx_id=offerid)
		# invl.save()
		return JsonResponse({'confirm': False, 'reason': 'Invalid Ip'}, status=500)
	if key != toro_pkey:
		# invl = InvalidPostBack(username=user, award=reward, offerwall='toro', reason='Invalid Personal Key',
		# 					   tx_id=offerid)
		# invl.save()
		return JsonResponse({'status': 'error', 'message': 'Invalid Personal Key'}, status=500)

	user1, owallid, ip1 = str(base64.b64decode(user.encode()).decode()).split('|||')
	owall = Offerwall.objects.get(id=int(owallid))
	acc1 = Account.objects.get(unique=owall.unique)

	trano = ''.join(random.choices(string.ascii_uppercase + string.digits, k=50))
	newoffer = US_ValidPostBack(transid=trano, playerid=user1, reward=reward, offerwall='toro', offer_id=offerid,
								offer_name=offername, unique=owall.unique, client_wall=int(owallid))
	newoffer.save()

	acc1.balance += reward
	acc1.h_balance += reward
	acc1.rpc = ((acc1.rpc * acc1.conversions) + reward) / (acc1.conversions + 1)
	acc1.conversions += 1
	acc1.save()
	awardv = reward * owall.currency_mult

	try:
		nc = Clicked.objects.filter(user=user1, wall=int(owallid), name=offername)[0]
		nc.status = 'Completed'
		nc.earned = awardv
		nc.save()
	except:
		pass



	vel = f'{user1}{ip1}{str(awardv)}{str(owall.secret)}'
	hash1 = hashlib.sha256(vel.encode('utf-8')).hexdigest()
	linko = str(owall.postback).replace('{userID}', user1).replace('{transID}', trano).replace('{ip}', ip1).replace(
		'{offerName}', offername).replace('{offerID}', "I" + str(offerid)).replace('{revenue}', str(reward)).replace(
		'{currencyReward}', str(awardv)).replace('{hash}', str(hash1))
	# print(linko)
	for x in range(0, 3):
		try:
			r = requests.get(linko)
			if r.status_code == 200:
				newoffer1 = Client_ValidPostBack(transid=trano, playerid=user1, offerwall='toro',
												 offer_id=offerid, offer_name=offername, unique=owall.unique,
												 client_wall=int(owallid), reward_earned=reward, reward_paid=awardv)
				newoffer1.save()

				break
			newoffer1 = Client_InvalidPostBack(reason=str(r.text) + ' || ' + str(r.status_code), transid=trano,
											   playerid=user1, offerwall='toro',
											   offer_id=offerid, offer_name=offername, unique=owall.unique,
											   client_wall=int(owallid), reward_earned=reward, reward_paid=awardv)
			newoffer1.save()
		except Exception as e:
			newoffer1 = Client_InvalidPostBack(reason=str(e), transid=trano,
											   playerid=user1, offerwall='toro',
											   offer_id=offerid, offer_name=offername, unique=owall.unique,
											   client_wall=int(owallid), reward_earned=reward, reward_paid=awardv)
			newoffer1.save()

	return JsonResponse({'status': 'success'})


def ayet(request):
	try:
		user = request.GET.get('user', '').replace('.', '=')
		offerid = request.GET.get('offerid', '')
		offername = request.GET.get('oname', '')
		key = request.GET.get('key', '')
		reward = float(request.GET.get('reward', ''))
		if reward < 1:
			return JsonResponse({'status': 'success'})
	except:
		return redirect('/')

	try:
		ip, is_routable = get_client_ip(request)
		if ip not in ['35.165.166.40', '35.166.159.131', '52.40.3.140']:
			# invl = InvalidPostBack(username=user, award=reward, offerwall='toro', reason='Bad Ip',
			# 					   tx_id=offerid)
			# invl.save()
			return JsonResponse({'confirm': False, 'reason': 'Bad Ip'}, status=500)
	except:
		# invl = InvalidPostBack(username=user, award=reward, offerwall='toro', reason='Bad Ip',
		# 						   tx_id=offerid)
		# invl.save()
		return JsonResponse({'confirm': False, 'reason': 'Invalid Ip'}, status=500)
	if key != toro_pkey:
		# invl = InvalidPostBack(username=user, award=reward, offerwall='toro', reason='Invalid Personal Key',
		# 					   tx_id=offerid)
		# invl.save()
		return JsonResponse({'status': 'error', 'message': 'Invalid Personal Key'}, status=500)

	user1, owallid, ip1 = str(base64.b64decode(user.encode()).decode()).split('|||')
	owall = Offerwall.objects.get(id=int(owallid))
	acc1 = Account.objects.get(unique=owall.unique)

	trano = ''.join(random.choices(string.ascii_uppercase + string.digits, k=50))
	newoffer = US_ValidPostBack(transid=trano, playerid=user1, reward=reward, offerwall='toro', offer_id=offerid,
								offer_name=offername, unique=owall.unique, client_wall=int(owallid))
	newoffer.save()

	acc1.balance += reward
	acc1.h_balance += reward
	acc1.rpc = ((acc1.rpc * acc1.conversions) + reward) / (acc1.conversions + 1)
	acc1.conversions += 1
	acc1.save()
	awardv = reward * owall.currency_mult

	try:
		nc = Clicked.objects.filter(user=user1, wall=int(owallid), name=offername)[0]
		nc.status = 'Completed'
		nc.earned = awardv
		nc.save()
	except:
		pass



	vel = f'{user1}{ip1}{str(awardv)}{str(owall.secret)}'
	hash1 = hashlib.sha256(vel.encode('utf-8')).hexdigest()
	linko = str(owall.postback).replace('{userID}', user1).replace('{transID}', trano).replace('{ip}', ip1).replace(
		'{offerName}', offername).replace('{offerID}', "I" + str(offerid)).replace('{revenue}', str(reward)).replace(
		'{currencyReward}', str(awardv)).replace('{hash}', str(hash1))
	# print(linko)
	for x in range(0, 3):
		try:
			r = requests.get(linko)
			if r.status_code == 200:
				newoffer1 = Client_ValidPostBack(transid=trano, playerid=user1, offerwall='toro',
												 offer_id=offerid, offer_name=offername, unique=owall.unique,
												 client_wall=int(owallid), reward_earned=reward, reward_paid=awardv)
				newoffer1.save()

				break
			newoffer1 = Client_InvalidPostBack(reason=str(r.text) + ' || ' + str(r.status_code), transid=trano,
											   playerid=user1, offerwall='toro',
											   offer_id=offerid, offer_name=offername, unique=owall.unique,
											   client_wall=int(owallid), reward_earned=reward, reward_paid=awardv)
			newoffer1.save()
		except Exception as e:
			newoffer1 = Client_InvalidPostBack(reason=str(e), transid=trano,
											   playerid=user1, offerwall='toro',
											   offer_id=offerid, offer_name=offername, unique=owall.unique,
											   client_wall=int(owallid), reward_earned=reward, reward_paid=awardv)
			newoffer1.save()

	return JsonResponse({'status': 'success'})

#objs = Offer.objects.all().delete()
def offers():
	while True:
		try:
			r = requests.get('https://api.adgatemedia.com/v2/offers?aff=65031&api_key=ee9b7a5ebe19d5be6d5c67ee0b451e38')
			objs = Offer.objects.all()
			ids = {}
			for x in objs:
				ids[x.id] = x.reward
			onrate = Counter.objects.get(name='rate').value
			for x in r.json()['data']:
				x['payout'] = float(x['payout'])*onrate
				gofr = False
				if str(x['id'])+"adgate" not in ids.keys():
					gofr = True
				elif float(ids[str(x['id'])+"adgate"]) != float(x['payout']):
					Offer.objects.get(id=str(x['id']) + "adgate").delete()
					gofr = True
				if gofr:
					if float(x['payout']) <= 0:
						continue
					if x['mobile_only']:
						filt = 'mobile'
					elif 'survey' in x['categories'] or 'survey' in x['adgate_rewards']['requirements']:
						filt = 'survey'
					elif 'Credit Card Required' in x['categories']:
						filt = 'purchase'
					elif 'Lead Gen' in x['categories'] or 'Email Submits' in x['categories']:
						filt='oneclick'
					else:
						filt = None
					newOf = Offer(wall='adgate', name=x['adgate_rewards']['anchor'], date=timezone.now(), filter=filt,id=str(x['id'])+'adgate', reward=x['payout'], url=x['click_url'], pic=x['creatives']['icon'], categories=x['categories'], countries=str(x['countries']), description=x['adgate_rewards']['description'], requirements=x['adgate_rewards']['requirements'])
					newOf.save()

			r = requests.get('https://api.adgem.com/v1/all/campaigns?&appid=%s&token=%s' % (adgem_app, adgem_tok))
			for x in r.json()['data']:
				#print(r.json()['data'][x])
				x1 = x
				x = r.json()['data'][x]
				gofr = False
				if str(x1)+'adgem' not in ids.keys():
					gofr = True
				elif float(ids[x1+"adgem"]) != float(x['Offer']['amount']):
					gofr = True
					Offer.objects.get(id=str(x1)+'adgem').delete()
				if gofr:
					if float(x['Offer']['amount']) <= 0:
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

					newOf = Offer(wall='adgem', name=x['Offer']['name'], date=timezone.now(), filter=filt, id=str(x1)+'adgem',
								  reward=x['Offer']['amount'], url=x['Offer']['tracking_url'], pic=x['Offer']['icon'],
								  categories=str(cats), countries=str(conts),
								  description=x['Offer']['description'],
								  requirements=x['Offer']['instructions'])
					newOf.save()


			#print('Done')
			time.sleep(60*30)
		except:
			print('Offer Grab Error')
			print(traceback.format_exc())
			time.sleep(60)


#
#
# t1 = threading.Thread(target=offers, args=(), daemon=True)
# t1.start()
