from django.contrib import admin

from .models import Brand, Category, Perfume, Offer, Review, Gender, ReviewReply

# Register your models here.
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Perfume)
admin.site.register(Offer)
admin.site.register(Review)
admin.site.register(ReviewReply)
admin.site.register(Gender)

