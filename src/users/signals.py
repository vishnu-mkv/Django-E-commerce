from django.db.models.signals import pre_save, post_save

from store.models import Cart
from .models import User, EmailActivation
from .utils import unique_key_generator


def send_activation_mail(sender, instance, created, **kwargs):
    if created:
        self_ = EmailActivation.objects.create(user=instance, email=instance.email, key=unique_key_generator())
        EmailActivation.send_activation(self_)

# creat cart
def create_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)

post_save.connect(send_activation_mail, sender=User)
post_save.connect(create_cart, sender=User)
