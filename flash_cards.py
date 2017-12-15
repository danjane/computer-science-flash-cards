import os
import pymysql
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from werkzeug.security import generate_password_hash, \
    check_password_hash


app = Flask(__name__)
app.debug = True
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'db', 'cards-jwasham-extreme.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('CARDS_SETTINGS', silent=True)


def init_db():
    db = get_db()
    with app.open_resource('data/schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='123456',
            port=3306,
            db='flashcards',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.mysql_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'mysql_db'):
        g.mysql_db.close()


# -----------------------------------------------------------

# Uncomment and use this to initialize database, then comment it
#   You can rerun it to pave the database and start over
@app.route('/initdb')
def initdb():
    init_db()
    return 'Initialized the database.'


@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('general'))
    else:
        return redirect(url_for('login'))


@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    with get_db().cursor() as cursor:
        query = '''
            SELECT id as cid, name, top, (
                SELECT count(*) FROM cards WHERE category_id = cid) as count
            FROM categories
            WHERE user_id=%s
            ORDER BY top DESC, update_time DESC
        '''
        cursor.execute(query, [session['user_id']])
        categories = cursor.fetchall()

    return render_template('categories.html', categories=categories)


@app.route('/category_post', methods=['POST'])
def category_post():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    category_id = int(request.form['id'])

    with get_db().cursor() as cursor:
        if category_id:
            cursor.execute('UPDATE categories SET name = %s WHERE id = %s AND user_id = %s', [
                request.form['name'],
                category_id,
                session['user_id']
            ])
        else:
            cursor.execute('INSERT INTO categories (name, user_id) VALUES (%s, %s)', [
                request.form['name'],
                session['user_id']
            ])
        get_db().commit()
        flash('Successfully')

        return redirect(url_for('categories'))


