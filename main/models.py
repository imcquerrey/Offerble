from django.db import models
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
import random
#offerimg = FileSystemStorage(location = '/var/www/mysite/media/offers/')
offerimg = FileSystemStorage(location = '/home/skinnypete/Websites/OfferWall/media/offers/')



def random_string():
	return int(random.randint(10000, 99999))


class Offer(models.Model):
	wall = models.CharField(max_length=300)
	name = models.CharField(max_length=300)
	id = models.CharField(max_length=100, primary_key=True)
	reward = models.FloatField()
	url = models.CharField(max_length=300)
	pic = models.FileField(storage=offerimg, blank=True, null=True, default='', max_length=500)
	#pic = models.FileField(upload_to='offers/%Y/%m', null=True)
	#pic = models.CharField(max_length=300)
	filter = models.CharField(max_length=300, blank=True, null=True)
	countries = models.CharField(max_length=3000)
	categories = models.CharField(max_length=3000)
	description = models.CharField(max_length=3000)
	requirements = models.CharField(max_length=3000)
	orderit = models.IntegerField(default=random_string)
	date=models.DateTimeField()
	featured = models.BooleanField(default=False)
	def __str__(self):
		return "%s | %s" % (self.name, self.reward)


class Featured(models.Model):
	unique = models.CharField(max_length=300, primary_key=True)
	value = models.CharField(max_length=15000)

class Counter(models.Model):
	name = models.CharField(max_length=300)
	value = models.FloatField(max_length=1000)
	def __str__(self):
		return "%s | %s" % (self.name, self.value)

class Active(models.Model):
	ip = models.CharField(max_length=300)
	wall = models.IntegerField()
	def __str__(self):
		return "%s | %s" % (self.ip, self.wall)

class Clicked(models.Model):
	user = models.CharField(max_length=300)
	status = models.CharField(max_length=300)
	wall = models.IntegerField()
	name = models.CharField(max_length=300)
	offerid = models.CharField(max_length=300)
	earned = models.FloatField()
	data = models.DateField()
	def __str__(self):
		return "%s | %s" % (self.user, self.status)


class Mobile(models.Model):
	player = models.CharField(max_length=300)
	linkgate = models.CharField(max_length=300)
	linkway = models.CharField(max_length=300)
	id = models.CharField(max_length=300)
	mainid = models.CharField(max_length=5, primary_key=True)

class Account(models.Model):
	email = models.CharField(max_length=250, primary_key=True)
	fullname = models.CharField(max_length=300)
	website = models.CharField(max_length=300)
	password = models.CharField(max_length=1000)
	unique = models.CharField(max_length=300)
	cookie = models.CharField(max_length=300, default='nope')
	balance = models.FloatField(default=0)
	h_balance = models.FloatField(default=0)
	clicks = models.IntegerField(default=0)
	conversions = models.IntegerField(default=0)
	rpc = models.FloatField(default=0)
	def __str__(self):
		return "%s | %s" % (self.email, self.balance)

class Invoice(models.Model):
	unique = models.CharField(max_length=300)
	status = models.CharField(max_length=300, default='Pending')
	method = models.CharField(max_length=300)
	address = models.CharField(max_length=300, blank=True, null=True)
	email = models.CharField(max_length=300, blank=True, null=True)
	amount = models.FloatField(default=0)
	international = models.BooleanField(blank=True, null=True)
	firstname = models.CharField(max_length=300, blank=True, null=True)
	lastname = models.CharField(max_length=300, blank=True, null=True)
	stree_addr = models.CharField(max_length=300, blank=True, null=True)
	state = models.CharField(max_length=300, blank=True, null=True)
	city = models.CharField(max_length=300, blank=True, null=True)
	zipcode = models.CharField(max_length=300, blank=True, null=True)
	currency = models.CharField(max_length=300, blank=True, null=True)
	routing = models.CharField(max_length=300, blank=True, null=True)
	acc_number = models.CharField(max_length=300, blank=True, null=True)
	acc_type = models.CharField(max_length=300, blank=True, null=True)
	country = models.CharField(max_length=300, blank=True, null=True)
	biz_type = models.CharField(max_length=300, blank=True, null=True)
	bank_id = models.CharField(max_length=300, blank=True, null=True)
	def __str__(self):
		return "%s | %s | %s | %s" % (self.email, self.method, self.amount,self.status)

