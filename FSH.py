from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time 
import re
import requests

fb_url = "https://m.facebook.com"
access_url = "https://www.facebook.com/v2.5/dialog/oauth?response_type=token&display=popup&client_id=145634995501895&redirect_uri=https%3A%2F%2Fdevelopers.facebook.com%2Ftools%2Fexplorer%2Fcallback&scope=user_status%2Cuser_location%2Cuser_tagged_places%2Cuser_photos%2Cuser_posts%2Cuser_relationship_details%2Cuser_relationships"
driver = webdriver.Firefox()
username=None
driver.get(fb_url)
assert "Welcome" in driver.title
driver.find_element_by_name("email").send_keys("Username")
driver.find_element_by_name("pass").send_keys("Password")
driver.find_element_by_name("pass").send_keys(Keys.RETURN)
while True:
	if driver.title == "Facebook":
		break
driver.get("https://m.facebook.com/me")

while True:
	if driver.title != "Facebook":
		url = str(driver.current_url)
		username = re.findall("m.facebook.com/(.+)\?_rdr",url)[0]
		break;
print username				
driver.get(access_url)
try:
	driver.find_element_by_name("__CONFIRM__").click()
except NoSuchElementException:
	pass
while True:
	if "Graph API Explorer" in driver.title:
		break
page_source=driver.page_source.encode('utf-8')
token= re.findall("accessToken\":\"(.+)\",\"anonymousTokenAllowed\"",page_source)[0]
print "Token = ",token
date = "1"
month = "1"
year = "2012"
d='%s-%s-%s 00:00:00'%(year,month,date)
p='%Y-%m-%d %H:%M:%S'
epoch = int(time.mktime(time.strptime(d,p)))
print "epoch = ",epoch
start=1
permalinks = []
while True:
	request  = "https://graph.facebook.com/fql?access_token=%s&q=SELECT permalink,privacy from stream WHERE source_id = me()  and  created_time < %s limit %s,10  "%(token,epoch,start)
	start += 10
	#print request
	response = requests.get(request)
	response_data = response.json()['data']
	if  len(response_data) == 0: 
		permalinks = set(permalinks)
		break
		
	else:
		for item in response_data:
			#print item['permalink']
			status_permalink = re.findall("(/posts/.+)",item['permalink'])
			if len(status_permalink)==1:
				priv = item['privacy']['value']
				if priv != "SELF"  :
					link = "https://m.facebook.com/%s%s"%(username,status_permalink[0])
					permalinks.append(link)		



for perm in permalinks:
	driver.get(perm)
	while True:
		if "Comments" in driver.title:
			break
		if "Photo" in driver.title:
			break
	if "Comments" in driver.title:
		elem = driver.find_elements_by_link_text("Public")
		if len(elem) == 0:
			elem = driver.find_elements_by_link_text("Friends")
		if len(elem) == 1:
			elem[0].click()
			driver.find_element_by_partial_link_text("Only Me").click()
		 
	if "Photo" in driver.title:
		try:
			driver.find_element_by_link_text("Hide from your Timeline").click()
			while True:
				if "photo.php" in driver.current_url:
					driver.find_element_by_xpath("//input[@value='Remove']").click()
					break
		except NoSuchElementException :
			pass

#driver.find_element_by_xpath("//a[@data-tooltip='Your friends']").click()
#driver.find_element_by_xpath("//li[@data-label='Only Me']").click()
