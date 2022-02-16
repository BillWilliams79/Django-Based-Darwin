from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
from wi.models import domain, area


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        #
        # each user should have a single default domain and area
        #
        default_domain = domain(name='Personal', created_by=instance)
        default_domain.save()
        default_area = area(name='Home', domain=default_domain, created_by=instance)
        default_area.save()
