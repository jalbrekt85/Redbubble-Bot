from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os
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
    return BeautifulSoup(driver.page_source, 'html.parser').find('a', class_='works_work-menu-option works_work-menu-option__duplicate')['href']

def create_driver():
    chromedriver_autoinstaller.install()
    options = webdriver.ChromeOptions()
    options.add_argument('user-data-dir=' + os.getcwd() + '\\chrome_profile')
    return webdriver.Chrome(options=options)

def is_image(file):
    return file[-3:] == 'png' or file[-3:] == 'jpg'
    
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
        tags = open(dir + '/tags.txt', 'r').read() if os.path.exists(dir + '/tags.txt') else None
        self.designs += [Design(f'{dir}/{file}', tags) for file in os.listdir(dir) if is_image(file)]
        
    def upload_designs(self):
        driver = create_driver()
        if not is_logged_in(driver):
            print('You must login into Redbubble. If you are using the same Chrome Profile, you only need to do this once\nOnce you login, the bot will automatically continue')
            wait = WebDriverWait(driver, 300)
                                                            # This should be the landing page after logging in
            wait.until(lambda driver: driver.current_url == "https://www.redbubble.com/explore/for-you/#" or driver.current_url == 'https://www.redbubble.com/portfolio/manage_works?ref=account-nav-dropdown')
       
        template_link = get_template_link(driver)
        start = time.time()
        for design in self.designs:
            driver.get(template_link)
            
            element = driver.find_element_by_css_selector('#work_title_en')
            element.clear()
            element.send_keys(design.title)

            element = driver.find_element_by_css_selector('#work_tag_field_en')
            element.clear()
            element.send_keys(design.tags)

            element = driver.find_element_by_css_selector('#work_description_en')
            element.clear()
            element.send_keys(design.desc)

            driver.find_element_by_css_selector('#select-image-single').send_keys(design.location)

            driver.find_element_by_css_selector('#rightsDeclaration').click()
            element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#submit-work")))
            element.click()
            wait = WebDriverWait(driver, 60)
            wait.until(lambda driver: 'https://www.redbubble.com/studio/promote' in driver.current_url)
        print(f'Uploaded {len(self.designs)} Designs in {round(time.time()-start, 2)} Seconds')
        driver.quit()

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
