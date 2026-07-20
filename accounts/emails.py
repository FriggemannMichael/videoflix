from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def build_activation_link(user, token):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    path = f'/pages/auth/activate.html?uid={uidb64}&token={token}'
    return f'{settings.FRONTEND_URL}{path}'


def _email_context(request, user, token):
    return {
        'activation_link': build_activation_link(user, token),
        'logo_url': request.build_absolute_uri(static('accounts/img/logo.png')),
    }


def send_activation_email(request, user, token):
    context = _email_context(request, user, token)
    html_body = render_to_string('accounts/activation_email.html', context)
    text_body = render_to_string('accounts/activation_email.txt', context)
    email = EmailMultiAlternatives(
        subject='Confirm your email',
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_body, 'text/html')
    email.send()
