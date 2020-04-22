from datetime import datetime
from psrPlatform import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(userid):
    return Users.query.filter_by(reviewerName = userid).first()


class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    reviewerID = db.Column(db.String(255), primary_key=True)
    reviewerName = db.Column(db.String(255), unique=True, nullable=False)
    reviewerPW = db.Column(db.String(255), nullable=False)
    rates = db.relationship('Ratings', backref='author', lazy=True)

    def get_id(self):
        return self.reviewerName
    def __repr__(self):
        return f"Users('{self.reviewerName}', '{self.reviewerID}')"


class Ratings(db.Model):
    __tablename__ = 'Ratings'
    reviewerID = db.Column(db.String(255), db.ForeignKey('Users.reviewerID'), primary_key=True, nullable=False)
    asin = db.Column(db.String(10), db.ForeignKey('Products.asin'), primary_key=True, nullable=False)
    reviewerName = db.Column(db.String(255), nullable=False)
    reviewText = db.Column(db.Text(30000), nullable=True)
    rating = db.Column(db.Integer, default=1)
    summary = db.Column(db.Text(1024), nullable=True)
    reviewTime = db.Column(db.DateTime, nullable=False, primary_key=True, default=datetime.utcnow)

    def __repr__(self):
        return f"Ratings('{self.reviewerID}', '{self.asin}','{self.reviewTime}')"

class Products(db.Model):
    __tablename__ = 'Products'
    asin = db.Column(db.String(10), primary_key=True)
    description = db.Column(db.Text(20000))
    price = db.Column(db.Float)
    imUrl = db.Column(db.String(255), nullable=False)
    categories = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    brand = db.Column(db.String(255))
    avg_overall_rating = db.Column(db.Float)
    keywords = db.Column(db.String(255))
    rates = db.relationship('Ratings', backref='product', lazy=True)

    def __repr__(self):
        return f"Products('{self.asin}', '{self.title}')"