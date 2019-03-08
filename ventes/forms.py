from django import forms


class CommandeForm(forms.Form):
    id = forms.IntegerField(min_value=1, disabled=True)
    name = forms.CharField(max_length=32, min_length=2, disabled=True)
    date = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'], disabled=True)
    count = forms.IntegerField(min_value=1, max_value=9)
