#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import os
from hashids import Hashids
from configparser import ConfigParser
from flask import g, session
from werkzeug.security import generate_password_hash, \
    check_password_hash


def config():
    if not hasattr(g, 'config'):
        config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../config.ini')

        cp = ConfigParser()
        if not cp.read(config_file):
            raise Exception('cannot found config.ini')
        g.config = cp

    return g.config


def get_db():
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = pymysql.connect(
            host=config().get('db', 'host'),
            user=config().get('db', 'username'),
            password=config().get('db', 'password'),
            port=config().getint('db', 'port'),
            db=config().get('db', 'dbname'),
            charset=config().get('db', 'charset'),
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.mysql_db


def user_id():
    try:
        if session['user_id']:
            return session['user_id']
    except NameError:
        print("You did not sign in.")


def encode_id(id):
    hashids = Hashids(
        min_length=config().get('safe', 'hashids_length'),
        salt=config().get('safe', 'hashids_salt'),
        alphabet=config().get('safe', 'hashids_alphabet')
    )
    return hashids.encode(id)


def decode_id(hashstr):
    hashids = Hashids(
        min_length=config().get('safe', 'hashids_length'),
        salt=config().get('safe', 'hashids_salt'),
        alphabet=config().get('safe', 'hashids_alphabet')
    )
    return hashids.decode(hashstr)[0]


def get_user():
    with get_db().cursor() as cursor:
        query = 'SELECT username, email, display_mode FROM users where id = %s LIMIT 1'
        cursor.execute(query, user_id())

    return cursor.fetchone()


def get_categories():
    with get_db().cursor() as cursor:
        query = '''
            SELECT user_id as uid, id as cid, name, top, (
                SELECT count(*) FROM cards WHERE user_id = uid AND category_id = cid) as count
            FROM categories
            WHERE user_id=%s
            ORDER BY top DESC, update_time DESC
        '''
        cursor.execute(query, [user_id()])
        return append_encode_id(cursor.fetchall(), 'cid')


def delete_category(category_id):
    category_id = decode_id(category_id)
    with get_db().cursor() as cursor:
        cursor.execute('DELETE FROM categories WHERE id = %s AND user_id = %s', [category_id, user_id()])
        get_db().commit()
        cursor.execute('DELETE FROM cards WHERE category_id = %s AND user_id = %s', [category_id, user_id()])
        get_db().commit()


def top_category(category_id):
    category_id = decode_id(category_id)
    with get_db().cursor() as cursor:
        cursor.execute('UPDATE categories SET top = 1-top WHERE id = %s AND user_id = %s', [
            category_id,
            user_id()
        ])
        get_db().commit()


def get_card(card_id):
    card_id = decode_id(card_id)
    with get_db().cursor() as cursor:
        query = '''
            SELECT id, category_id, front, back, known
            FROM cards
            WHERE id = %s AND user_id = %s
            LIMIT 1
        '''
        cursor.execute(query, [card_id, user_id()])
        card = cursor.fetchone()

        if card:
            card['category_eid'] = encode_id(card['category_id'])

        return card


def get_cards(category_id):
    category_id = decode_id(category_id)
    with get_db().cursor() as cursor:
        query = '''
            SELECT id, category_id, front, back, known
            FROM cards
            WHERE category_id = %s AND user_id = %s
            ORDER BY id DESC
        '''
        cursor.execute(query, [category_id, user_id()])
        cards = append_encode_id(cursor.fetchall())
        return replace_wrap(cards)


def add_card(form):
    with get_db().cursor() as cursor:
        cursor.execute('INSERT INTO cards (category_id, front, back, user_id) VALUES (%s, %s, %s, %s)', [
            decode_id(form['category_id']),
            form['front'],
            form['back'],
            user_id()
        ])
        get_db().commit()
        return encode_id(cursor.lastrowid)


def update_card(form):
    category_id = decode_id(form['category_id'])
    card_id = decode_id(form['card_id'])

    with get_db().cursor() as cursor:
        query = '''
            UPDATE cards
            SET
              category_id = %s,
              front = %s,
              back = %s
            WHERE id = %s
            AND user_id = %s
        '''
        cursor.execute(
            query,
            [
                category_id,
                form['front'],
                form['back'],
                card_id,
                user_id()
            ]
        )
        get_db().commit()


def delete_card(card_id):
    card_id = decode_id(card_id)
    with get_db().cursor() as cursor:
        cursor.execute('DELETE FROM cards WHERE id = %s AND user_id = %s', [card_id, user_id()])
        get_db().commit()


def add_category(form):
    with get_db().cursor() as cursor:
        cursor.execute('INSERT INTO categories (name, user_id) VALUES (%s, %s)', [
            form['name'],
            user_id()
        ])
        get_db().commit()


def update_category(form):
    category_id = decode_id(form['id'])
    with get_db().cursor() as cursor:
        cursor.execute('UPDATE categories SET name = %s WHERE id = %s AND user_id = %s', [
            form['name'],
            category_id,
            user_id()
        ])
        get_db().commit()


def mark_known(card_id):
    card_id = decode_id(card_id)
    with get_db() as cursor:
        cursor.execute('UPDATE cards SET known = 1 - known WHERE id = %s AND user_id = %s', [card_id, user_id()])
        get_db().commit()

        return cursor.rowcount


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

        return {"id": cursor.lastrowid, "username": username}


def get_password(input_password):
    return generate_password_hash(input_password)


def check_password(store_password, input_password):
    return check_password_hash(store_password, input_password)


def update_settings(form):
    with get_db().cursor() as cursor:
        if form['password']:
            query = 'UPDATE users SET username = %s, email = %s, password = %s, display_mode = %s WHERE id = %s'
            cursor.execute(query, [
                form['username'],
                form['email'],
                get_password(form['password']),
                form['display_mode'],
                user_id()
            ])
        else:
            query = 'UPDATE users SET username = %s, email = %s, display_mode = %s WHERE id = %s'
            cursor.execute(query, [
                form['username'],
                form['email'],
                form['display_mode'],
                user_id()
            ])
    get_db().commit()


def get_plans():
    with get_db().cursor() as cursor:
        query = 'SELECT id, parent_id, title, finish FROM plans WHERE user_id = %s'
        cursor.execute(query, [user_id()])
        plans = cursor.fetchall()
        return append_encode_id(plans)


def plans_add(parent_ids, titles):
    """
    批量插入plan
    """
    parent_ids = list(map(decode_id, parent_ids))
    user_ids = [user_id()] * len(parent_ids)
    values = list(zip(titles, parent_ids, user_ids))

    with get_db().cursor() as cursor:
        query = 'INSERT INTO plans (title, parent_id, user_id) VALUES (%s, %s, %s)'
        cursor.executemany(query, values)
        get_db().commit()

        return cursor.rowcount


def plan_add(form):
    """
    插入一条plan
    """
    last = len(form) - 1
    form[last] = decode_id(form[len(form) - 1])
    form.append(user_id())
    with get_db().cursor() as cursor:
        query = 'INSERT INTO plans (title, parent_id, user_id) VALUES (%s, %s, %s)'
        cursor.execute(query, form)
        get_db().commit()

        return cursor.rowcount


def plan_update(form):
    """
    更新一条plan
    """
    last = len(form) - 1
    form[last] = decode_id(form[len(form) - 1])
    form.append(user_id())
    with get_db().cursor() as cursor:
        cursor.execute('UPDATE plans SET title = %s WHERE id = %s AND user_id = %s', form)
        get_db().commit()

        return cursor.rowcount


def plan_delete(plan_id):
    plan_id = decode_id(plan_id)
    with get_db().cursor() as cursor:
        query = 'DELETE FROM plans WHERE (id = %s OR parent_id = %s) AND user_id = %s'
        cursor.execute(query, [plan_id, plan_id, user_id()])
        get_db().commit()

        return cursor.rowcount


def update_plans_status(form):
    plan_id = decode_id(form['id'])
    with get_db().cursor() as cursor:
        cursor.execute('UPDATE plans SET finish = %s WHERE id = %s AND user_id = %s', [
            form['finish'],
            plan_id,
            user_id()
        ])
        get_db().commit()
        return cursor.rowcount


def get_plan_finish(plan_id):
    id = decode_id(plan_id)
    with get_db().cursor() as cursor:
        query = 'SELECT finish FROM plans WHERE id = %s AND user_id = %s'
        cursor.execute(query, [id, user_id()])
        plan = cursor.fetchone()
        return plan['finish']


def replace_wrap(values):
    for key, value in enumerate(values):
        values[key]['back'] = values[key]['back'].replace('\n', '<br />')

    return values


def append_encode_id(values, column='id'):
    """
    :param values: 数据中读取出来的内容集合
    :param column: 要加密的列，默认‘id’列
    :return: 返回加密后的内容集合
    """
    for key, value in enumerate(values):
        values[key]['eid'] = encode_id(value[column])

    return values
