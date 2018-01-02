from models import dao
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'LJksd9u823j(*&*(23jU(Odlej09adsdfL'


@app.teardown_appcontext
def close_db(error):
    dao.get_db().close()


@app.route('/settings')
def settings():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user = dao.get_user(session['user_id'])

    return render_template('settings.html', user=user)


@app.route('/settings_save', methods=['POST'])
def settings_save():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        dao.update_settings(request.form, session['user_id'])
        flash('Save successfully')

    return redirect(url_for('settings'))


@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('start'))
    else:
        return redirect(url_for('login'))


@app.route('/start')
def start():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    categories = dao.get_categories(session['user_id'])

    return render_template('start.html', categories=categories)


@app.route('/categories')
def categories():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    categories = dao.get_categories(session['user_id'])

    return render_template('categories.html', categories=categories)


@app.route('/category_save', methods=['POST'])
def category_save():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.form['id']:
        dao.update_category(request.form, session['user_id'])
    else:
        dao.add_category(request.form, session['user_id'])

    flash('Successfully')

    return redirect(url_for('categories'))


@app.route('/category_delete/<category_id>')
def category_delete(category_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    dao.delete_category(category_id, session['user_id'])
    flash('Category deleted.')

    return redirect(url_for('categories'))


@app.route('/category_top/<category_id>')
def category_top(category_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    dao.top_category(category_id, session['user_id'])
    flash('Successfully')

    return redirect(url_for('categories'))


@app.route('/cards/<category_id>')
def cards(category_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cards = dao.get_cards(category_id, session['user_id'])

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

    dao.add_card(request.form, session['user_id'])
    flash('New card was successfully added.')

    return redirect(url_for('cards'))


@app.route('/edit/<card_id>')
def edit(card_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    card = dao.get_card(card_id, session['user_id'])

    return render_template('edit.html', card=card)


@app.route('/edit_card', methods=['POST'])
def edit_card():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    dao.update_card(request.form, session['user_id'])
    flash('Card saved.')

    return redirect(url_for('edit', card_id=request.form['card_id']))


@app.route('/delete/<card_id>')
def delete(card_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    dao.delete_card(card_id, session['user_id'])
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
        card = dao.get_card(card_id, session['user_id'])
    else:
        card = dao.get_category(category_id, session['user_id'])
    if not card:
        flash("You've learned all the " + category + " cards.")
        return redirect(url_for('cards'))
    short_answer = (len(card['back']) < 75)
    return render_template('memorize.html',
                           card=card,
                           card_type=category,
                           short_answer=short_answer)


@app.route('/mark_known/<card_id>/<card_type>')
def mark_known(card_id, card_type):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    dao.mark_known(card_id, session['user_id'])
    flash('Card marked as known.')

    return redirect(url_for(card_type))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            error = 'Email and password can not be empty'
            return render_template('login.html', error=error)

        user = dao.get_user_by_email(email)

        if not user or not dao.check_password(user['password'], password):
            error = 'Invalid email or password'
            return render_template('login.html', error=error)

        session['user_id'] = user['id']
        session['username'] = user['username']
        session['logged_in'] = True
        session.permanent = True
        flash("You've logged in")
        return redirect(url_for('categories'))

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
        elif dao.get_user_by_email(email):
            error = 'Email has already been registered'
        else:
            user = dao.add_user(email, password)
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['logged_in'] = True
            session.permanent = True
            flash('Register success')
            return redirect(url_for('cards'))

    return render_template('register.html', error=error)


def ajax_response(message, data):
    output = {"msg": message}
    output.update(data)
    jsonify(output)


"""如果直接运行本模块，则直接执行"""
if __name__ == '__main__':
    app.run(host='0.0.0.0')
