import sqlite3
import logging
import os
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    app.config['db_count'] += 1
    return connection

def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

app = Flask(__name__)
app.config['SECRET_KEY'] = '2660973556'
app.config['db_count']=0
 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      
      app.logger.error("The post cannot be found")

      return render_template('404.html'), 404
    
    else:
      
      app.logger.info('Article "{title}" retrieved!'.format(title=post['title']))
      return render_template('post.html', post=post)

@app.route('/about')
def about():
    app.logger.info("About page is retrived")
    return render_template('about.html')

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            app.logger.info(f"Article. title:{title} is retrieved!")

            return redirect(url_for('index'))
    
    return render_template('create.html')


@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    return response

@app.route('/metrics')
def metrics():

    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    posts_count = len(posts)
    connection.close()
    
    response = app.response_class(
            response=json.dumps({"data":{"db_connection_count": app.config['db_count'], "post_count": posts_count}}),
            status=200,
            mimetype='application/json'
    )

    return response

if __name__ == "__main__":
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    
    format_output = '%(asctime)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(format=format_output, level=logging.DEBUG, handlers=[stderr_handler, stdout_handler])
    
    app.run(host='0.0.0.0', port='3111', debug=False)