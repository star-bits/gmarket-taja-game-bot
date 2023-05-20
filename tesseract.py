import hgtk
from ppadb.client import Client
import os
import cv2
import numpy as np
import pytesseract
import mss
import re

adb = Client(host='127.0.0.1', port=5037)
devices = adb.devices()
device = devices[0]

def decompose_into_jamo(input_string):
    decomposed_string = ""
    for char in input_string:
        if hgtk.checker.is_hangul(char):
            jamo = hgtk.letter.decompose(char)
            for component in jamo:
                if component != '':
                    decomposed_string += component
        else:
            decomposed_string += char
    return decomposed_string

# -----------------------------------------------------------------------------
# Keyboard Config
q_x, q_y = 60, 1700
p_x      = 1020
a_x, a_y = 100, 1830
l_x      = 975
z_x, z_y = 208, 1960
m_x      = 863

spce_y   = 2080
# -----------------------------------------------------------------------------

shft = (q_x, z_y)
engl = (q_x, spce_y)
spce = (p_x - q_x, spce_y)
entr = (p_x, spce_y)

alphabet_to_coord = {
    'Q': (q_x, q_y),
    'W': (q_x + (p_x - q_x) * 1 / 9, q_y),
    'E': (q_x + (p_x - q_x) * 2 / 9, q_y),
    'R': (q_x + (p_x - q_x) * 3 / 9, q_y),
    'T': (q_x + (p_x - q_x) * 4 / 9, q_y),
    'Y': (q_x + (p_x - q_x) * 5 / 9, q_y),
    'U': (q_x + (p_x - q_x) * 6 / 9, q_y),
    'I': (q_x + (p_x - q_x) * 7 / 9, q_y),
    'O': (q_x + (p_x - q_x) * 8 / 9, q_y),
    'P': (p_x, q_y),
    'A': (a_x, a_y),
    'S': (a_x + (l_x - a_x) * 1 / 8, a_y),
    'D': (a_x + (l_x - a_x) * 2 / 8, a_y),
    'F': (a_x + (l_x - a_x) * 3 / 8, a_y),
    'G': (a_x + (l_x - a_x) * 4 / 8, a_y),
    'H': (a_x + (l_x - a_x) * 5 / 8, a_y),
    'J': (a_x + (l_x - a_x) * 6 / 8, a_y),
    'K': (a_x + (l_x - a_x) * 7 / 8, a_y),
    'L': (l_x, a_y),
    'Z': (z_x, z_y),
    'X': (z_x + (m_x - z_x) * 1 / 6, z_y),
    'C': (z_x + (m_x - z_x) * 2 / 6, z_y),
    'V': (z_x + (m_x - z_x) * 3 / 6, z_y),
    'B': (z_x + (m_x - z_x) * 4 / 6, z_y),
    'N': (z_x + (m_x - z_x) * 5 / 6, z_y),
    'M': (m_x, z_y),
}

jamo_to_coord = {
    'ㅂ': alphabet_to_coord['Q'],
    'ㅈ': alphabet_to_coord['W'],
    'ㄷ': alphabet_to_coord['E'],
    'ㄱ': alphabet_to_coord['R'],
    'ㅅ': alphabet_to_coord['T'],
    'ㅛ': alphabet_to_coord['Y'],
    'ㅕ': alphabet_to_coord['U'],
    'ㅑ': alphabet_to_coord['I'],
    'ㅐ': alphabet_to_coord['O'],
    'ㅔ': alphabet_to_coord['P'],
    'ㅁ': alphabet_to_coord['A'],
    'ㄴ': alphabet_to_coord['S'],
    'ㅇ': alphabet_to_coord['D'],
    'ㄹ': alphabet_to_coord['F'],
    'ㅎ': alphabet_to_coord['G'],
    'ㅗ': alphabet_to_coord['H'],
    'ㅓ': alphabet_to_coord['J'],
    'ㅏ': alphabet_to_coord['K'],
    'ㅣ': alphabet_to_coord['L'],
    'ㅋ': alphabet_to_coord['Z'],
    'ㅌ': alphabet_to_coord['X'],
    'ㅊ': alphabet_to_coord['C'],
    'ㅍ': alphabet_to_coord['V'],
    'ㅠ': alphabet_to_coord['B'],
    'ㅜ': alphabet_to_coord['N'],
    'ㅡ': alphabet_to_coord['M'],
}

shift_jamo_to_coord = {
    'ㅃ': jamo_to_coord['ㅂ'],
    'ㅉ': jamo_to_coord['ㅈ'],
    'ㄸ': jamo_to_coord['ㄷ'],
    'ㄲ': jamo_to_coord['ㄱ'],
    'ㅆ': jamo_to_coord['ㅅ'],
    'ㅒ': jamo_to_coord['ㅐ'],
    'ㅖ': jamo_to_coord['ㅔ'],
}

