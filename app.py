import os
from flask import Flask, flash, redirect, render_template, Request, request, session, url_for, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Float, ForeignKey, Integer, String, text, or_
from sqlalchemy.orm import relationship



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///groceries.db'
app.secret_key = 'web_app'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'img')
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    products = relationship("Product", back_populates="category")

class Product(db.Model):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    MFG = Column(String)
    EXP = Column(String)
    cost_per_unit = Column(Float)
    units = Column(String)
    section_id = Column(Integer, ForeignKey('categories.id'))
    stock = Column(Integer)
    image = Column(String)

    category = relationship("Category", back_populates="products")

class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    product = db.relationship('Product', backref='carts')

@app.route('/', methods = ['GET', 'POST'])
def home():
  products = Product.query.all()
  categories = Category.query.all()
  print(categories)

  return render_template('home.html', products=products, categories=categories)

@app.route('/search', methods=['POST'])
def search():
    products = []
    search = request.form.get('search')
    field = request.form.get('field')
    if field == 'name':
        products = db.session.query(Product).filter(Product.name.contains(search)).all()
    elif field == 'MFG':
        products = db.session.query(Product).filter(Product.MFG.contains(search)).all()
    elif field == 'EXP':
        products = db.session.query(Product).filter(Product.EXP.contains(search)).all()
    elif field == 'cost_per_unit':
        lower_bound = float(search) * 0.75
        upper_bound = float(search)
        products = db.session.query(Product).filter(Product.cost_per_unit.between(lower_bound, upper_bound)).all()
    elif field == 'section_id':
        products = db.session.query(Product).join(Category, Product.section_id == Category.id).filter(Category.name.contains(search)).all()
    categories = Category.query.all()
    return render_template('home.html', products=products, categories=categories)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        result = db.session.execute(text('SELECT * FROM users WHERE username = :username AND password = :password'), {'username': username, 'password': password}).fetchone()
        if result:
            session['username'] = username
            session['user_id'] = result[0]
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error = 'incorrect username and password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        result = db.session.execute(text('SELECT * FROM users WHERE username = :username'), {'username': username}).fetchone()
        if result:
            return render_template('register.html', error='Username already taken')
        else:
            db.session.execute(text('INSERT INTO users (username, password) VALUES (:username, :password)'), {'username': username, 'password': password})
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/manager', methods = ['GET', 'POST'])
def manager():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        result = db.session.execute(text('SELECT * FROM admin WHERE username = :username AND password = :password'), {'username': username, 'password': password}).fetchone()
        if result:
            session['username'] = username
            session['is_manager'] = True
            return redirect(url_for('home'))
        else:
            return render_template('manager_login.html', error = 'incorrect username and password')
    return render_template('manager_login.html')


@app.route('/category', methods = ['GET', 'POST'])
def category():
     
     if 'is_manager' not in session or not session['is_manager']:
         return redirect(url_for('manager'))
     if request.method == 'POST':
        if 'delete_id' in request.form:
            delete_id = request.form['delete_id']
            db.session.execute(text('DELETE FROM categories WHERE id = :id'), {'id': delete_id})
            db.session.execute(text('DELETE FROM sqlite_sequence WHERE name="categories"'))
            db.session.commit()
        else:
            name = request.form['name']
            db.session.execute(text('INSERT INTO categories (name) VALUES (:name)'), {'name': name})
            db.session.commit()
            categories = db.session.execute(text('SELECT * FROM categories')).fetchall()
     categories = db.session.execute(text('SELECT * FROM categories')).fetchall()
     return render_template('category.html', categories=categories)

