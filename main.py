"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
#coding=utf-8

from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
import md5
import datetime
from google.appengine.ext import db
from jinja2 import Markup


class Article(db.Model):
    name = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    media = db.StringProperty(required=True)
    fileid = db.StringProperty(required=True)
    time = db.StringProperty(required=True)
    topicid = db.StringProperty(required=True)

class Topic(db.Model):
    name = db.StringProperty(required=True)
    topicid = db.StringProperty(required=True)


app = Flask(__name__)
f=open('password.cfg')
code = f.readline().strip()
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/')
def index():

    topics = db.GqlQuery("SELECT * FROM Topic")
    
    files = []
    for f in topics:
        a = {}
        a['topicid'] = f.topicid
        a['name'] = f.name
        files.append(a)
    
    return render_template('index.html', files=files)

@app.route('/topic/<tid>')
def page(tid):

    articles = db.GqlQuery("SELECT * FROM Article WHERE topicid = "+"'"+tid+"'")

    files = []
    for f in articles:
        a = {}
        a['title'] = f.name
        a['content'] = Markup(f.content.replace(' ', '<br>'))
        a['media'] = f.media
        files.append(a)
    
    files.reverse()

    return render_template('page.html', files=files)

@app.route('/update')
def add_content():
    return render_template('update.html')

@app.route('/post', methods=['POST'])
def post_content():

    if md5.new(request.form['code']).hexdigest() != code:
    	return redirect(url_for('add_content'))

    tid = md5.new(request.form['topic']).hexdigest()
    topics = db.GqlQuery("SELECT * FROM Topic WHERE topicid = "+"'"+tid+"'")

    if not topics.fetch(10):
        
        t = Topic(name=request.form['topic'], 
        		  topicid=tid)

        t.put()

    title = request.form['title']
    time = str(datetime.datetime.now())
    fileid = md5.new(time).hexdigest()
    media = request.form['media']

    content = request.form['content']

    f = Article(name=title,
    			time=time,
    			fileid=fileid,
    			content=content,
    			media=media,
    			topicid=tid)

    f.put()

    return redirect(url_for('add_content'))


@app.route('/delete')
def delete():

    articles = db.GqlQuery("SELECT * FROM Article")

    files = []
    for f in articles:
        a = {}
        a['title'] = f.name
        a['fileid'] = f.fileid
        files.append(a)
    
    return render_template('delete.html', files=files)


@app.route('/remove', methods=['POST'])
def remove():

    if md5.new(request.form['code']).hexdigest() != code:
        return redirect(url_for('delete'))

    for f in request.form.getlist('files'):
    	f = "'" + f + "'"
        q = db.GqlQuery("SELECT * FROM Article WHERE fileid = " + f)
        db.delete(q.fetch(10))
    
    return redirect(url_for('delete'))




@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

if __name__ == '__main__':
	app.run(debug=True)