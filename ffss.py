import time
import os
import datetime

import pyautogui


def main():
    # ======== Initialization ========

    # Number of pages
    page = int(input('Number of pages: '))

    # Page direction (left or right)
    direction = 'left'  # default
    if input('Page direction [l|r]: ') == 'r':
        direction = 'right'

    # Top-left of the screenshot area
    print('Press enter key, after move the mouse cursor top-left of the screenshot area...')
    input()
    x1, y1 = pyautogui.position()

    # Bottom-right of the screenshot area
    print('Press enter key, after move the mouse cursor bottom-right of the screenshot area...')
    input()
    x2, y2 = pyautogui.position()

    # To predefine an area, specify a magic number
    # x1 = <magic number>
    # y1 = <magic number>
    # x2 = <magic number>
    # y2 = <magic number>

    # Screenshot interval (seconds)
    wait = float(input('interval [s]: '))

    # Waiting before starting
    print('Start after 5 seconds, During which time the target window should be brought to the forefront...')
    time.sleep(5)

    # ======== Preprocess ========

    # file name prefix
    fname_prefix = "page"

    # make output directory
    output_dir = "output_" + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    os.mkdir(output_dir)

    # ======== Screenshot ========

    for p in range(page):
        # save the screenshot
        fname = fname_prefix + str(p + 1).zfill(4) + '.png'
        r = (x1, y1, x2 - x1, y2 - y1)
        ss = pyautogui.screenshot(region=r)
        ss.save(os.path.join(output_dir, fname))
        print('save: {}'.format(fname))

        # form feed
        pyautogui.keyDown(direction)
        time.sleep(wait)


if __name__ == '__main__':
    main()
