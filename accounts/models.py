from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string


class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password=None, phone_number=None):
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.is_confirmed = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)

    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)

    confirmation_token = models.CharField(max_length=64, blank=True)

    objects = MyAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def generate_confirmation_token(self):
        """
        Generates a unique confirmation token and saves the user.
        """
        self.confirmation_token = get_random_string(64)
        self.save()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line = models.CharField(blank=True, max_length=100)
    profile_picture = models.ImageField(blank=True, upload_to='userprofile/',
                                        default='/userprofile/default_profile.png')
    city = models.CharField(blank=True, max_length=20)
    could_sell = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name

    def is_complete(self):
        return all([self.address_line, self.city, self.profile_picture])
