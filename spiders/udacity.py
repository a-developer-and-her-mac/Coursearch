import json
import re
import os
import time 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def format_stars(s):
	starting = s.index(':')
	ending = s.index('%')
	answer = s[starting + 1:ending]
	answer = answer.strip()
	answer = float(answer) / 20
	answer = round(answer, 3)
	return answer

def configure_driver():
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	# chrome_options = Options()
	chrome_options.add_argument("--disable-dev-shm-usage")
	chrome_options.add_argument("--no-sandbox")
	# driver = webdriver.Chrome(executable_path="chromedriver.exe", options = chrome_options)
	driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options = chrome_options)
	return driver

def getCourses(driver , search_keyword):
	driver.get(f"https://www.udacity.com/courses/all?search={search_keyword}")
	try:
		WebDriverWait(driver, 5).until(lambda s: s.find_element_by_class_name("catalog-cards__list").is_displayed())
		ActionChains(driver).send_keys(Keys.ESCAPE).perform()
	except TimeoutException:
		print("TimeoutException: Element not found")

	buttons = driver.find_elements_by_xpath("//button[@class='card__bottom__button']")
	i = 0
	for button in buttons:
		try:
			ActionChains(driver).send_keys(Keys.ESCAPE).perform()
			time.sleep(0.1)
			button.click()
			i = i + 1
			if(i == 20):
				break
		except:
			pass
	ActionChains(driver).send_keys(Keys.ESCAPE).perform()
	
	soup = BeautifulSoup(driver.page_source, "lxml")

	mylist = []
	for course_page in soup.select("ul.catalog-cards__list"):
		for course in course_page.select("li.catalog-cards__list__item"):
			mydict = {}

			title_selector = "article.catalog-component div.catalog-component__card a.card__top div.card__title-container h2"
			partner_selector = "article.catalog-component div.catalog-component__card a.card__top div.card__title-container h3"
			author_selector = "article.catalog-component div.catalog-component__card a.card__top div.card__text-content section p.text-content__text"
			link_selector = "article.catalog-component div.catalog-component__card a.card__top"
			image_selector = "https://d20vrrgs8k4bvw.cloudfront.net/images/open-graph/udacity.png"
			level_selector = "article.catalog-component div.catalog-component__card div.card__bottom div.difficulty"
			reviews_selector = "article.catalog-component div.catalog-component__details div.layout__button-container div.reviews"
			stars_selector = "article.catalog-component div.catalog-component__details div.layout__button-container div.reviews div.nd-rating-stars div.active-stars"

			if course.select_one(reviews_selector).text:
				try:
					mydict["rating_count"] = float(re.sub(" Reviews","",str(course.select_one(reviews_selector).text)))
					mydict["rating_out_of_five"] = float((format_stars(course.select_one(stars_selector)['style'])))
					mydict["course_name"] = course.select_one(title_selector).text
					mydict["offered_by"] = "Udacity"
					mydict["partner_name"] = course.select(author_selector)[-1].text
					mydict["link_to_course"] = 'https://www.udacity.com' + course.select_one(link_selector)['href']
					mydict["image_link"] = image_selector
					mydict["difficulty_level"] = course.select_one(level_selector).text.capitalize()
					mylist.append(mydict)
				except:
					pass
			else:
				continue
			
	return mylist

def func(search_keyword):
	driver = configure_driver()
	list = getCourses(driver,search_keyword)
	driver.close()
	return list
