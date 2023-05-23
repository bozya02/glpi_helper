import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image
from io import BytesIO
from forcedisplays import *


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
