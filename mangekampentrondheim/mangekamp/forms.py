from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationForm

from mangekamp.models import UserProfile, Event

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
    first_name = forms.CharField(required=False, label="Fornavn")
    last_name = forms.CharField(required=False, label="Etternavn")

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['alternative_email'].required = False
        userprofile = UserProfile.objects.get(id=self.initial['id'])
        self.fields['first_name'].initial = userprofile.user.first_name
        self.fields['last_name'].initial = userprofile.user.last_name

    def save(self):
        userprofile = super(UserProfileForm, self).save()
        user = userprofile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

    class Meta:
        model = UserProfile

class EmailEventForm(forms.Form):
    title = forms.CharField(label='Tittel')
    body = forms.CharField(widget=forms.Textarea(), label='Innhold')
