from django import forms


class CommandeForm(forms.Form):
    pk = forms.IntegerField(min_value=1)
    name = forms.CharField(max_length=32, min_length=2)
    date = forms.DateTimeField(input_formats=['%A %d %B %H:%M'])
    quantity = forms.IntegerField(min_value=1, max_value=9)
