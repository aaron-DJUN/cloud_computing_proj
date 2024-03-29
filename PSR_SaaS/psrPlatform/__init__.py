from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mysqldb import MySQL
import pickle 
import pandas as pd
from .recom_model.recommender import get_similar_users, get_top_N_recommended_items
# load recommender system 
SVDpp_val = pickle.load(open('./psrPlatform/recom_model/SVDpp_model.sav', 'rb'))
user_knn = pickle.load(open('./psrPlatform/recom_model/Knn_model.sav', 'rb'))
recom_df = pd.read_csv('./psrPlatform/recom_model/df_new.csv', index_col=None)
user_pool = set(recom_df.user.tolist())

app = Flask(__name__)
app.config['SECRET_KEY'] = #
app.config['SQLALCHEMY_DATABASE_URI'] = #
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = #
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from psrPlatform import routes
