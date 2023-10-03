from django.contrib import admin
from main.models import Offer, US_ValidPostBack, Client_InvalidPostBack, Client_ValidPostBack, Offerwall, Invoice, Stat_10, Stat_24, Account, Counter, Featured

class OfferAdmin(admin.ModelAdmin):
	search_fields = ('name','wall')


admin.site.register(Offer, OfferAdmin)


class AccountAdmin(admin.ModelAdmin):
	search_fields = ('email',)


admin.site.register(Account, AccountAdmin)

class US_ValidPostBackAdmin(admin.ModelAdmin):
	search_fields = ('unique',)


admin.site.register(US_ValidPostBack, US_ValidPostBackAdmin)


class Client_ValidPostBackAdmin(admin.ModelAdmin):
	search_fields = ('unique', 'transid',)


admin.site.register(Client_ValidPostBack, Client_ValidPostBackAdmin)

class Client_InvalidPostBackAdmin(admin.ModelAdmin):
	search_fields = ('unique', 'transid',)


admin.site.register(Client_InvalidPostBack, Client_InvalidPostBackAdmin)


admin.site.register(Stat_24)
admin.site.register(Stat_10)

class InvoiceAdmin(admin.ModelAdmin):
	search_fields = ('unique', 'status',)
admin.site.register(Invoice, InvoiceAdmin)



class OfferwallAdmin(admin.ModelAdmin):
	search_fields = ('id', 'unique',)

admin.site.register(Offerwall, OfferwallAdmin)


admin.site.register(Counter)

admin.site.register(Featured)