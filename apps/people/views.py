from django import forms
from django.contrib.auth import login, logout as _logout, get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils import six
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode, int_to_base36
from django.utils.crypto import salted_hmac
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, FormView
from django_database_constraints.views import TransactionalModelFormMixin

from .models import User
from lib.common.views import NextMixin
from lib.render_to_email import render_to_email


class RegisterView(TransactionalModelFormMixin, FormView):
    """
    Create a new user account.
    """
    
    template_name = "registration/register.html"
    success_url = reverse_lazy("registered")

    def validationerror_from_integrityerror(self, ierror):
        # only one integrity constraint against the User model
        return forms.ValidationError(
            {
                'email': _('That email address is already in use.'),
            }
        )

    def get_form_class(self):
        request = self.request
        
        class Register(forms.Form):
            email = forms.EmailField()
            name = forms.CharField(
                label=_('Display name on site'),
                max_length=500,
            )
            password = forms.CharField(
                widget=forms.PasswordInput,
            )

            def save(self):
                user = User(
                    email=self.cleaned_data['email'],
                    name=self.cleaned_data['name'],
                    is_active=False,
                )
                user.set_password(self.cleaned_data['password'])
                user.save()

                c = {
                    'email': user.email,
                    'confirm_url': request.build_absolute_uri(
                        reverse(
                            'confirm_email_address',
                            kwargs={
                                'uidb64': urlsafe_base64_encode(
                                    force_bytes(user.pk),
                                ),
                                'token': token_generator.make_token(user),
                            },
                        )
                    ),
                    'user': user,
                }

                render_to_email(
                    text_template='registration/welcome_email.txt',
                    html_template='registration/welcome_email.html',
                    to=(user,),
                    subject=_('Welcome to Kallisto!'),
                    opt_out=False,
                    context=c,
                )
                
                return user

        return Register
register = RegisterView.as_view()


class RegisteredView(TemplateView):
    """Say 'thanks, now wait for the email'."""

    template_name = "registration/registered.html"
registered = RegisteredView.as_view()


class EmailConfirmationTokenGenerator(PasswordResetTokenGenerator):
    key_salt = "apps.people.EmailConfirmationTokenGenerator"

    def _make_token_with_timestamp(self, user, timestamp):
        # timestamp is number of days since 2001-1-1.  Converted to
        # base 36, this gives us a 3 digit string until about 2121
        ts_b36 = int_to_base36(timestamp)

        # By hashing on the internal state of the user and using state
        # that is sure to change, we produce a hash that will be
        # invalid as soon as it is used.
        # We limit the hash to 20 chars to keep URL short

        # Ensure results are consistent across DB backends
        if user.last_login is None:
            # Gets converted to a string directly, so this will do fine
            # since as soon as they log in this will change.
            login_timestamp = 0
        else:
            login_timestamp = user.last_login.replace(
                microsecond=0,
                tzinfo=None,
            )

        value = (six.text_type(user.pk) + user.password +
                six.text_type(login_timestamp) + six.text_type(timestamp))
        hash = salted_hmac(self.key_salt, value).hexdigest()[::2]
        return "%s-%s" % (ts_b36, hash)
token_generator = EmailConfirmationTokenGenerator()


@never_cache
def confirm_email_address(
    request,
    uidb64,
    token,
    error_template="registration/failed_email_confirm.html",
    template="registration/email_confirm.html",
    redirect_to="/"
):
    redirect = request.GET.get('next', None)
    args = request.GET.copy()
    if 'next' in args:
        del args['next']
    args = args.urlencode()
    if redirect is None:
        redirect = redirect_to
    if args != "":
        if '?' in redirect:
            redirect += '&'
        else:
            redirect += '?'
        redirect += args

    try:
        user = User.objects.get(pk=urlsafe_base64_decode(uidb64))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if request.user.is_authenticated() and request.user != user:
        user = None

    if user is None or not token_generator.check_token(user, token):
        return TemplateResponse(request, error_template, {}, status=400)

    if request.method == 'POST':
        if request.user.is_authenticated():
            if request.user == user:
                user.is_active = True
                user.save()
                update_last_login(None, user)
                return HttpResponseRedirect(redirect)
            else:
                return TemplateResponse(request, error_template, {}, status=400)

        user.is_active = True
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return HttpResponseRedirect(redirect)
    else:
        return TemplateResponse(request, template, { 'next': redirect, 'email': user.email })


class LogoutView(TemplateView, NextMixin):
    """
    Logs the user out.
    """
    
    template_name = "registration/logout.html"
    
    def post(self, request):
        _logout(self.request)
        return HttpResponseRedirect(self.get_next_url())
logout = LogoutView.as_view()

    
@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None): # pragma: no cover
    # Don't bother running coverage for this...although it really should
    # be tested, this MUST be folded into Django at some point before
    # I become the annoying person at conferences who just wants to talk
    # about fixing the auth app.
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    
    NOTE: we adapt this because we want to automatically log them in
    once they've set their new password. Because this is correct behaviour.
    And it's IMPOSSIBLE to do this in a form, because forms don't get a
    Request object as context. Sigh.
    """
    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    try:
        uid_int = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid_int)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        title = _('Enter new password')
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                user = form.save()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        validlink = False
        form = None
        title = _('Password reset unsuccessful')
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)
