from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.common.keys import Keys
import os
import pyautogui
import random
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
from functools import partial


def is_logged_in(driver):
    driver.get('https://www.redbubble.com/portfolio/manage_works?ref=account-nav-dropdown')
    time.sleep(0.5)
    return driver.current_url != 'https://www.redbubble.com/auth/login'

def get_template_link(driver):
    # Manual selection
    # return 'https://www.redbubble.com/portfolio/images/12345678-artwork-title/duplicate'
    
    # Automatic selection
    driver.get('https://www.redbubble.com/portfolio/manage_works?ref=account-nav-dropdown')
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('a', class_='works_work-menu-option works_work-menu-option__duplicate')['href']

def create_driver(phone=False):
    chromedriver_autoinstaller.install()
    options = webdriver.ChromeOptions()
    options.add_argument('user-data-dir=' + os.getcwd() + '\\chrome_profile')
    
    # Emulate phone driver for instagram
    if phone:
        options.add_experimental_option("mobileEmulation", {"deviceName": "Pixel 2"})
    return webdriver.Chrome(options=options)

def is_image(file):
    return file[-3:] == 'png' or file[-3:] == 'jpg' or file[-4:] == 'jpeg'
    
class Design:
    def __init__(self, location, tags):
        self.location = location.replace('/', '\\')
        self.title = self.location.split('\\')[-1][:-4]
        self.tags = ', '.join(self.title.split()) if tags is None else tags
        self.desc = f'{self.title}: {self.tags}'
        
    def __repr__(self):
        return f'RB Design: {self.title}'


class Bot:
    def __init__(self):
        self.designs = []

    def add_designs(self, dir):
        found_designs = [os.path.abspath(file) for file in os.listdir(dir) if is_image(file)]
        if os.path.exists(dir + '/tags.txt'):
            tags = open(dir + '/tags.txt', 'r').read()
        else:
            tags = None
        self.designs += [Design(file, tags) for file in found_designs]
        random.shuffle(self.designs)
        print(self.designs)
        
    def upload_designs(self):
        driver = create_driver()
        if not is_logged_in(driver):
            print('You must login into Redbubble. If you are using the same Chrome Profile, you only need to do this once\nOnce you login, the bot will automatically continue')
            wait = WebDriverWait(driver, 9999)
                                                            # This should be the landing page after logging in
            wait.until(lambda driver: driver.current_url == "https://www.redbubble.com/explore/for-you/#")
        template_link = get_template_link(driver)
        
        for design in self.designs:
            driver.get(template_link)
            
            element = driver.find_element_by_css_selector('#work_title_en')
            element.send_keys(Keys.CONTROL, 'a')
            element.send_keys(Keys.BACKSPACE)
            element.send_keys(design.title)

            element = driver.find_element_by_css_selector('#work_tag_field_en')
            element.send_keys(Keys.CONTROL, 'a')
            element.send_keys(Keys.BACKSPACE)
            element.send_keys(design.tags)

            element = driver.find_element_by_css_selector('#work_description_en')
            element.send_keys(Keys.CONTROL, 'a')
            element.send_keys(Keys.BACKSPACE)
            element.send_keys(design.desc)

            driver.find_element_by_css_selector('#add-new-work > div > div.duplicate > div.upload-button-wrapper.replace-all-images').click()
            time.sleep(1.5)
            pyautogui.typewrite(design.location)
            time.sleep(1)
            pyautogui.hotkey('ENTER')
            time.sleep(20)

            driver.find_element_by_css_selector('#rightsDeclaration').click()
            driver.find_element_by_css_selector('#submit-work').click()
            time.sleep(30)

def run_gui():
    bot = Bot()
    current_row = ['']
    root = Tk()
    
    def open_dir(current_row):
        root.filename = filedialog.askdirectory(title='Select A Folder With Your Designs')
        if root.filename != '':
            dir_entry = Entry(root, width=50)
            dir_entry.insert(0, root.filename)
            dir_entry.grid(row=len(current_row), column=0)
            found_desings_label = Label(root, text='Found ' + str(len([file for file in os.listdir(root.filename) if is_image(file)])) + ' Designs')
            found_desings_label.grid(row=len(current_row), column=1)
            upload_button.grid(row=len(current_row)+1, column=0, pady=(15, 15))
            current_row.append('')
            bot.add_designs(root.filename)
            
    def upload():
        if len(bot.designs) != 0:
            bot.upload_designs()
        else:
            messagebox.showwarning('Empty Fields', 'Please select at least one folder with valid designs')

    open_dir_current = partial(open_dir, current_row)
    dir_button = Button(root, text='Add Designs', command=open_dir_current)
    upload_button = Button(root, text='upload', command=upload)
    dir_button.grid(row=0, column=0)

    root.mainloop()

    
if __name__ == '__main__':
    run_gui()
