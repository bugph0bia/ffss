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
    st = fill_setting(st)

    # run screenshot
    screenshot(st)


def load_setting():
    """Load setting from file."""

    with open('setting.json', 'r', encoding='utf-8') as f:
        st = json.loads(f.read())
    return st


def fill_setting(st):
    """Fill setting from user input or default."""

    key = 'page_num'
    if key not in st:
        print(f'\n[{key}]')
        itext = intput_with_default('Number of pages, or "auto" > ', 'auto')
        if not itext:
            itext = 'auto'
        if itext != 'auto':
            itext = int(itext)
        st[key] = itext

    key = 'page_derection'
    if key not in st:
        print(f'\n[{key}]')
        itext = intput_with_default('Page direction [l|r] > ', 'r')
        match itext.lower():
            case 'r' | 'right':
                itext = 'right'
            case 'l' | 'left':
                itext = 'left'
        st[key] = itext

    key = 'wait_before_start_ms'
    if key not in st:
        print(f'\n[{key}]')
        st[key] = int(intput_with_default('Wait before start [ms] > ', '5000'))

    key = 'interval_ms'
    if key not in st:
        print(f'\n[{key}]')
        st[key] = int(intput_with_default('Interval [ms] > ', '1000'))

    key = 'output_dir_prefix'
    if key not in st:
        print(f'\n[{key}]')
        st[key] = intput_with_default('Output directory prefix > ', 'output_')

    key = 'fname_prefix'
    if key not in st:
        print(f'\n[{key}]')
        st[key] = intput_with_default('File name prefix > ', 'page_')

    key = 'ss_left'
    if key not in st:
        print(f'\n[{key}]')
        print('Press enter key after move the mouse cursor left of the screenshot area.')
        print('Alternatively, enter "max" to use the maximum size of the display.')
        itext = input('> ')
        if itext.lower() == 'max':
            st[key] = 0
        else:
            st[key] = pyautogui.position()[0]

    key = 'ss_right'
    if key not in st:
        print(f'\n[{key}]')
        print('Press enter key after move the mouse cursor right of the screenshot area.')
        print('Alternatively, enter "max" to use the maximum size of the display.')
        itext = input('> ')
        if itext.lower() == 'max':
            st[key] = pyautogui.size()[0]
        else:
            st[key] = pyautogui.position()[0]

    key = 'ss_top'
    if key not in st:
        print(f'\n[{key}]')
        print('Press enter key after move the mouse cursor top of the screenshot area.')
        print('Alternatively, enter "max" to use the maximum size of the display.')
        itext = input('> ')
        if itext.lower() == 'max':
            st[key] = 0
        else:
            st[key] = pyautogui.position()[1]

    key = 'ss_bottom'
    if key not in st:
        print(f'\n[{key}]')
        print('Press enter key after move the mouse cursor bottom of the screenshot area.')
        print('Alternatively, enter "max" to use the maximum size of the display.')
        itext = input('> ')
        if itext.lower() == 'max':
            st[key] = pyautogui.size()[1]
        else:
            st[key] = pyautogui.position()[1]

    key = 'trim'
    if key not in st:
        print(f'\n[{key}]')
        itext = intput_with_default('Trim posotion [none|fit|fit-onetime]: ', 'none')
        match itext.lower():
            case 'fit':
                itext = 'fit'
            case 'fit-onetime':
                itext = 'fit-onetime'
            case _:
                itext = 'none'
        st[key] = itext

    return st


def intput_with_default(prompt, default):
    """input() with default value"""

    itext = input(prompt)
    if not itext:
        itext = default
    return itext


def screenshot(st):
    """run screenshot"""

    # preparation
    interval = st['interval_ms'] / 1000
    wait_before_start = st['wait_before_start_ms'] / 1000
    output_dir = st['output_dir_prefix'] + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    fname_prefix = st['fname_prefix']
    page_num = st['page_num']
    page_derection = st['page_derection']
    x1 = st['ss_left']
    x2 = st['ss_right']
    y1 = st['ss_top']
    y2 = st['ss_bottom']
    trim = st['trim']

    # waiting before starting
    print(f'Start after {wait_before_start} seconds, During which time the target window should be brought to the forefront...')
    time.sleep(wait_before_start)

    # make output directory
    os.mkdir(output_dir)

    trim_area = None
    ss_old = None
    page = 0

    while True:
        # make file path
        fname = fname_prefix + str(page + 1).zfill(4) + '.png'
        fpath = os.path.join(output_dir, fname)

        # screenshot
        region = (x1, y1, x2 - x1, y2 - y1)
        ss = pyautogui.screenshot(region=region)

        # trim_area is determined by setting of 'trim':
        #   - 'none': No trimming.
        #   - 'fit': Everytime, automatically determined.
        #   - 'fit-onetime': First time (Front cover) only, automatically determined.
        if trim == 'fit' or (trim == 'fit-onetime' and page == 0):
            trim_area = fit_trim_area(ss)

        # triming
        if trim != 'none':
            ss = ss.crop(trim_area)

        # (auto mode) same pages consecutive ?
        if page_num == 'auto':
            if ss_old == ss:
                break

        # save
        ss.save(fpath)
        print('save: {}'.format(fname))

        # reach the last page ?
        if isinstance(page_num, int):
            if page >= page_num:
                break

        # form feed
        pyautogui.keyDown(page_derection)
        time.sleep(interval)

        # next
        ss_old = ss
        page += 1


def fit_trim_area(org_img):
    """Automatically fit to determine trim area"""

    # create background image from RGB of (0, 0) pixel
    bg_img = Image.new('RGB', org_img.size, org_img.getpixel((0, 0)))

    # get trim region
    diff = ImageChops.difference(org_img, bg_img)
    area = diff.convert('RGB').getbbox()
    return area


if __name__ == '__main__':
    main()
