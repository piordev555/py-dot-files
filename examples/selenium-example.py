import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# open the web browser
driver = webdriver.Firefox()
driver.get('http://www.python.org')

# wait
time.sleep(5)

# select the pypi button
elem = driver.find_element_by_class_name('pypi-meta')
elem.click()

# wait
time.sleep(4)

# select the search element
elem = driver.find_element_by_id('term')

# type in the input text field
elem.send_keys('django')

# hit enter
elem.send_keys(Keys.RETURN)

time.sleep(10)

# go back
driver.back()

time.sleep(3)

# go back again
driver.back()

# wait
time.sleep(2)

# select the search element
elem = driver.find_element_by_id('id-search-field')
elem.click()

# type in the input text field
elem.send_keys('manuel')

# hit enter
elem.send_keys(Keys.RETURN)

# wait
time.sleep(5)

# click on the result
elem = driver.find_element_by_css_selector(
    '.list-recent-events > li:nth-child(1) > h3:nth-child(1) > a:nth-child(1)')
elem.click()

# wait
time.sleep(5)

# close the browser
driver.close()
