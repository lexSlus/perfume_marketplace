from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import UserProfile, Account


@receiver(post_save, sender=Account)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Account)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


@receiver(post_save, sender=UserProfile)
def update_could_sell(sender, instance, created, **kwargs):
    if created:
        instance.could_sell = instance.is_complete()
        instance.save()
    elif 'update_fields' in kwargs and kwargs['update_fields']:
        if any(field in kwargs['update_fields'] for field in ['address_line', 'city', 'profile_picture']):
            instance.could_sell = instance.is_complete()
            instance.save()
