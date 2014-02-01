from django.http import HttpResponse
import urllib, urllib2,json,string,httplib,time
import logging
import requests
from BeautifulSoup import BeautifulSoup
import datetime
import time
import urlparse

class LoginManager(object):
	def __init__(self,email,password):
		self.username = email
		self.password = password
		self.BIGipServerweb1lougb = ""
		self.PageUniqueId = ""
		self.viewstate = ""
		self.eventvalidation = ""
		self.ASPXAUTH = ""
		self.studentId = 0
	def login(self):
		#First we just go to the login page to get the unique id,serverid,viewstate,and eventvalidation
		r = requests.get("https://loudoun.gradebook.net/clarity/Gradebook/Logon.aspx")
		self.BIGipServerweb1lougb = r.cookies['BIGipServerweb1lougb']
		soup = BeautifulSoup(r.content)
		#not a fan of parsing html but w/e it gets us what we need
		self.PageUniqueId = soup.find('input',{'id' : 'PageUniqueId'})['value']
		self.viewstate = soup.find('input',{'id' : '__VIEWSTATE'})['value']
		self.eventvalidation = soup.find('input',{'id' : '__EVENTVALIDATION'})['value']
		#now we need to login, we do this by posting login info and other stuff
		#We grab the ASPXAUTH from this, which is one of the key parts to logging in
		headers = {	'Content-Type': 'application/x-www-form-urlencoded'}
		cookies = { 'BIGipServerweb1lougb':self.BIGipServerweb1lougb}
		#lots of data to post
		payload = { '__LASTFOCUS':'','__EVENTTARGET':'','__EVENTARGUMENT':'','__VIEWSTATE':self.viewstate,
					'__EVENTVALIDATION':self.eventvalidation, 'ctl00$ContentPlaceHolder$Username':self.username,
					'ctl00$ContentPlaceHolder$Password':self.password,'ctl00$ContentPlaceHolder$lstDomains':'Pinnacle',
					'ctl00$ContentPlaceHolder$lstDomains':'Pinnacle','ctl00$ContentPlaceHolder$LogonButton':'Sign in',
					'ctl00$ContentPlaceHolder$LogonButton':'Sign in','PageUniqueId':self.PageUniqueId}
		
		next_loc = 'https://loudoun.gradebook.net/clarity/Gradebook/Logon.aspx'
		r = requests.post(next_loc,headers = headers,data = payload,cookies = cookies,allow_redirects = False)
		try:
			self.ASPXAUTH = r.cookies['PinnacleWeb.ASPXAUTH']
		except:
			return False
		#Now we need to go to the main grade page and get our student id number
		#we also need to get a new unique page id..idk why they even have this
		cookies = { 'BIGipServerweb1lougb':self.BIGipServerweb1lougb,'PinnacleWeb.DomainId':'Pinnacle',
					'PinnacleWeb.ASPXAUTH':self.ASPXAUTH}

		next_loc = 'https://loudoun.gradebook.net/clarity/Gradebook/InternetViewer/Default.aspx'
		r = requests.get(next_loc,cookies = cookies)
		self.studentId = r.cookies['PinnacleWeb.StudentId']
		soup = BeautifulSoup(r.content)
		self.PageUniqueId = soup.find('input',{'id' : 'PageUniqueId'})['value']
		#We now have every key that we need for logging in
		return True
	def get_grade_json(self):
		self.final_list = []
		#we go to default clarity page so we can parse the html and get what we want
		cookies = { 'BIGipServerweb1lougb':self.BIGipServerweb1lougb,'PinnacleWeb.DomainId':'Pinnacle',
					'PinnacleWeb.ASPXAUTH':self.ASPXAUTH}

		next_loc = 'https://loudoun.gradebook.net/clarity/Gradebook/InternetViewer/GradeSummary.aspx?'
		r = requests.get(next_loc,cookies = cookies)
		soup = BeautifulSoup(r.content)
		#Next part of getting the grade data is at this url
		#it returns json and is easier than parsing html
		cookies = { 'BIGipServerweb1lougb':self.BIGipServerweb1lougb,'PinnacleWeb.DomainId':'Pinnacle',
					'PinnacleWeb.ASPXAUTH':self.ASPXAUTH}
		payload = {"studentId":self.studentId}
		next_loc = 'https://loudoun.gradebook.net/clarity/Gradebook/InternetViewer/InternetViewerService.ashx/Init?'
		r = requests.post(next_loc,cookies = cookies,data = payload)
		json_grade_data = json.loads(r.content)['classes']
		#might be multiple boxes so we get all tbodys just in case there is multiple
		grade_data = soup.findAll('table',{'class' : 'reportTable'})
		all_class_list = []
		period_list = []
		for chart_data in grade_data:
			class_index = 0
			for each_class in chart_data.findAll('tbody'):
				for class_data in each_class.findAll('tr'):
					class_dict = {}
					grade_list = []
					term_list = []
					#parse html to get title and grade numbers
					class_title = class_data.find('th',{'class' : 'classTitle'}).text
					class_dict['class_name'] = class_title
					enroll_id = [""]
					for letter_grade_data in class_data.findAll('td',{'colspan' : '3'}):
						grade_list.append(letter_grade_data.text)
						try:
							info_url = letter_grade_data.find('a',href=True)['href']
							parsed = urlparse.urlparse(info_url)
							enroll_id = urlparse.parse_qs(parsed.query)['EnrollmentId']
							term_id = urlparse.parse_qs(parsed.query)['TermId']
							term_list.append(urlparse.parse_qs(parsed.query)['TermId'])
						except:
							term_list.append(["0"])
					#set values in class_dict
					class_dict['grade_values'] = grade_list
					class_dict['enroll_id'] = enroll_id
					class_dict['term_ids'] = term_list
					#add class data into a list with rest of classes
					all_class_list.append(class_dict)
					class_index += 1
			#Now we need to grab the periods. 
			#I believe the one with the most data will be on the bottom
			#If not screw clarity
			#tis to confusing
			period_list = []
			for quarter_name in chart_data.findAll('th',{'colspan' : '3'}):
				#This is the first entry for some reason
				#Screws up my parsing lol
				if quarter_name.text != 'Course Grade-Sec':
					period_list.append(quarter_name.text)
		#I don't get all the names though if it is highschool..
		#I have to hardcode what they are
		#Pretty annoying
		if len(period_list) ==  9:
		    period_list[3] = 'First Semester Final Grade'
		    period_list[7] = 'Second Semester Final Grade'
		    period_list[8] = 'Final Grade'
		    for _class in all_class_list:
		        if len(_class['grade_values']) == 5:
		            _class['grade_values'].insert(2,"")
		            _class['grade_values'].insert(3,"")
		            _class['grade_values'].insert(6,"")
		            _class['grade_values'].insert(7,"")
		#I could have a way of determing the period, but I am just going to set it lol...
		quarter_index = 3
		#appends other things we need for displaying grades
		self.final_list.append({'classes':all_class_list})
		self.final_list.append({'periods':period_list})
		self.final_list.append({'quarter_index':quarter_index})
		self.final_list.append({'credentials':[self.ASPXAUTH,self.studentId]})
		self.final_list.append({'message':""})
		return json.dumps(self.final_list)


def login(request):
	lol = LoginManager(request.GET['username'],request.GET['password'])
	if lol.login():
		return HttpResponse(lol.get_grade_json())
	else:
		return HttpResponse('Unauthorized', status=401)
