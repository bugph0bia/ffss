import time
import os
import datetime
import json

import pyautogui
import win32gui
import ctypes
from PIL import Image, ImageChops


VERSION = 'v0.0.1'


def main():
    """main"""
    print(f'================ ssff: Screenshot and form feed ({VERSION}) ================')

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
        print('Number of pages, or "auto".\nDefault: auto')
        itext = intput_with_default('> ', 'auto')
        if not itext:
            itext = 'auto'
        if itext != 'auto':
            itext = int(itext)
        st[key] = itext
        print(f'{key} = {st[key]}')

    key = 'page_direction'
    if key not in st:
        print(f'\n[{key}]')
        print('Page direction [right(r)|left(l)].\nDefault: right')
        itext = intput_with_default('> ', 'r')
        match itext.lower():
            case 'r' | 'right':
                itext = 'right'
            case 'l' | 'left':
                itext = 'left'
        st[key] = itext
        print(f'{key} = {st[key]}')

    key = 'wait_before_start_ms'
    if key not in st:
        print(f'\n[{key}]')
        print('Wait before start [ms].\nDefault: 5000')
        st[key] = int(intput_with_default('> ', '5000'))
        print(f'{key} = {st[key]}')

    key = 'interval_ms'
    if key not in st:
        print(f'\n[{key}]')
        print('Interval [ms].\nDefault: 1000')
        st[key] = int(intput_with_default('> ', '1000'))
        print(f'{key} = {st[key]}')

    key = 'output_dir_prefix'
    if key not in st:
        print(f'\n[{key}]')
        print('Output directory prefix.\nDefault: output_')
        st[key] = intput_with_default('> ', 'output_')
        print(f'{key} = {st[key]}')

    key = 'fname_prefix'
    if key not in st:
        print(f'\n[{key}]')
        print('File name prefix.\nDefault: page_')
        st[key] = intput_with_default(' > ', 'page_')
        print(f'{key} = {st[key]}')

    key = 'ss_left'
    if key not in st:
        print(f'\n[{key}]')
        print('Press enter key after move the mouse cursor LEFT of the screenshot area.')
        print('Alternatively, enter "max" to use the maximum size of the display.')
        itext = input('> ')
        if itext.lower() == 'max':
            st[key] = 0
        else:
            st[key] = pyautogui.position()[0]
        print(f'{key} = {st[key]}')

    key = 'ss_right'
    if key not in st:
        print(f'\n[{key}]')
        print('Press enter key after move the mouse cursor RIGHT of the screenshot area.')
        print('Alternatively, enter "max" to use the maximum size of the display.')
        itext = input('> ')
        if itext.lower() == 'max':
            st[key] = pyautogui.size()[0]
        else:
            st[key] = pyautogui.position()[0]
        print(f'{key} = {st[key]}')

    key = 'ss_top'
    if key not in st:
        print(f'\n[{key}]')
        print('Press enter key after move the mouse cursor TOP of the screenshot area.')
        print('Alternatively, enter "max" to use the maximum size of the display.')
        itext = input('> ')
        if itext.lower() == 'max':
            st[key] = 0
        else:
            st[key] = pyautogui.position()[1]
        print(f'{key} = {st[key]}')

    key = 'ss_bottom'
    if key not in st:
        print(f'\n[{key}]')
        print('Press enter key after move the mouse cursor BOTTOM of the screenshot area.')
        print('Alternatively, enter "max" to use the maximum size of the display.')
        itext = input('> ')
        if itext.lower() == 'max':
            st[key] = pyautogui.size()[1]
        else:
            st[key] = pyautogui.position()[1]
        print(f'{key} = {st[key]}')

    key = 'trim'
    if key not in st:
        print(f'\n[{key}]')
        print('Trim position [none(n)|fit(f)|fit-onetime(o)].\nDefault: none')
        itext = intput_with_default('> ', 'none')
        match itext.lower():
            case 'f' | 'fit':
                itext = 'fit'
            case 'o' | 'fit-onetime':
                itext = 'fit-onetime'
            case _:
                itext = 'none'
        st[key] = itext
        print(f'{key} = {st[key]}')

    key = 'target_window'
    if key not in st:
        print(f'\n[{key}]')
        print('Target window title (allow substring).')
        st[key] = intput_with_default('> ', None)
        print(f'{key} = {st[key]}')

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
    page_direction = st['page_direction']
    x1 = st['ss_left']
    x2 = st['ss_right']
    y1 = st['ss_top']
    y2 = st['ss_bottom']
    trim = st['trim']
    target_window = st['target_window']

    # foreground target window
    if target_window:
        foreground_window(target_window)

    # waiting before starting
    print(f'Start after {wait_before_start} seconds, during which time the target window should be brought to the forefront...')
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
        pyautogui.keyDown(page_direction)
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


def foreground_window(title):
    """Foreground the window with the specified title."""

    def fg(hwnd, lparam):
        """Callback by EnumWindows()"""

        caption = win32gui.GetWindowText(hwnd)
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)

        if caption.find(lparam) >= 0:
            if win32gui.IsIconic(hwnd):
                SW_SHOWNORMAL = 1
                win32gui.ShowWindow(hwnd, SW_SHOWNORMAL)

            # foreground
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            # activate
            pyautogui.moveTo(left + 5, top + 5)
            pyautogui.click()
            return False  # exit EnumWindows()

        return True  # continue EnumWindows()

    try:
        win32gui.EnumWindows(fg, title)
    except win32gui.error as e:
        # read off exceptions when enumeration is stopped (fg() returns False).
        pass


if __name__ == '__main__':
    main()