@app.route('/products', methods = ['GET', 'POST'])
def products():
    if 'is_manager' not in session or not session['is_manager']:
        return redirect(url_for('manager'))

    if request.method == 'POST':
        if 'delete_id' in request.form:
            delete_id = request.form['delete_id']
            db.session.execute(text('DELETE FROM products WHERE id = :id'), {'id': delete_id})
            db.session.execute(text('DELETE FROM sqlite_sequence WHERE name="products"'))
            db.session.commit()
        else:
            name = request.form['name']
            mfg = request.form['mfg']
            exp = request.form['exp']
            cost_per_unit = request.form['cost_per_unit']
            units = request.form['units']
            section_id = request.form['section_id']
            stock = int(request.form['stock'])
            if stock <= 0:
                flash('Stock must be a positive number')
                return redirect(url_for('products'))

            image = request.files['image']

            if image:
                filename = image.filename

                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])

                db.session.execute(text('INSERT INTO products (name, MFG, EXP, cost_per_unit, units, section_id, stock, image) VALUES (:name, :mfg, :exp, :cost_per_unit, :units, :section_id, :stock, :image)'), {'name': name, 'mfg': mfg, 'exp': exp, 'cost_per_unit': cost_per_unit, 'units':units, 'section_id': section_id, 'stock': stock, 'image': filename})
                db.session.commit()
            else:
                db.session.execute(text('INSERT INTO products (name, MFG, EXP, cost_per_unit, units, section_id, stock) VALUES (:name, :mfg, :exp, :cost_per_unit, :units, :section_id, :stock)'), {'name': name, 'mfg': mfg, 'exp': exp, 'cost_per_unit': cost_per_unit, 'units':units, 'section_id': section_id, 'stock': stock})
                db.session.commit()

    products = db.session.execute(text('SELECT * FROM products')).fetchall()
    sections = db.session.execute(text('SELECT * FROM categories')).fetchall()
    return render_template('products.html', products=products, sections=sections)

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = db.session.execute(text('SELECT * FROM products WHERE id = :id'), {'id': id}).fetchone()

    if not product:
        flash('Product not found')
        return redirect(url_for('products'))

    if request.method == 'POST':
        name = request.form['name']
        mfg = request.form['mfg']
        exp = request.form['exp']
        cost_per_unit = request.form['cost_per_unit']
        units = request.form['units']
        section_id = request.form['section_id']
        stock = request.form['stock']

        db.session.execute(text('UPDATE products SET name = :name, MFG = :mfg, EXP = :exp, cost_per_unit = :cost_per_unit, units = :units, stock = :stock, section_id = :section_id WHERE id = :id'), {'name': name, 'mfg': mfg, 'exp': exp, 'cost_per_unit': cost_per_unit, 'units': units, 'stock': stock, 'section_id': section_id, 'id': id})
        db.session.commit()

        return redirect(url_for('products'))
    
    sections = db.session.execute(text('SELECT * FROM categories')).fetchall()
    return render_template('edit_product.html', product=product, sections=sections)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    product_id = request.form.get('product_id')
    cart_item = Cart.query.filter_by(user_id=user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=user.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    cart_items = Cart.query.filter_by(user_id=user.id).all()
    total_price = 0
    for item in cart_items:
        item.total_price = item.quantity * item.product.cost_per_unit
        total_price += item.total_price
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/delete_from_cart', methods=['POST'])
def delete_from_cart():
    if 'username' not in session:
        return redirect(url_for('login'))
    item_id = request.form.get('item_id')
    Cart.query.filter_by(id=item_id).delete()
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/increase_quantity', methods=['POST'])
def increase_quantity():
    if 'username' not in session:
        return redirect(url_for('login'))
    item_id = request.form.get('item_id')
    cart_item = Cart.query.filter_by(id=item_id).first()
    if cart_item:
        cart_item.quantity += 1
        db.session.commit()
    return redirect(url_for('cart'))

@app.route('/decrease_quantity', methods=['POST'])
def decrease_quantity():
    if 'username' not in session:
        return redirect(url_for('login'))
    item_id = request.form.get('item_id')
    cart_item = Cart.query.filter_by(id=item_id).first()
    if cart_item and cart_item.quantity > 1:
        cart_item.quantity -= 1
        db.session.commit()
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    cart_items = Cart.query.filter_by(user_id=user.id).all()
    total_price = 0
    cart_items_copy = []
    for item in cart_items:
        if item.product.stock >= item.quantity:
            item.product.stock -= item.quantity
            item.total_price = item.quantity * item.product.cost_per_unit
            total_price += item.total_price
            cart_items_copy.append({
                'product_name': item.product.name,
                'cost_per_unit': item.product.cost_per_unit,
                'quantity': item.quantity,
                'total_price': item.total_price
            })
        else:
            return "Error: Not enough stock for " + item.product.name
    db.session.commit()
    Cart.query.filter_by(user_id=user.id).delete(synchronize_session='fetch')
    db.session.commit()
    return render_template('checkout.html', cart_items=cart_items_copy, total_price=total_price)

if __name__ == "__main__":
    app.run(debug=True)
