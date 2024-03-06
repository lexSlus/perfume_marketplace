from django.contrib import admin

from accounts.models import Account, UserProfile

admin.site.register(Account)
admin.site.register(UserProfile)
