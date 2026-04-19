from django import forms
from website.models import Contact, NewsLetter

class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = '__all__'


class NewsLetterForm(forms.ModelForm):

    class Meta:
        model = NewsLetter
        fields = '__all__'