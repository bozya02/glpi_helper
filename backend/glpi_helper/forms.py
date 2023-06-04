from datetime import date
import json

import django.utils.timezone
from django import forms

import api.views
import config
from config import ITEM_TYPES


class ScannerForm(forms.Form):
    file = forms.FileField(label='Выберите файл', allow_empty_file=False)


class TicketForm(forms.Form):
    title = forms.CharField(label='Заголовок')
    description = forms.CharField(label='Описание', widget=forms.Textarea)
    anonymous = forms.BooleanField(label='Анонимная?', required=False, initial=config.CAN_ANON)
    username = forms.CharField(label='Логин', required=False)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=False)


class SearchForm(forms.Form):
    itemtype = forms.ChoiceField(choices=ITEM_TYPES, label='Тип устройства')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['itemtype'].widget.attrs['class'] = 'form-select'


class MovementForm(forms.Form):
    user = forms.CharField(label='Пользователь',
                           widget=forms.Select(
                               choices=[tuple([name, name]) for name in
                                        json.loads(api.views.get_users().content)['result']]),
                           )
    location = forms.CharField(label='Местоположение',
                               widget=forms.Select(
                                   choices=[tuple([name, name]) for name in
                                            json.loads(api.views.get_locations().content)['result']])
                               )
    date = forms.DateField(label='Дата', initial=django.utils.timezone.now(),
                           widget=forms.DateInput(attrs={'min': date.today().strftime('%d.%m.%Y')}))
