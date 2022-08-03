from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('Email is required!')
        if not first_name:
            raise ValueError('First Name required!')
        if not last_name:
            raise ValueError('Last Name required!')
        if not password:
            raise ValueError('Password is required!')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name.strip().capitalize(),
            last_name=last_name.strip().capitalize(),
        )

        user.set_password(password)
        user.active = False
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, first_name, last_name, password):
        user = self.create_user(email=email,
                                first_name=first_name,
                                last_name=last_name,
                                password=password,
                                )
        user.active = True
        user.staff = True
        user.save(using=self._db)

        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(email=email,
                                first_name=first_name,
                                last_name=last_name,
                                password=password,
                                )
        user.active = True
        user.staff = True
        user.admin = True
        user.save(using=self._db)

        return user
