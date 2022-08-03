from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
import datetime
from .models import User, EmailActivation


class CustomLoginForm(AuthenticationForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    remember_me = forms.BooleanField(required=False)


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(label='Email',
                             max_length=255,
                             widget=forms.EmailInput(attrs={'class': 'form-control'}),
                             )
    first_name = forms.CharField(label='First Name',
                                 max_length=120,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Last Name',
                                max_length=120,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("The Email is already associated with an account!")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name').strip().capitalize()
        if first_name.isalpha():
            return first_name
        else:
            raise forms.ValidationError("Check your first name.")

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name').strip().capitalize()
        if last_name.isalpha():
            return last_name
        else:
            raise forms.ValidationError("Check your last name.")

    def clean(self):
        form = self.cleaned_data
        if form.get('password') != form.get('password2'):
            self.add_error('password2', 'Passwords do not match.')
        return form


class UserAdminCreateForm(RegisterForm):

    def save(self, commit=True):
        user = super(UserAdminCreateForm, self).save(commit=False)
        user.set_password(self.cleaned_data.get('password'))
        user.save(commit=True)
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'active', 'staff', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class ResendActivationForm(forms.ModelForm):
    email = forms.EmailField(label='Email', max_length=255, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = EmailActivation
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists() and qs.first().active:
            raise forms.ValidationError("The Email is already active! Click here to login")
        elif qs.exists() and not qs.first().active:
            today_min = datetime.datetime.combine(datetime.date.today(),datetime.time.min)
            today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
            qs2 = EmailActivation.objects.filter(email=email, date__range=(today_min, today_max), mail_sent=True)
            print(qs2, qs2.count())
            if qs2.count() > 5:
                raise forms.ValidationError("Limit exceeded. Check your Email")
        else:
            raise forms.ValidationError("Email is not registered. Click here to register")

        return email
