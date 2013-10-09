from django.conf.urls import patterns, include, url


from clarity import login
from clarity import grade

urlpatterns = patterns('',
    url(r'^clarity/login', login.login, name='login'),
	url(r'^clarity/grade', grade.grade, name='grade'),	
 )
