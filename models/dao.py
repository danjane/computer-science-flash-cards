#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import os
from configparser import ConfigParser
from flask import g
from werkzeug.security import generate_password_hash, \
    check_password_hash


def get_db():
    if not hasattr(g, 'mysql_db'):
        config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../config.ini')

        config = ConfigParser()
        if not config.read(config_file):
            raise Exception('cannot found config.ini')

        g.mysql_db = pymysql.connect(
            host=config.get('db', 'host'),
            user=config.get('db', 'username'),
            password=config.get('db', 'password'),
            port=config.getint('db', 'port'),
            db=config.get('db', 'dbname'),
            charset=config.get('db', 'charset'),
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.mysql_db


def get_user(user_id):
    with get_db().cursor() as cursor:
        query = 'SELECT username, email, display_mode FROM users where id = %s LIMIT 1'
        cursor.execute(query, user_id)

    return cursor.fetchone()


def get_categories(user_id):
    with get_db().cursor() as cursor:
        query = '''
            SELECT user_id as uid, id as cid, name, top, (
                SELECT count(*) FROM cards WHERE user_id = uid AND category_id = cid) as count
            FROM categories
            WHERE user_id=%s
            ORDER BY top DESC, update_time DESC
        '''
        cursor.execute(query, [user_id])
        return cursor.fetchall()


def delete_categories(category_id, user_id):
    with get_db().cursor() as cursor:
        cursor.execute('DELETE FROM categories WHERE id = %s AND user_id = %s', [category_id, user_id])
        get_db().commit()
        cursor.execute('DELETE FROM cards WHERE category_id = %s AND user_id = %s', [category_id, user_id])
        get_db().commit()


def top_category(category_id, user_id):
    with get_db().cursor() as cursor:
        cursor.execute('UPDATE categories SET top = 1-top WHERE id = %s AND user_id = %s', [
            category_id,
            user_id
        ])
        get_db().commit()


def get_cards(category_id, user_id):
    with get_db().cursor() as cursor:
        query = '''
            SELECT id, category_id, front, back, known
            FROM cards
            WHERE category_id = %s AND user_id = %s
            ORDER BY id DESC
        '''
        cursor.execute(query, [category_id, user_id])
        return cursor.fetchall()


def add_card(form, user_id):
    with get_db().cursor() as cursor:
        cursor.execute('INSERT INTO cards (category_id, front, back, user_id) VALUES (%s, %s, %s)', [
            form['category_id'],
            form['front'],
            form['back'],
            user_id
        ])
        get_db().commit()


def get_card_by_category_id(category_id, user_id):
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
        cursor.execute(query, [category_id, user_id])
        return cursor.fetchone()


def get_card_by_id(card_id, user_id):
    with get_db().cursor() as cursor:
        query = '''
          SELECT
            id, category_id, front, back, known
          FROM cards
          WHERE id = %s AND user_id = %s
          LIMIT 1
        '''

        cursor.execute(query, [card_id, user_id])
        return cursor.fetchone()


def mark_known(card_id, user_id):
    with get_db() as cursor:
        cursor.execute('UPDATE cards SET known = 1 WHERE id = %s AND user_id = %s', [card_id, user_id])
        get_db().commit()


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

