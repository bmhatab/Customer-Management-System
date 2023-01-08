from datetime import datetime
from app import db,login_manager
from . import main
from .forms import UserForm,LoginForm
from ..forms import CustomerForm,InteractionForm
from ..models import Users,Customer,Interaction
from flask import Flask, render_template,flash,request,redirect,url_for,session
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user




@main.route('/')
def index():
    return render_template("base_index.html")

@main.route('/user/add', methods =['GET','POST'])
def add_user(): 
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash password first
            hash_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data,email=form.email.data,password_hash=hash_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        flash("User Added Sucessfully")
    #To display user names on the page 
    our_users = Users.query.order_by(Users.date_added)   
    return render_template('add_user.html',form=form,name=name,our_users=our_users)


@main.route('/login',methods=['GET','POST']) #post method needed for page containing forms
def login():
    form = LoginForm()
    #validating form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            # checking the hash
            if check_password_hash(user.password_hash,form.password.data):
                login_user(user)
                flash("Login Successful!")
                return redirect(url_for('main.dashboard'))
                
            else:
                flash("Wrong password -- Try again")
        else:
            flash("That user doesn't exist -- Try again")
    
    else:
        return render_template("login.html",form=form)



@main.route('/logout', methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    flash("You are logged out!")
    return render_template("base_index.html")

######################################################################################


@main.route('/customers/new/', methods=['GET', 'POST'])
def create_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(name=form.name.data, email=form.email.data, phone=form.phone.data, address=form.address.data, notes=form.notes.data)
        db.session.add(customer)
        db.session.commit()
        flash('Customer created successfully!')
        return redirect(url_for('main.list_customers'))
    return render_template('customers/new.html', form=form)

@main.route('/customers/')
def list_customers():
    customers = Customer.query.all()
    return render_template('customers/index.html', customers=customers)

@main.route('/customers/<int:customer_id>/', methods=['GET', 'POST'])
def view_customer(customer_id):
    customer = Customer.query.get(customer_id)
    interactions = Interaction.query.filter_by(customer_id=customer_id).all()
    return render_template('customers/view.html', customer=customer, interactions=interactions)


@main.route('/customers/<int:customer_id>/edit/', methods=['GET', 'POST'])
def edit_customer(customer_id):
    customer = Customer.query.get(customer_id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.email = form.email.data
        customer.phone = form.phone.data
        customer.address = form.address.data
        customer.notes = form.notes.data
        db.session.commit()
        flash('Customer edited successfully!')
        return redirect(url_for('main.view_customer', customer_id=customer_id))
    return render_template('customers/edit.html', form=form, customer=customer)


@main.route('/customers/<int:customer_id>/delete/', methods=['GET','POST'])
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully!')
    return redirect(url_for('main.list_customers'))

#####################################################################################

@main.route('/customers/<int:customer_id>/interactions/new/', methods=['GET', 'POST'])
def create_interaction(customer_id):
    form = InteractionForm()
    if form.validate_on_submit():
        interaction = Interaction(customer_id=customer_id, interaction_type=form.interaction_type.data, interaction_date=form.interaction_date.data, notes=form.notes.data)
        db.session.add(interaction)
        db.session.commit()
        flash('Interaction created successfully!')
        return redirect(url_for('main.view_customer', customer_id=customer_id))
    return render_template('customers/new_interaction.html',form=form,customer_id=customer_id)

@main.route('/customer-interactions')
def customer_interactions():
  customers = Customer.query.all()
  return render_template('customer_interactions.html', customers=customers)