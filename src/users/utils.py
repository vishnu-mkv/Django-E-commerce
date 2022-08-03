import random, string
from .models import EmailActivation


def unique_key_generator():
    size = random.randint(30,40)
    key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))

    qs_exists = EmailActivation.objects.filter(key=key).exists()
    if qs_exists:
        unique_key_generator()
    else:
        return key

