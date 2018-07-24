from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from palmtree.auth import login_required
from palmtree.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username, likes, dislikes'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    comments = db.execute(
	    'SELECT c.id, post_id, author_id, created, comment, likes, dislikes, username'
		' FROM comment c JOIN user u ON c.author_id = u.id'
		' ORDER BY created'
	).fetchall()
    return render_template('blog/index.html', posts=posts, comments=comments)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, likes, dislikes)'
                ' VALUES (?, ?, ?, 0, 0)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

@bp.route('/<int:post_id>/comment', methods=('POST',))
def comment(post_id):
	comment = request.form['comment']
	error = None

	if not comment:
		error = 'Comment is required.'

	if error is not None:
		flash(error)
	else:
		db = get_db()
		db.execute(
			'INSERT INTO comment (post_id, author_id, comment, likes, dislikes)'
			' VALUES (?, ?, ?, 0, 0)',
			(post_id, g.user['id'], comment)
		)
		db.commit()
		return redirect(url_for('blog.index'))

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username, likes, dislikes'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/view')
def view(id):
	post = get_post(id,False)
	return render_template('blog/view.html',post=post)

@bp.route('/<int:id>/statuspost', methods=('POST',))
def statuspost(id):
	db = get_db()
	if request.form['status'] == 'Like':
		db.execute(
			'UPDATE post SET likes = likes+1 WHERE id = ?', (id,))
	elif request.form['status'] == 'Dislike':
		db.execute(
			'UPDATE post SET dislikes = dislikes+1 WHERE id = ?', (id,))
	else:
		flash('Unknown status.')
	db.commit()
	return redirect(url_for('blog.index'))

@bp.route('/<int:id>/statuscomment', methods=('POST',))
def statuscomment(id):
	db = get_db()
	if request.form['status'] == 'Like':
		db.execute(
			'UPDATE comment SET likes = likes+1 WHERE id = ?', (id,))
	elif request.form['status'] == 'Dislike':
		db.execute(
			'UPDATE comment SET dislikes = dislikes+1 WHERE id = ?', (id,))
	else:
		flash('Unknown status.')
	db.commit()
	return redirect(url_for('blog.index'))

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