class S_Invoice(models.Model):
	unique = models.CharField(max_length=300)
	method = models.CharField(max_length=300)
	address = models.CharField(max_length=300, blank=True, null=True)
	email = models.CharField(max_length=300, blank=True, null=True)
	international = models.BooleanField(blank=True, null=True)
	firstname = models.CharField(max_length=300, blank=True, null=True)
	lastname = models.CharField(max_length=300, blank=True, null=True)
	street_addr = models.CharField(max_length=300, blank=True, null=True)
	state = models.CharField(max_length=300, blank=True, null=True)
	city = models.CharField(max_length=300, blank=True, null=True)
	zipcode = models.CharField(max_length=300, blank=True, null=True)
	currency = models.CharField(max_length=300, blank=True, null=True)
	routing = models.CharField(max_length=300, blank=True, null=True)
	acc_number = models.CharField(max_length=300, blank=True, null=True)
	acc_type = models.CharField(max_length=300, blank=True, null=True)
	country = models.CharField(max_length=300, blank=True, null=True)
	biz_type = models.CharField(max_length=300, blank=True, null=True)
	bank_id = models.CharField(max_length=300, blank=True, null=True)
	def __str__(self):
		return "%s | %s" % (self.email, self.method)

class Stat_24(models.Model):
	unique = models.CharField(max_length=300)
	hour = models.IntegerField(default=0)
	users = models.IntegerField(default=0)
	earnings = models.FloatField(default=0)

	def __str__(self):
		return "%s | %s | %s" % (self.hour, self.users, self.earnings)


class Stat_10(models.Model):
	unique = models.CharField(max_length=300)
	day = models.IntegerField(default=0)
	users = models.IntegerField(default=0)
	earnings = models.FloatField(default=0)
	def __str__(self):
		return "%s | %s | %s" % (self.day, self.users, self.earnings)

class Offerwall(models.Model):
	unique = models.CharField(max_length=300)
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	created = models.DateField(default=timezone.now)
	postback = models.CharField(max_length=400)
	secret = models.CharField(max_length=35, unique=True)
	currency_name = models.CharField(max_length=30)
	currencys_name = models.CharField(max_length=30)
	currency_abr = models.CharField(max_length=30)
	currency_mult = models.FloatField(default=0)
	def __str__(self):
		return "%s | %s" % (self.name, self.id)

class US_ValidPostBack(models.Model):
	offerwall = models.CharField(max_length=300)
	unique = models.CharField(max_length=300)
	playerid = models.CharField(max_length=300)
	client_wall = models.IntegerField()
	reward = models.FloatField()
	offer_name = models.CharField(max_length=300)
	offer_id = models.CharField(max_length=300)
	transid = models.CharField(max_length=50)
	def __str__(self):
		return "%s | Earned: $%s" % (self.client_wall, self.reward)


class Client_ValidPostBack(models.Model):
	offerwall = models.CharField(max_length=300)
	unique = models.CharField(max_length=300)
	playerid = models.CharField(max_length=300)
	client_wall = models.IntegerField()
	reward_earned = models.FloatField()
	reward_paid = models.FloatField()
	offer_name = models.CharField(max_length=300)
	offer_id = models.CharField(max_length=300)
	transid = models.CharField(max_length=50)
	def __str__(self):
		return "%s | Earned: %s | Paid: %s" % (self.client_wall, self.reward_earned, self.reward_paid)


class Client_InvalidPostBack(models.Model):
	reason = models.CharField(max_length=1000)
	offerwall = models.CharField(max_length=300)
	unique = models.CharField(max_length=300)
	playerid = models.CharField(max_length=300)
	client_wall = models.IntegerField()
	reward_earned = models.FloatField()
	reward_paid = models.FloatField()
	offer_name = models.CharField(max_length=300)
	offer_id = models.CharField(max_length=300)
	transid = models.CharField(max_length=50)
	def __str__(self):
		return "%s | Reason: %s" % (self.client_wall, str(self.reason)[:50])