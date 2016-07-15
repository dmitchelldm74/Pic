from flask import Flask, redirect, url_for, render_template, request, Response, session
from werkzeug import secure_filename
import sqlite3, uuid, datetime
from post import Post
app = Flask(__name__)
app.config['SECRET_KEY'] = open('SECRET_KEY', 'r').read().split('\n')[0]
IMAGES = tuple('jpg jpe jpeg png gif svg bmp ico, JPG, PNG'.split())
headers = """"""
@app.route('/')
def home():
    if "user" in session:
        conn = sqlite3.connect('database')
        c = conn.cursor()
        data = ""
        DONE = []
        a = list(c.execute("SELECT * FROM viewers f, posts p WHERE f.owner = p.owner AND f.viewer = ? ORDER BY p.timestamp;", (session['user'],)))
        for u in a:
            if u[5] not in DONE:
                liked = False
                likes = 0
                for a in c.execute('SELECT * FROM likes WHERE id=?', (u[5],)):
                    if a[1] == session['user']:
                        liked = True
                    likes += 1
                print data
                data = render_template('one.html', data={'likes':str(likes), 'liked':liked, 'id':u[5], 'time':u[6], 'user':u[0], 'des':u[4], 'img':url_for('uploads', fname=u[3]), "delete":url_for('delete', post_id=u[5])}) + data
                DONE.append(u[5])
        conn.close()
        return render_template('posts.html', headers=headers, data=data)
    return render_template('account.html', headers=headers)
@app.route('/delete/<post_id>')
def delete(post_id):
    if "user" in session:
        conn = sqlite3.connect('database')
        c = conn.cursor()
        c.execute('DELETE FROM posts WHERE id=? AND owner=?', (post_id, session["user"]))
        conn.commit()
        conn.close()
    return redirect('/')
@app.route('/+viewer', methods=['POST'])
def viewer():
    if 'user' in session:
        Post('viewers', (session['user'], request.form['user']))
    return redirect('/')
@app.route('/s/<user>')
def sug(user):
    conn = sqlite3.connect('database')
    c = conn.cursor()
    q = '%' + user + '%'
    a = list(c.execute('SELECT user FROM users WHERE user LIKE ?', (q,)))
    conn.close()
    return render_template('s.html', a=a)
@app.route('/like/<ID>')
def like(ID):
    if 'user' in session:
        conn = sqlite3.connect('database')
        c = conn.cursor()
        u = session['user']
        do = True
        for i in c.execute('SELECT * FROM likes WHERE id=? AND liker=?', (ID, u)):
            do = False
        if do == True:
            Post('likes', (ID, u))
        conn.close()
    return redirect('/#' + ID)
@app.route('/dislike/<ID>')
def dislike(ID):
    if 'user' in session:
        conn = sqlite3.connect('database')
        c = conn.cursor()
        u = session['user']
        c.execute('DELETE FROM likes WHERE id=? AND liker=?', (ID, u))
        conn.commit()
        conn.close()
    return redirect('/#' + ID)
@app.route('/uploads/<fname>')
def uploads(fname):
    return Response(open('uploads/' + fname, 'r').read(), mimetype="text/plain")
@app.route('/fonts/<fname>')
def fonts(fname):
    return Response(open('fonts/' + fname, 'r').read(), mimetype="text/plain")
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'user' in session:
        f = request.files['file']
        des = request.form['des']
        user = session['user']
        ID = str(uuid.uuid4())
        fname = ID + f.filename
        timestamp = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        Post('posts', (user, fname, des, ID, timestamp))
        if "." in f.filename:
            if f.filename.rsplit('.')[1] in IMAGES:
                f.save('uploads/' + secure_filename(fname))
                #return Response(open('uploads/' + fname, 'r').read(), mimetype="text/plain")
    return redirect('/')
@app.route('/in.pop')
def in_pop():
    session.pop('user', None)
    return redirect('/')
@app.route('/post')
def post():
    return render_template('post.html', headers=headers)
@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        conn = sqlite3.connect('database')
        c = conn.cursor()
        user = request.form['user']
        ps = request.form['ps']
        for u in c.execute('SELECT * FROM users WHERE user=?', (user,)):
            conn.close()
            if ps == u[1]:
                session['user'] = user
                session['ps'] = ps
            return redirect('/')
        session['user'] = user
        session['ps'] = ps
        Post('viewers', (user, user))
        c.execute("INSERT INTO users VALUES (?, ?)", (user, ps))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('account.html', headers=headers)
if __name__ == '__main__':
    app.run(port=8765, debug=True, host='0.0.0.0')
