from django.http import HttpResponse
import requests
from BeautifulSoup import BeautifulSoup
import json

def grade(request):
	enroll_id = request.GET['enroll_id']
	term_id = request.GET['term_id']
	student_id = request.GET['student_id']
	aspx_auth = request.GET['aspx']
	lol = GradeManager(enroll_id,term_id,student_id,aspx_auth)
	return HttpResponse(lol.get_grade_json())

class GradeManager(object):
	def __init__(self,enrollment_id,term_id,student_id,aspx_auth):
		self.enrollment_id = enrollment_id
		self.term_id = term_id
		self.student_id = student_id
		self.aspx_auth = aspx_auth
		
		self.url = 'https://loudoun.gradebook.net/clarity/Gradebook/InternetViewer/StudentAssignments.aspx?'\
					'EnrollmentId=%s&TermId=%s&StudentId=%s'% (self.enrollment_id,self.term_id,self.student_id)
	def get_grade_json(self):
		cookies = {'PinnacleWeb.ASPXAUTH':self.aspx_auth}
		r = requests.get(self.url,cookies = cookies)
		soup = BeautifulSoup(r.content)
		grade_table = soup.find('table',{'id' : 'Assignments'}).find('tbody').findAll('tr')
		grade_list = []
		for grade in grade_table:
			grade_title = grade.find('td').text
			grade_text =  grade.findAll('td',{'class' : 'grade'})
			grade_score = '%s/%s(%s)' % (grade_text[0].text,grade_text[1].text.split('.')[0],grade_text[2].text)
			grade_list.append([{'assignment_name':grade_title},{'score':grade_score}])

		
		return json.dumps(grade_list)
