import pandas as pd
from selenium import webdriver
from selenium_stealth import stealth
import sqlite3
import time
import random
from pandas import DataFrame

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")

# options.add_argument("--headless")

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

data = {}

for page in range(1, 3):
    url = f"https://www.olx.ua/uk/transport/?page={page}%5Bprivate_business%5D=business"
    driver.get(url)

    blocks = driver.find_element('class name', "css-j0t2x2")
    posts = blocks.find_elements('class name', 'css-1sw7q4x')

    for post in posts:
        try:
            the_post_title = post.find_element('tag name', 'h6').text
            price = post.find_element('tag name', 'p').text
            title_link = post.find_element('tag name', 'a').get_attribute("href")

            data[title_link] = {
                'url': title_link,
                'price': price,
                'title': the_post_title
            }
        except Exception as e:
            print(f"Error processing post: {e}")


for post_url in data.values():
    time.sleep(random.randint(1, 5))
    driver.get(post_url['url'])
    driver.switch_to.default_content()
    time.sleep(3)
    try:
        if driver.find_element('xpath', '/html/body/div/div[2]/div[2]/div[3]/div[2]/div[1]'
                                        '/div[5]/div/button[2]').click():
            phone_number = driver.find_element('xpath', '/html/body/'
                                                        'div/div[2]/div[2]/div[3]/div[2]/'
                                                        'div[1]/div[5]/div/button[2]/span/a').text
        else:
            phone_number = None
    except Exception as e:
        phone_number = None
        #print(f"No number or you encountered a captcha: {e}")

    try:
        description = driver.find_element('class name', 'css-1wws9er').find_element('class name', 'css-1m8mzwg').text
    except Exception as e:
        description = None
        #print(f"Error getting description: {e}")

    post_url['phone_number'] = phone_number
    post_url['description'] = description

conn = sqlite3.connect('mydata.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    url TEXT,
    price TEXT,
    phone_number TEXT,
    description TEXT
)
''')

insert_data = [(post['title'], post['url'], post['price'], post['phone_number'], post['description'])
               for post in data.values()]

cursor.executemany('INSERT INTO posts (title, url, price, phone_number, description) VALUES (?,?,?,?,?)', insert_data)
conn.commit()

cursor.execute('SELECT * FROM posts')
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
