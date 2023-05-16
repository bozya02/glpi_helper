from django import forms


class ScannerForm(forms.Form):
    file = forms.FileField(label='Выберите файл', allow_empty_file=False)
