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

    user = dao.get_user()

    return render_template('settings.html', user=user)


@app.route('/settings_save', methods=['POST'])
def settings_save():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        dao.update_settings(request.form)
        flash('Save successfully')

    return redirect(url_for('settings'))


@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('start'))
    else:
        return redirect(url_for('login'))


@app.route('/categories')
def categories():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    categories = dao.get_categories()

    return render_template('categories.html', categories=categories)


@app.route('/category/<category_id>')
def category(category_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cards = dao.get_cards(category_id)

    return render_template('category.html', cards=cards, category_id=category_id)


@app.route('/category_save', methods=['POST'])
def category_save():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.form['id']:
        dao.update_category(request.form)
    else:
        dao.add_category(request.form)

    flash('Successfully')

    return redirect(url_for('categories'))


@app.route('/category_delete/<category_id>')
def category_delete(category_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    dao.delete_category(category_id)
    flash('Category deleted.')

    return redirect(url_for('categories'))


@app.route('/category_top/<category_id>')
def category_top(category_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    dao.top_category(category_id)
    flash('Successfully')

    return redirect(url_for('categories'))


@app.route('/start')
@app.route('/start/<category_id>')
def start(category_id=''):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cards = categories = {}

    if category_id:
        cards = dao.get_cards(category_id)
    else:
        categories = dao.get_categories()

    return render_template('start.html', cards=cards, category_id=category_id, categories=categories)


@app.route('/manage/<category_id>')
@app.route('/manage/<category_id>/<card_id>')
def manage(category_id, card_id=0):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    categories = dao.get_categories()

    card = {}
    if card_id:
        card = dao.get_card(card_id)
        card['eid'] = card_id

    return render_template('manage.html', card=card, category_id=category_id, categories=categories)


@app.route('/card_save', methods=['POST'])
def card_save():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.form['card_id']:
        dao.update_card(request.form)
        card_id = request.form['card_id']
        flash('Updated.')
    else:
        card_id = dao.add_card(request.form)
        flash('Added.')

    return redirect(url_for('manage', category_id=request.form['category_id'], card_id=card_id))


@app.route('/delete/<category_id>/<card_id>')
def delete(category_id, card_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    dao.delete_card(card_id)
    flash('Card deleted.')

    return redirect(url_for('category', category_id=category_id))


@app.route('/mark_known', methods=['POST'])
def mark_known():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    card_id = request.form['card_id']
    card = dao.get_card(card_id)

    dao.mark_known(card_id)

    return redirect(url_for('start', category_id=card['category_eid'], _anchor=card_id))


@app.route('/plans')
def plans():
    plans = dao.get_plans()

    tree = []
    for item in plans:
        if not item['parent_id']:
            tree.append(create_tree(item, plans))

    return render_template('plans.html', plans=render_plans(tree))


def create_tree(parent, plans):
    parent['children'] = []
    for item in plans:
        if item['parent_id'] == parent['id']:
            parent['children'].append(create_tree(item, plans))

    return parent


def render_plans(plans):
    html = '<ul>'
    for plan in plans:
        check_url = url_for('plan_check', plan_id=plan['eid'], finish='')
        save_url = url_for('plan_save', plan_id=plan['eid'])
        checked = ' checked' if plan['finish'] else ''

        html += '<li><div class="plan-item">'
        html += '<label><input type="checkbox" class="plan-check"{} name=plan[] value="{}" /></label> '\
                .format(checked, check_url)
        html += '<span class="plan-title" data-url="{}">{}</span>'.format(save_url, plan['title'])
        html += '</div>'
        if plan['children']:
            html += render_plans(plan['children'])
        html += '</li>'

    html += '</ul>'

    return html


@app.route('/plan_save/<plan_id>', methods=['POST'])
def plan_save(plan_id):
    form = {"title": request.form['title'], "plan_id": plan_id}
    result = dao.plan_update(form)

    return ajax_response({"status": result})


@app.route('/plan_add', methods=['POST'])
def plan_add():
    parent_ids = request.form.getlist('parent_ids[]')
    titles = request.form.getlist('titles[]')
    result = dao.plans_add(parent_ids, titles)

    return ajax_response({"status": result})


@app.route('/plan_delete/<plan_id>')
def plan_delete(plan_id):
    result = dao.plan_delete(plan_id)

    return ajax_response({"status": result})


@app.route('/plan_check/<plan_id>/<finish>')
def plan_check(plan_id, finish):
    form = {"id": plan_id, 'finish': finish}
    result = dao.update_plans_status(form)

    if not result:
        finish = dao.get_plan_finish(plan_id)

    return ajax_response({"finish": finish})


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


def ajax_response(data):
    return jsonify(data)


"""如果直接运行本模块，则直接执行"""
if __name__ == '__main__':
    app.run(host='0.0.0.0')
