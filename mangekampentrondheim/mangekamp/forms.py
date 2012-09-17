from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationForm

from mangekamp.models import UserProfile

class MangekampRegistrationForm(RegistrationForm):
    """
    Subclass of django-registration RegistrationForm which enforces
    unique capgemini email addresses for each user.
    """
    def clean_email(self):
        """
        Validate that the email is unique and that it originates 
        at sogeti or capgemini.
        """
        valid_domains = ['capgemini.com', 'capgemini.no', 'sogeti.com', 'sogeti.no']
        email_parts = self.cleaned_data['email'].split('@')
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("Denne eposten er allerede i bruk."))
        elif email_parts[1] not in valid_domains:
            raise forms.ValidationError(_("Eposten er ikke fra en gyldig organisasjon"))
        else:
            return self.cleaned_data['email']

class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['alternative_email'].required = False

    class Meta:
        model = UserProfile

class EmailEventForm(forms.Form):
    title = forms.CharField()
    body = forms.CharField(widget=forms.Textarea())
