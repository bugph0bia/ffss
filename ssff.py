import time
import os
import datetime
import json
import shutil
import traceback

import pyautogui
import win32gui
import ctypes
from PIL import Image, ImageChops


VERSION = 'v0.4.0'


def main():
    """main"""
    print(f'================ ssff: Screenshot and form feed ({VERSION}) ================')

    # load stting
    st = load_setting()
    st = fill_setting(st)

    # run screenshot
    screenshot(st)

    print('All completed.')
    input()


def load_setting():
    """Load setting from file."""

    with open('setting.json', 'r', encoding='utf-8') as f:
        st = json.loads(f.read())
    return st


def fill_setting(st):
    """Fill setting from user input or default."""

    key = 'start_file_no'
    print(f'\n[{key}]')
    if key not in st:
        print('Start file number.\nDefault: 1')
        st[key] = intput_with_default('> ', '1')
    st[key] = max(int(st[key]), 1)
    print(f'{key} = {st[key]}')

    key = 'page_num'
    print(f'\n[{key}]')
    if key not in st:
        print('Number of pages, or "auto".\nDefault: auto')
        st[key] = intput_with_default('> ', 'auto')
    if st[key] != 'auto':
        st[key] = int(st[key])
    print(f'{key} = {st[key]}')

    key = 'page_direction'
    print(f'\n[{key}]')
    if key not in st:
        print('Page direction [right(r)|left(l)].\nDefault: right')
        st[key] = intput_with_default('> ', 'r')
    match st[key].lower():
        case 'r' | 'right':
            st[key] = 'right'
        case 'l' | 'left':
            st[key] = 'left'
    print(f'{key} = {st[key]}')

    key = 'wait_before_start_ms'
    print(f'\n[{key}]')
    if key not in st:
        print('Wait before start [ms].\nDefault: 5000')
        st[key] = int(intput_with_default('> ', '5000'))
    print(f'{key} = {st[key]}')

    key = 'interval_ms'
    print(f'\n[{key}]')
    if key not in st:
        print('Interval [ms].\nDefault: 1000')
        st[key] = int(intput_with_default('> ', '1000'))
    print(f'{key} = {st[key]}')

    key = 'output_dir_prefix'
    print(f'\n[{key}]')
    if key not in st:
        print('Output temporary directory prefix.\nDefault: output_')
        st[key] = intput_with_default('> ', 'output_')
    print(f'{key} = {st[key]}')

    key = 'fname_prefix'
    print(f'\n[{key}]')
    if key not in st:
        print('File name prefix.\nDefault: page_')
        st[key] = intput_with_default(' > ', 'page_')
    print(f'{key} = {st[key]}')

    key = 'ss_left'
    print(f'\n[{key}]')
    if key not in st:
        print('Press enter key after move the mouse cursor LEFT of the screenshot area.')
        print('Alternatively, enter "max" to use the maximum size of the display.')
        st[key] = input('> ')
    if not st[key]:
        st[key] = pyautogui.position()[0]
    elif str(st[key]).lower() == 'max':
        st[key] = 0
    else:
        st[key] = int(st[key])
    print(f'{key} = {st[key]}')

    key = 'ss_right'
    print(f'\n[{key}]')
    if key not in st:
        print('Press enter key after move the mouse cursor RIGHT of the screenshot area.')
        print('Alternatively, enter "max" to use the maximum size of the display.')
        st[key] = input('> ')
    if not st[key]:
        st[key] = pyautogui.position()[0]
    elif str(st[key]).lower() == 'max':
        st[key] = pyautogui.size()[0]
    else:
        st[key] = int(st[key])
    print(f'{key} = {st[key]}')

    key = 'ss_top'
    print(f'\n[{key}]')
    if key not in st:
        print('Press enter key after move the mouse cursor TOP of the screenshot area.')
        print('Alternatively, enter "max" to use the maximum size of the display.')
        st[key] = input('> ')
    if not st[key]:
        st[key] = pyautogui.position()[1]
    elif str(st[key]).lower() == 'max':
        st[key] = 0
    else:
        st[key] = int(st[key])
    print(f'{key} = {st[key]}')

    key = 'ss_bottom'
    print(f'\n[{key}]')
    if key not in st:
        print('Press enter key after move the mouse cursor BOTTOM of the screenshot area.')
        print('Alternatively, enter "max" to use the maximum size of the display.')
        st[key] = input('> ')
    if not st[key]:
        st[key] = pyautogui.position()[1]
    elif str(st[key]).lower() == 'max':
        st[key] = pyautogui.size()[1]
    else:
        st[key] = int(st[key])
    print(f'{key} = {st[key]}')

    key = 'trim'
    print(f'\n[{key}]')
    if key not in st:
        print('Trim position [none(n)|fit(f)|fit-onetime(o)].\nDefault: none')
        st[key] = intput_with_default('> ', 'none')
    match st[key].lower():
        case 'f' | 'fit':
            st[key] = 'fit'
        case 'o' | 'fit-onetime':
            st[key] = 'fit-onetime'
        case _:
            st[key] = 'none'
    print(f'{key} = {st[key]}')

    key = 'vsplit'
    print(f'\n[{key}]')
    if key not in st:
        print('Split image vertical, if width > height [yes(y)|no(n)].\nDefault: no')
        st[key] = intput_with_default('> ', 'no')
    match st[key].lower():
        case 'y' | 'yes':
            st[key] = 'yes'
        case _:
            st[key] = 'no'
    print(f'{key} = {st[key]}')

    key = 'target_window'
    print(f'\n[{key}]')
    if key not in st:
        print('Target window title (allow substring).')
        st[key] = intput_with_default('> ', None)
    print(f'{key} = {st[key]}')

    key = 'dir_name'
    print(f'\n[{key}]')
    if key not in st:
        print('Rename output directory after all processing. If not set, not rename.')
        st[key] = intput_with_default('> ', None)
    print(f'{key} = {st[key]}')

    key = 'to_zip'
    print(f'\n[{key}]')
    if key not in st:
        print('Zip compress output directory after all processing. [yes(y)|no(n)].\nDefault: no')
        st[key] = intput_with_default('> ', 'no')
    match st[key].lower():
        case 'y' | 'yes':
            st[key] = 'yes'
        case _:
            st[key] = 'no'
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
    start_file_no = st['start_file_no']
    page_num = st['page_num']
    page_direction = st['page_direction']
    x1 = st['ss_left']
    x2 = st['ss_right']
    y1 = st['ss_top']
    y2 = st['ss_bottom']
    trim = st['trim']
    vsplit = (st['vsplit'] == 'yes')
    target_window = st['target_window']
    dir_name = st['dir_name']
    to_zip = (st['to_zip'] == 'yes')

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
    page = 1
    fno = start_file_no

    # main process
    while True:
        # screenshot
        region = (x1, y1, x2 - x1, y2 - y1)
        ss = pyautogui.screenshot(region=region)

        # trim_area is determined by setting of 'trim':
        #   - 'none': No trimming.
        #   - 'fit': Everytime, automatically determined.
        #   - 'fit-onetime': First time (Front cover) only, automatically determined.
        if trim == 'fit' or (trim == 'fit-onetime' and page == 1):
            trim_area = fit_trim_area(ss)

        # triming
        if trim != 'none':
            ss = ss.crop(trim_area)

        # (auto mode) same pages consecutive ?
        if page_num == 'auto':
            if ss_old == ss:
                break

        if vsplit and ss.width > ss.height:
            # vertical split
            ssl = ss.crop((0, 0, ss.width//2, ss.height))
            ssr = ss.crop((ss.width//2, 0, ss.width, ss.height))
            # save
            save_image(ssl, output_dir, fname_prefix, fno)
            save_image(ssr, output_dir, fname_prefix, fno+1)
            fno += 2

        else:
            # save
            save_image(ss, output_dir, fname_prefix, fno)
            fno += 1

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
        
    print('Screenshot process completed.')

    # rename output dir
    if dir_name:
        try:
            os.rename(output_dir, dir_name)
            print(f'Rename output directory: {output_dir} -> {dir_name}')
            output_dir = dir_name
        except Exception:
            print(f'Failed rename output directory: {output_dir} -> {dir_name}')

    # zip compress output dir
    if to_zip:
        try:
            # compressing
            shutil.make_archive(output_dir, format='zip', root_dir=output_dir)
            print('Zip compress output dir.')
            # delete src directory
            shutil.rmtree(output_dir)
            print('Delete temporary directory.')
        except Exception:
            print('Failed zip compress or delete directory.')


def save_image(img, output_dir, fname_prefix, fno):
    """Save image."""
    # make file path
    fname = fname_prefix + str(fno).zfill(4) + '.png'
    fpath = os.path.join(output_dir, fname)
    # save
    img.save(fpath)
    print('save: {}'.format(fname))


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
    try:
        main()
    except Exception:
        traceback.print_exc()
        input()

