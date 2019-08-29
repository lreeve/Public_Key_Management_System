# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask_user import UserMixin, UserManager
from flask_user.db_manager import DBManager
from flask_user.forms import RegisterForm
from flask_wtf import FlaskForm
from flask import current_app
from wtforms import StringField, SubmitField, validators, ValidationError
from app import db
#import app

# from flask_app import app

# Define the User data model. Make sure to add the flask_user.UserMixin !!
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information (required for Flask-User)
    username = db.Column(db.Unicode(255), nullable=False, server_default='', unique=True)
    #email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    # reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')
    pk = db.Column(db.Unicode(255), nullable=False, server_default='', unique=True)

    org_name = db.Column(db.Unicode(255), nullable=False, server_default='', unique=True)
    org_id = db.Column(db.Unicode(255), nullable=False, server_default='', unique=True)

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')

    # Relationships
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))

    revoked_keys = db.relationship('RevokedKeys', secondary='users_revoked',
                            backref=db.backref('users', lazy='dynamic'))

# Define the Role data model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()
    label = db.Column(db.Unicode(255), server_default=u'')  # for display purposes


# Define the UserRoles association model
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


class RevokedKeys(db.Model):
    __tablename__ = 'revoked_keys'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(255), nullable=False, server_default=u'')
    key = db.Column(db.Unicode(255), nullable=False, server_default=u'')


class UsersRevoked(db.Model):
    __tablename__ = 'users_revoked'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    revoked_id = db.Column(db.Integer(), db.ForeignKey('revoked_keys.id', ondelete='CASCADE'))




def pk_validator(form, field):
    pk = list(field.data)
    pk_length = len(pk)
    
    # Check that it contains only lowercase letters and numbers
    for ch in pk:
        if not (ch.islower() or ch.isdigit()): 
            raise ValidationError('Password must contain ONLY numbers and lowercase letters')
    
    # Public key must have exactly 64 characters 
    is_valid = pk_length == 64
    if not is_valid:
        raise ValidationError('Password must have exactly 64 characters')


def unique_pk_validator(form, field):
    user_manager =  current_app.user_manager
    available = db.session.query(User.pk).filter_by(pk=field.data).scalar() == None
    if not available:
        raise ValidationError('This public key is already in use. Please try another one.')


def unique_org_id_validator(form, field):
    user_manager =  current_app.user_manager
    available = db.session.query(User.org_id).filter_by(org_id=field.data).scalar() == None
    if not available:
        raise ValidationError('This organization id is already in use. Please try another one.')


def unique_org_name_validator(form, field):
    user_manager =  current_app.user_manager
    available = db.session.query(User.org_name).filter_by(org_name=field.data).scalar() == None
    if not available:
        raise ValidationError('This organization name is already in use. Please try another one.')



# Define the User registration form
# It augments the Flask-User RegisterForm with additional fields
class MyRegisterForm(RegisterForm):
    
    org_name = StringField('Organization Name', validators=[
        validators.DataRequired('Name is required'),
        unique_org_name_validator])

    org_id = StringField('Organization ID', validators=[
        validators.DataRequired('ID is required'),
        unique_org_id_validator])

    pk = StringField('Public Key', validators=[
        validators.DataRequired('Public Key is required'), 
        pk_validator, unique_pk_validator])


# Define the User profile form
class UserProfileForm(FlaskForm):
    username = StringField('Username', validators=[
        validators.DataRequired('Username is required')])

    org_name = StringField('Organization Name', validators=[
        validators.DataRequired('Username is required')])

    org_id = StringField('Organization ID', validators=[
        validators.DataRequired('ID is required')])

    pk = StringField('Public Key', validators=[
        validators.DataRequired('Public Key is required'),
        pk_validator])
    submit = SubmitField('Save')


