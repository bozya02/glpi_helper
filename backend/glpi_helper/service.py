import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
from PIL import Image

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image
from io import BytesIO

from config import DEFAULT_QR
from forcedisplays import *
import qrcode
from reportlab.pdfgen import canvas
from api.models import Item

def recognize_qr(file):
    inp = np.asarray(bytearray(file), dtype=np.uint8)
    img = cv2.imdecode(inp, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('gray.jpg', gray)

    edges = cv2.Canny(gray, 50, 150)
    cv2.imwrite('edges.jpg', edges)

    contours, hierarchy = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
        if len(approx) == 4:
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(img, [box], 0, (0, 0, 255), 2)

    decoded_objects = pyzbar.decode(gray)

    content = None
    for obj in decoded_objects:
        content = obj.data.decode('utf-8')
        print("Data: ", content)
    return content


def get_table_display():
    display = {key: forces['item'][key] for key in table_display if key in forces['item']}

    return display


def get_qr_display(is_computer):
    display = {key: forces['item'][key] for key in qr_display if key in forces['item']}
    if is_computer:
        display.update(forces['computer'])

    return display


def generate_xlsx(items):
    workbook = Workbook()
    worksheet = workbook.active
    display = get_table_display()

    header = ['Номер'] + list(display.values()) + ['Ответственный']
    for col_num, header_title in enumerate(header, 1):
        col_letter = get_column_letter(col_num)
        worksheet[f'{col_letter}1'] = header_title

    for row_num, item in enumerate(items, start=2):
        worksheet[f'A{row_num}'] = row_num - 1
        for col_num, key in enumerate(display.keys(), start=2):
            col_letter = get_column_letter(col_num)
            worksheet[f'{col_letter}{row_num}'] = item['item'].get(key, '')

        worksheet[f'{get_column_letter(len(display) + 2)}{row_num}'] = item['user']

    excel_file = BytesIO()

    # Save the workbook to the BytesIO object
    workbook.save(excel_file)
    excel_file.seek(0)

    return excel_file

def generate_qr(item_ids, itemtype):
    if len(item_ids) == 1:
        # Генерация фотографии QR-кода

        item_id = item_ids[0]

        db_item = Item.check_or_create_item(item_id, itemtype)

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(DEFAULT_QR.format(db_item.item_type, db_item.guid))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        return buffer
    else:
        # Генерация PDF-файла
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)

        x = 10
        y = 700

        for i, item_id in enumerate(item_ids):
            print(item_id)

            db_item = Item.check_or_create_item(item_id, itemtype)

            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(DEFAULT_QR.format(db_item.item_type, db_item.guid))
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            pdf.drawInlineImage(img, x, y, width=130, height=130)

            if i % 4 == 3:
                x = 10
                y -= 150
            else:
                x += 150

        pdf.save()

        buffer.seek(0)

        return buffer