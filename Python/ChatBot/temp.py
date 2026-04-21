import pyautogui
import pyperclip
import time

pyautogui.click(1087,1040)
time.sleep(2)

pyautogui.moveTo(684,163)
pyautogui.dragTo(1041,879,duration=1.0,button='left')

pyautogui.hotkey('ctrl','c')
time.sleep(1)

text=pyperclip.paste()

pyautogui.click(763,1040)

print(text)
