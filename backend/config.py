ITEM_TYPES = [
    ('Computer', 'Компьютер'),
    ('Printer', 'Принтер'),
    ('Monitor', 'Монитор'),
    ('Peripheral', 'Другое'),
]

DOMAIN = '10.3.6.141:8000'
DEFAULT_QR = 'http://' + DOMAIN + '/scanner/{0}/{1}'

CAN_ANON = False