@app.route('/category_delete/<category_id>')
def category_delete(category_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    with get_db().cursor() as cursor:
        cursor.execute('DELETE FROM categories WHERE id = %s AND user_id = %s', [category_id, session['user_id']])
        get_db().commit()
        cursor.execute('DELETE FROM cards WHERE category_id = %s AND user_id = %s', [category_id, session['user_id']])
        get_db().commit()
        flash('Category deleted.')

    return redirect(url_for('categories'))


@app.route('/category_top/<category_id>')
def category_top(category_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    with get_db().cursor() as cursor:
        cursor.execute('UPDATE categories SET top = 1-top WHERE id = %s AND user_id = %s', [
            category_id,
            session['user_id']
        ])
        get_db().commit()
        flash('Successfully')

        return redirect(url_for('categories'))


@app.route('/cards')
def cards():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    with get_db().cursor() as cursor:
        query = '''
            SELECT id, category_id, front, back, known
            FROM cards
            WHERE user_id = %s
            ORDER BY id DESC
        '''
        cursor.execute(query, [session['user_id']])
        cards = cursor.fetchall()

    return render_template('cards.html', cards=cards)


@app.route('/add')
def add():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('add.html')


@app.route('/add_card', methods=['POST'])
def add_card():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    with get_db().cursor() as cursor:
        cursor.execute('INSERT INTO cards (category_id, front, back, user_id) VALUES (%s, %s, %s)', [
            request.form['category_id'],
            request.form['front'],
            request.form['back'],
            session['user_id']
        ])
        get_db().commit()
        flash('New card was successfully added.')

        return redirect(url_for('cards'))


@app.route('/edit/<card_id>')
def edit(card_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    with get_db().cursor() as cursor:
        query = '''
            SELECT id, category_id, front, back, known
            FROM cards
            WHERE id = %s AND user_id = %s
        '''
        cursor.execute(query, [card_id, session['user_id']])
        card = cursor.fetchone()

    return render_template('edit.html', card=card)


@app.route('/edit_card', methods=['POST'])
def edit_card():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    selected = request.form.getlist('known')
    known = bool(selected)

    with get_db().cursor() as cursor:
        command = '''
            UPDATE cards
            SET
              category_id = %s,
              front = %s,
              back = %s,
              known = %s
            WHERE id = %s
            AND user_id = %s
        '''
        cursor.execute(
            command,
            [
                request.form['category_id'],
                request.form['front'],
                request.form['back'],
                known,
                request.form['card_id'],
                session['user_id']
            ]
        )
        get_db().commit()
        flash('Card saved.')

        return redirect(url_for('edit', card_id=request.form['card_id']))


@app.route('/delete/<card_id>')
def delete(card_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    with get_db().cursor() as cursor:
        cursor.execute('DELETE FROM cards WHERE id = %s AND user_id = %s', [card_id, session['user_id']])
        get_db().commit()
        flash('Card deleted.')

    return redirect(url_for('cards'))


@app.route('/general')
@app.route('/general/<card_id>')
def general(card_id=None):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return memorize("general", card_id)


@app.route('/code')
@app.route('/code/<card_id>')
def code(card_id=None):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return memorize("code", card_id)


def memorize(category, card_id):
    if category == "general":
        category_id = 1
    elif category == "code":
        category_id = 2
    else:
        return redirect(url_for('cards'))

    if card_id:
        card = get_card_by_id(card_id)
    else:
        card = get_card_by_category_id(category_id)
    if not card:
        flash("You've learned all the " + category + " cards.")
        return redirect(url_for('cards'))
    short_answer = (len(card['back']) < 75)
    return render_template('memorize.html',
                           card=card,
                           card_type=category,
                           short_answer=short_answer)


def get_card_by_category_id(category_id):
    with get_db().cursor() as cursor:
        query = '''
          SELECT
            id, category_id, front, back, known
          FROM cards
          WHERE
            category_id = %s
            AND user_id = %s
            AND known = 0
          LIMIT 1
        '''
        cursor.execute(query, [category_id, session['user_id']])
        return cursor.fetchone()


def get_card_by_id(card_id):
    with get_db().cursor() as cursor:
        query = '''
          SELECT
            id, category_id, front, back, known
          FROM cards
          WHERE id = %s AND user_id = %s
          LIMIT 1
        '''

        cursor.execute(query, [card_id, session['user_id']])
        return cursor.fetchone()


@app.route('/mark_known/<card_id>/<card_type>')
def mark_known(card_id, card_type):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    with get_db() as cursor:
        cursor.execute('UPDATE cards SET known = 1 WHERE id = %s AND user_id = %s', [card_id, session['user_id']])
        get_db().commit()
        flash('Card marked as known.')

    return redirect(url_for(card_type))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            error = 'Email and Password can not be empty'
            return render_template('login.html', error=error)

        user = get_user_by_email(email)

        if not user or not check_password_hash(user['password'], password):
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

        session['user_id'] = user['id']
        session['username'] = user['username']
        session['logged_in'] = True
        session.permanent = True
        flash("You've logged in")
        return redirect(url_for('cards'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('logged_in', None)
    flash("You've logged out")
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'Post'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if not email or not password:
            error = 'Email and Password can not be empty'
        elif get_user_by_email(email):
            error = 'Email has already been registered'
        else:
            user = add_user(email, password)
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['logged_in'] = True
            session.permanent = True
            flash('Register success')
            return redirect(url_for('cards'))

    return render_template('register.html', error=error)


def get_user_by_email(email):
    with get_db().cursor() as cursor:
        query = '''
            SELECT id, username, email, password FROM users
            WHERE email = %s
            LIMIT 1
        '''
        cursor.execute(query, [email])
        return cursor.fetchone()


def add_user(email, password):
    username = email.partition('@')[0]
    pw_hash = generate_password_hash(password)

    with get_db().cursor() as cursor:
        query = '''
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
        '''
        cursor.execute(query, [username, email, pw_hash])
        get_db().commit()

        return {id: cursor.lastrowid, username: username}


"""如果直接运行本模块，则直接执行"""
if __name__ == '__main__':
    app.run(host='0.0.0.0')
