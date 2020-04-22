import os
import random
import string
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from psrPlatform import app, db, bcrypt
from psrPlatform.forms import RegistrationForm, LoginForm, RateForm, PicForm
from psrPlatform.models import Users, Products, Ratings
from psrPlatform import SVDpp_val, user_knn, user_pool
from psrPlatform import get_similar_users, get_top_N_recommended_items
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import pickle
import numpy as np
import tensorflow as tf
from keras.preprocessing import image
from keras.models import load_model
from keras.backend import clear_session, set_session
from datetime import timedelta

## load the deep learning model
label2idx = pickle.load(open('./psrPlatform/img_model/img_label2idx.pkl', 'rb'))
idx2label = {i:j for j, i in label2idx.items()}
sess = tf.Session()
graph = tf.get_default_graph()
set_session(sess)
model = load_model("./psrPlatform/img_model/model_47000img_identification.h5") 

def gen_reviewerID(stringLength=14):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength))).upper()    

# default page
@app.route("/")
@app.route("/default")
def default():
    return render_template('default.html')

# home page
@app.route("/home")
@login_required
def home():
    user = Users.query.filter_by(reviewerName=current_user.reviewerName).first_or_404()
    return render_template('home.html', username=user.reviewerName)


@app.route("/games_by_p/<string:price_choose>")
@login_required
def games_by_p(price_choose):
    page = request.args.get('page', 1, type=int)
    price_choose_int = int(price_choose)
    games = Products.query.filter(Products.price < price_choose_int).paginate(page=page, per_page=5)
    return render_template('games_list.html', games=games, price_choose=price_choose)

@app.route("/games_by_pic ", methods=['GET', 'POST'])
@login_required
def games_by_pic():
    form = PicForm()
    if form.validate_on_submit():
        games_pre = pre_picture(form.picture.data)
        games_found = [Products.query.filter_by(asin = i).first() for i in games_pre]
        games_found = [i for i in games_found if i is not None]
        if games_found:
            return render_template('games_list_pic.html', games = games_found)
        else: 
            flash('Whoops. Unable to find the image due to no record in database. Try another one.', 'danger')
    return render_template('search_by_pic.html', form=form, legend='Search by Picture')

@app.route("/recommended_games")
@login_required
def recommended_games():
    user = Users.query.filter_by(reviewerName=current_user.reviewerName).first_or_404()
    userId = Users.query.filter_by(reviewerName=current_user.reviewerName).first().reviewerID
    print(userId)
    if userId not in user_pool:
        userId = random.sample(user_pool, 1)[0]
    recom_games = get_top_N_recommended_items(userId)
    games_found = [Products.query.filter_by(asin = i).first() for i in recom_games]
    games_found = [i for i in games_found if i is not None]
    if games_found :
        return render_template('recommended_games.html', games = games_found)
    else:
        flash('Unable to recommend. Rate more games would help the system learn!', 'danger')
    return render_template('home.html', username=user.reviewerName)



@app.route("/games/<string:game_id>")
@login_required
def game_detail(game_id):
    game = Products.query.filter_by(asin = game_id).first_or_404()
    page = request.args.get('page', 1, type=int)
    rates = Ratings.query.filter_by(asin = game_id).order_by(Ratings.reviewTime.desc())\
        .paginate(page=page, per_page=5)
    return render_template('game_detail.html', game = game, rates = rates)

@app.route("/rate/new", methods=['GET', 'POST'])
@login_required
def create_post():
    form = RateForm()
    if form.validate_on_submit():
        game = Products.query.filter_by(asin = form.game_id.data).first()
        #print(game.asin)
        rate = Ratings(product=game,
                        reviewerName = current_user.reviewerName,
                        reviewText=form.comment.data,
                        summary = form.summary.data,
                        rating = int(form.score.data),
                        author=current_user)
        db.session.add(rate)
        db.session.commit()
        flash('Your rate has been submitted!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Rate',
                           form=form, legend='New Rate')

@app.route("/user_rates")
@login_required
def user_rates():
    page = request.args.get('page', 1, type=int)
    rates = Ratings.query.filter_by(author=current_user)\
        .order_by(Ratings.reviewTime.desc())\
        .paginate(page=page, per_page=5)
    username=current_user.reviewerName
    return render_template('user_rates.html', rates=rates, username=username)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        while True:
            new_reviewerID = gen_reviewerID()
            if not Users.query.get(new_reviewerID):
                break
        user = Users(reviewerID = new_reviewerID, reviewerName=form.username.data, reviewerPW=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(reviewerName=form.username.data).first()
        if user and bcrypt.check_password_hash(user.reviewerPW, form.password.data):
            login_user(user,duration = timedelta(minutes=5))
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check account and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('default'))


def save_picture(form_picture):
    picture_path = os.path.join(app.root_path, 'static/profile_pics', form_picture.filename)
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_path


def pre_picture(form_picture):
    img = Image.open(form_picture)
    img = img.resize((150, 150))
    x = np.expand_dims(image.img_to_array(img), axis=0)/255.0
    #print(x.shape)
    #print(model.summary())
    global sess
    global graph
    with graph.as_default():
        set_session(sess)
        pred = model.predict(x)
        #clear_session()
    # get top 3 product id with confidence
    pred = pred.flatten()
    top_3_idx = pred.argsort()[::-1][:3]
    top_3_items = {idx2label[i]:np.round(pred[i],10) for i in top_3_idx}
    print(top_3_items)
    top_3_list = sorted(top_3_items.keys(), key=lambda x: top_3_items[x], reverse = True) 
    return top_3_list


