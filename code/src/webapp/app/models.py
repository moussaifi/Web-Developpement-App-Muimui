from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext.login import UserMixin

from app import db, bcrypt


class User(db.Model, UserMixin):

    """ A user who has an account on the website. """

    __tablename__ = 'users'
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    phone = db.Column(db.String)
    email = db.Column(db.String, primary_key=True)
    confirmation = db.Column(db.Boolean)
    _password = db.Column(db.String)

    def __init__(self, first_name, last_name, phone, email,
                 confirmation, _password):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.confirmation = confirmation
        self.set_password(_password)

    @property
    def full_name(self):
        """ Returns First Name and Last Name"""
        return '{} {}'.format(self.first_name, self.last_name)

    @hybrid_property
    def password(self):
        """ Returns Password """
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        """ Generates hashed password"""
        self._password = bcrypt.generate_password_hash(plaintext).decode('utf-8')
        # pwhash = bcrypt.hashpw(plaintext.encode('utf8'), bcrypt.gensalt())
        # self._password = pwhash.decode('utf8')

    def set_password(self, password):
        """ set password """
        self._password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, plaintext):
        """ Checks password entered by user with original password """
        return bcrypt.check_password_hash(self.password, plaintext)

    def get_id(self):
        """ Returns user's email """
        return self.email


class InstaInfluencer(db.Model):
    """ Instagram influencer's table """

    __tablename__ = 'insta_influencer'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String)
    user_handle = db.Column(db.String)
    user_last_scrapped = db.Column(db.DateTime)


class InstaPost(db.Model):
    """ Instagram influencer's table """

    __tablename__ = 'insta_post'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String)
    post_date = db.Column(db.DateTime)
    last_scrapped_at = db.Column(db.DateTime)
    post_text = db.Column(db.String)
    likes = db.Column(db.Integer)
    comments = db.Column(db.Integer)
    post_link = db.Column(db.String)
    img_link = db.Column(db.String)


class Products(db.Model):
    """Product inventory table
    """

    __tablename__ = 'products'

    """
    TYPES = [('babana_republic', 'Banana Republic'),
             ('hm', 'H&M'),
             ('topshop', 'TopShop'),
             ('mango', 'Mango'),
             ('macys', "Macy's")]
    """

    id = db.Column(db.Integer, primary_key=True)
    page_link = db.Column(db.String)
    image_link = db.Column(db.String)
    name = db.Column(db.String)
    # date_scrapped = db.Column(db.DateTime)
    price = db.Column(db.Float)
    description = db.Column(db.String)
    brand = db.Column(db.String)
    # origin_site = db.Column(db.String)


class UserInfluencerMap(db.Model):
    """Mapping table between user and influencer
    """

    __tablename__ = 'user_influencer_map'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String, db.ForeignKey('users.email'))
    influencer_id = db.Column(db.Integer,
                              db.ForeignKey('insta_influencer.id'))
