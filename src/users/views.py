from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout

from .forms import RegisterForm, ResendActivationForm, CustomLoginForm
from .models import User, EmailActivation
from .utils import unique_key_generator

def logout_view(request):
    logout(request)
    return redirect('/')


class LogInView(LoginView):
    authentication_form = CustomLoginForm
    form_class = CustomLoginForm
    template_name = 'login.html'

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        login(self.request, form.get_user())
        if remember_me:
            self.request.session.set_expiry(1209600)
        return redirect(self.get_success_url())


    #def get(self):
     #   if self.request.is_authenticated:
      #      return redirect('profile/')
       # else:
        #    return render(self.request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            request.session['register_success'] = True
            return redirect('users:register_success')
    if request.method == 'GET':
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def account_activate_view(request, key):
    obj = EmailActivation.objects.filter(key=key).first()
    validation = {}
    msg = ""
    if obj is not None:
        validation = obj.validate_key()
    else:
        msg = "Invalid key."
    print(obj.user.active)
    if not validation['valid'] and not obj.user.active:
        msg = "Key expired. Click here to resend email activation"
    elif obj.user.active:
        msg = "User already active. Click here to LogIn"
    elif validation['valid']:
        validation['user_id'].activate()
        return redirect('users:login')
    return render(request, 'email_validate.html', {'msg': msg})


def registration_success_view(request):
    # To block users who use direct urls
    success = False
    if request.session.get('register_success'):
        success = request.session['register_success']

    context = {
        'success': success
    }
    return render(request, 'register_success.html', context)


def resend_activation_view(request):
    form = ResendActivationForm()
    if request.method == 'POST':
        form = ResendActivationForm(request.POST)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data.get('email'))
            new_mail = EmailActivation.objects.create(user=user,
                                                      email=form.cleaned_data.get('email'),
                                                      key=unique_key_generator())
            response = new_mail.send_activation()
            if response:
                request.session['register_success'] = True
                return redirect('users:register_success')

    return render(request, 'resend_activation.html', {'form': form})
