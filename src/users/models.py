from django.conf import settings
from django.db import models
from django.urls import reverse
from django.template.loader import get_template
from django.core.mail import send_mail
from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser

from store.models import Cart
from .manager import UserManager


# Create your models here.


class User(AbstractBaseUser):
    email = models.EmailField(unique=True, verbose_name='email address', max_length=255)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    date_created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)  # True on email activation
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        return str(self.first_name + ' ' + self.last_name)

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


class EmailActivation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255)
    key = models.CharField(max_length=225, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)
    activated = models.BooleanField(default=False)
    mail_sent = models.BooleanField(default=False)

    objects = models.Manager()

    def __str__(self):
        return self.email

    def send_activation(self):
        if not self.activated and not self.expired:
            if self.key:
                base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                key_path = reverse('accounts:email-activate', kwargs={'key': self.key})
                path = "{base}{key}".format(base=base_url, key=key_path)
                name = User.objects.filter(email=self.email).first().first_name
                context = {
                    'path': path,
                    'name': name,
                    'email': self.email,
                }
                txt_ = get_template('register_mail.txt').render(context)
                html_ = get_template('register_mail.html').render(context)
                subject = "Activate your NameIt account."
                from_email = settings.DEFAULT_FROM_EMAIL
                reciptent = [self.email]
                sent_mail = send_mail(subject,
                                      txt_,
                                      from_email,
                                      reciptent,
                                      False,
                                      html_message=html_
                )
                # sent_mail = True
                if sent_mail:
                    self.mail_sent = True
                    self.save()
                return sent_mail
        return False

    def validate_key(self):
        now = timezone.now()
        if not self.user.active and not self.expired:
            time_diff = now - self.date
            if time_diff.days == 0:
                return {'user_id': self, 'valid': True}
            else:
                self.expired = True
                self.save()
        return {'user_id': self, 'valid': False}

    def activate(self):
        self.user.active = True
        self.user.save()
        self.activated = True
        self.save()