combined_jamo_to_coord = {
    'ㅘ': (jamo_to_coord['ㅗ'], jamo_to_coord['ㅏ']),
    'ㅙ': (jamo_to_coord['ㅗ'], jamo_to_coord['ㅐ']),
    'ㅚ': (jamo_to_coord['ㅗ'], jamo_to_coord['ㅣ']),
    'ㅝ': (jamo_to_coord['ㅜ'], jamo_to_coord['ㅓ']),
    'ㅞ': (jamo_to_coord['ㅜ'], jamo_to_coord['ㅔ']),
    'ㅟ': (jamo_to_coord['ㅜ'], jamo_to_coord['ㅣ']),
    'ㅢ': (jamo_to_coord['ㅡ'], jamo_to_coord['ㅣ']),
    'ㄳ': (jamo_to_coord['ㄱ'], jamo_to_coord['ㅅ']),
    'ㄵ': (jamo_to_coord['ㄴ'], jamo_to_coord['ㅈ']),
    'ㄶ': (jamo_to_coord['ㄴ'], jamo_to_coord['ㅎ']),
    'ㄺ': (jamo_to_coord['ㄹ'], jamo_to_coord['ㄱ']),
    'ㄻ': (jamo_to_coord['ㄹ'], jamo_to_coord['ㅁ']),
    'ㄼ': (jamo_to_coord['ㄹ'], jamo_to_coord['ㅂ']),
    'ㄽ': (jamo_to_coord['ㄹ'], jamo_to_coord['ㅅ']),
    'ㄾ': (jamo_to_coord['ㄹ'], jamo_to_coord['ㅌ']),
    'ㄿ': (jamo_to_coord['ㄹ'], jamo_to_coord['ㅍ']),
    'ㅀ': (jamo_to_coord['ㄹ'], jamo_to_coord['ㅎ']),
    'ㅄ': (jamo_to_coord['ㅂ'], jamo_to_coord['ㅅ']),
}

# We know for sure that there are no lower case alphabets nor special characters.

def type_on_phone(input_string):
    decomposed_string = decompose_into_jamo(input_string)
    for char in decomposed_string:

        if char in jamo_to_coord:
            x, y = jamo_to_coord[char]
            device.shell(f'input touchscreen tap {x} {y}')
        
        if char in shift_jamo_to_coord:
            x, y = shft
            device.shell(f'input touchscreen tap {x} {y}')
            x, y = shift_jamo_to_coord[char]
            device.shell(f'input touchscreen tap {x} {y}')
            x, y = shft
            device.shell(f'input touchscreen tap {x} {y}')
                    
        if char in combined_jamo_to_coord:
            first, second = combined_jamo_to_coord[char]
            x, y = first
            device.shell(f'input touchscreen tap {x} {y}')
            x, y = second
            device.shell(f'input touchscreen tap {x} {y}')

        if char in alphabet_to_coord:
            x, y = engl
            device.shell(f'input touchscreen tap {x} {y}')
            x, y = alphabet_to_coord[char]
            device.shell(f'input touchscreen tap {x} {y}')
            x, y = engl
            device.shell(f'input touchscreen tap {x} {y}')

        if char == ' ':
            x, y = spce
            device.shell(f'input touchscreen tap {x} {y}')

    x, y = entr
    device.shell(f'input touchscreen tap {x} {y}')

# -----------------------------------------------------------------------------
# Model Config
# install tesseract: `brew install tesseract`
# check install location: `brew info tesseract` > `/opt/homebrew/Cellar/tesseract/5.3.1`
# `kor.traineddata` downloaded from https://github.com/tesseract-ocr/tessdata_best/blob/main/kor.traineddata should be placed at `/opt/homebrew/share/tessdata`
os.environ['TESSDATA_PREFIX'] = '/opt/homebrew/share/tessdata/'
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/Cellar/tesseract/5.3.1/bin/tesseract'
custom_config = r'--oem 3 --psm 6 -l kor+eng'
min_confidence = 95
# -----------------------------------------------------------------------------
# Image Config
top_left_x, top_left_y = 35, 257
bottom_right_x, bottom_right_y = 432, 678
capture_region = {"top": top_left_y, "left": top_left_x, "width": bottom_right_x - top_left_x, "height": bottom_right_y - top_left_y}
brightness_threshold = 191
darkening_factor = 0.5
# -----------------------------------------------------------------------------

def custom_threshold(img, threshold, factor):
    img_copy = img.copy()
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j] < threshold:
                img_copy[i, j] = img[i, j] * factor
    return img_copy

def process_ocr_result(ocr_result):
    lines = ocr_result.split('\n')
    regex = re.compile(r'[^A-Z\uac00-\ud7a3]')
    processed_lines = [regex.sub('', line) for line in lines]
    processed_lines = [line for line in processed_lines if line]
    return processed_lines

while True:
    with mss.mss() as sct:
        screen_capture = sct.grab(capture_region)

    image_np = np.array(screen_capture)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_BGRA2BGR)
    image_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    image_thresholded = custom_threshold(image_gray, brightness_threshold, darkening_factor)
    
    ocr_result = pytesseract.image_to_string(image_thresholded, config=custom_config)
    processed_lines = process_ocr_result(ocr_result)
    print(processed_lines)

    if processed_lines:
        type_on_phone(processed_lines[-1])

    output_height, output_width = image_thresholded.shape[:2]
    resized_image_thresholded = cv2.resize(image_thresholded, (output_width // 2, output_height // 2))

    cv2.imshow('OCR Input', resized_image_thresholded)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()