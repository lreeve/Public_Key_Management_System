# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import Blueprint, redirect, render_template
from flask import request, url_for, flash
from flask_user import current_user, login_required, roles_required
from app import db
from app.models.user_models import User, UserProfileForm, RevokedKeys
from flask import current_app as app
import json
import time
import datetime

main_blueprint = Blueprint('main', __name__, template_folder='templates')

# The Home page is accessible to anyone
@main_blueprint.route('/')
def home_page():
    return render_template('main/home_page.html')


# The User page is accessible to authenticated users (users that have logged in)
@main_blueprint.route('/member')
@login_required  # Limits access to authenticated users
def member_page():
    return render_template('main/user_page.html')


# The Admin page is accessible to users with the 'admin' role
@main_blueprint.route('/admin')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_page():
    return render_template('main/admin_page.html')


@main_blueprint.route('/main/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    form = UserProfileForm(request.form, obj=current_user)

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('main.home_page'))

    # Process GET or invalid POST
    return render_template('main/user_profile_page.html',
                           form=form)


@main_blueprint.route('/user/register', methods=['GET', 'POST'])
@roles_required('admin')
def register_view():
    self = app.user_manager
    """ Display registration form and create new User."""
    register_form = self.RegisterFormClass(request.form)  # for register.html

    # Process valid POST
    if request.method == 'POST' and register_form.validate():
        user = self.db_manager.add_user()
        register_form.populate_obj(user)
        # Store password hash instead of password
        user.password = self.hash_password(user.password)

        self.db_manager.save_user_and_user_email(user, None)
        self.db_manager.commit()
        flash("Successfully registered user: " + user.username, 'success')

    # Render form
    self.prepare_domain_translations()
    return render_template(self.USER_REGISTER_TEMPLATE,
                  form=register_form,
                  register_form=register_form)


@main_blueprint.route('/user/revoke_key', methods=['GET', 'POST'])
@login_required
def revoke_key():
    """ Remove user's key from database."""
    self = app.user_manager

    # Change user's key to empty string
    username = current_user.query.filter_by(username=current_user.username).first()
    current_user.revoked_keys.append(RevokedKeys(
            timestamp=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 
            key=current_user.pk))
    username.pk = ''
    self.db_manager.commit()
    #flash("Successfully revoked public key")

    # Return to Home Page
    return redirect(url_for('main.home_page'))


@main_blueprint.route('/public_keys')
#@login_required
def get_keys():
    # Formatted as such:
    # { org_name: {id: "", pk: ""}
    users = User.query.all()
    pub_keys = []
    #roles = [role.name for role in user.roles]
    for u in users:
        pub_keys.append(
            {"name": u.org_name,
            "id": u.org_id,
            "pk": u.pk
        })
    return json.dumps(pub_keys)


@main_blueprint.route('/revoked_keys')
def revoked_keys():
    users = User.query.all()
    revoked = []
    for u in users:
        revoked.append(
            {"name": u.org_name,
            "id": u.org_id,
            "revoked_keys": [(r.timestamp, r.key) for r in u.revoked_keys]
        })
    return json.dumps(revoked)







