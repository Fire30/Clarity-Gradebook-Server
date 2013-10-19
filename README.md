Clarity Gradebook Server
=============

This is a simple python implentation that is able to parse the html from loudoun county's online gradebook and return relevant JSON. It uses the django web framework. I use this in my clarity viewer android app, and my iOS app will soon be updated to include it also.

Prerequisites
=============
-Python 2.7.x

-Django 1.5.1

-Requests 2.x

-Beautiful Soup

Usage
==============
To acess the JSON for every class and their total grades the formed url would be:
www.site.com/clarity/login?username=xxxpassword=xxx

to acess JSON for individual grades for a certain class the url would be:
http://site.com/clarity/grade?enroll_id=xxx&term_id=xxx&student_id=xxx&aspx=xxx
Obviously subsituting the the xxx's for their respective parameters

LICENSE
==============

The MIT License (MIT)

Copyright (c) <2013> <TJ Corley>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
