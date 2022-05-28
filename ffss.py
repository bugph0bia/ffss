import time
import os
import datetime
import json

import pyautogui
from PIL import Image, ImageChops



USAGE = """================ ffss: form feed and screenshot ================
"""


def main():
    """main"""
    print(USAGE)

    # load stting
    st = load_setting()
    st = input_setting(st)

    # run screenshot
    screenshot(st)


def load_setting():
    """Load setting from file."""

    with open('setting.json', 'r', encoding='utf-8') as f:
        st = json.loads(f.read())
    return st


def input_setting(st):
    """Load setting from user input."""

    if 'page_num' not in st:
        t = intput_with_default('Number of pages, or "auto": ', 'auto')
        if not t:
            t = 'auto'
        st['page_num'] = t

    if 'page_derection' not in st:
        st['page_derection'] = intput_with_default('Page direction [l|r]: ', 'r')

    if 'wait_before_start_ms' not in st:
        st['wait_before_start_ms'] = intput_with_default('Wait before start [ms]: ', '5000')

    if 'interval_ms' not in st:
        st['interval_ms'] = intput_with_default('Interval [ms]: ', '1000')

    if 'output_dir_prefix' not in st:
        st['output_dir_prefix'] = intput_with_default('Output directory prefix: ', 'output_')

    if 'fname_prefix' not in st:
        st['fname_prefix'] = intput_with_default('File name prefix: ', 'page_')

    if 'trim_mode' not in st:
        st['trim_mode'] = 'manual'

    if 'trim_top_left' not in st:
        print('Press enter key, after move the mouse cursor top-left of the screenshot area...')
        input()
        x, y = pyautogui.position()
        st['trim_top_left'] = f'{x},{y}'

    if 'trim_bottom_right' not in st:
        print('Press enter key, after move the mouse cursor bottom-right of the screenshot area...')
        input()
        x, y = pyautogui.position()
        st['trim_bottom_right'] = f'{x},{y}'

    return st


def screenshot(st):
    """run screenshot"""

    # get settings or set default
    interval = int(st['interval_ms']) / 1000
    wait_before_start = int(st['wait_before_start_ms']) / 1000
    output_dir = st['output_dir_prefix'] + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    fname_prefix = st['fname_prefix']
    page_num = st['page_num']
    if page_num != 'auto':
        page_num = int(page_num)
    page_derection = st['page_derection']
    match page_derection.lower():
        case 'r' | 'right':
            page_derection = 'right'
        case 'l' | 'left':
            page_derection = 'left'
    trim_mode = st['trim_mode']
    match trim_mode.lower():
        case 'auto':
            trim_mode = 'auto'
        case 'auto-onetime':
            trim_mode = 'auto-onetime'
        case _:
            trim_mode = 'manual'
    trim_top_left = st['trim_top_left']
    x1 = int(trim_top_left.split(',')[0])
    y1 = int(trim_top_left.split(',')[1])
    trim_bottom_right = st['trim_bottom_right']
    x2 = int(trim_bottom_right.split(',')[0])
    y2 = int(trim_bottom_right.split(',')[1])

    # Waiting before starting
    print(f'Start after {wait_before_start} seconds, During which time the target window should be brought to the forefront...')
    time.sleep(wait_before_start)

    # make output directory
    os.mkdir(output_dir)

    region = None
    ss_old = None
    p = 0
    while True:
        # make file path
        fname = fname_prefix + str(p + 1).zfill(4) + '.png'
        fpath = os.path.join(output_dir, fname)

        # region = (x1, y1, x2 - x1, y2 - y1)
        # ss = pyautogui.screenshot(region=region)
        ss = pyautogui.screenshot()

        # triming
        # region is determined by trim_mode:
        #   - 'auto': Everytime, automatically determined.
        #   - 'auto-onetime': First time (Front cover) only, automatically determined.
        #   - 'manual': Determined by setting value.
        if trim_mode == 'auto' or (trim_mode == 'auto-onetime' and p == 0):
            region = get_trim_region(ss)
        elif trim_mode == 'manual':
            region = (x1, y1, x2, y2)
        ss = ss.crop(region)

        # (auto mode) same pages consecutive ?
        if page_num == 'auto':
            if ss_old == ss:
                break

        # save
        ss.save(fpath)
        print('save: {}'.format(fname))

        # reach the last page ?
        if isinstance(page_num, int):
            if p >= page_num:
                break

        # form feed
        pyautogui.keyDown(page_derection)
        time.sleep(interval)

        # next
        ss_old = ss
        p += 1


def intput_with_default(prompt, default):
    """input() with default value"""

    itext = input(prompt)
    if not itext:
        itext = default
    return itext


def get_trim_region(org_img):
    """get trim region automaticaly"""

    # create background image from RGB of (0, 0) pixel
    bg_img = Image.new('RGB', org_img.size, org_img.getpixel((0, 0)))

    # get trim region
    diff = ImageChops.difference(org_img, bg_img)
    region = diff.convert("RGB").getbbox()
    return region


if __name__ == '__main__':
    main()
