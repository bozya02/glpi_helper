from django import forms


class ScannerForm(forms.Form):
    file = forms.FileField(label='Выберите файл', allow_empty_file=False)

class TicketForm(forms.Form):
    title = forms.CharField(label='Заголовок')
    description = forms.CharField(label='Описание', widget=forms.Textarea)
    anonymous = forms.BooleanField(label='Анонимная?', required=False, initial=True)
    username = forms.CharField(label='Логин', required=False)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=False)