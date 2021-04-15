from flask import Flask, render_template, url_for, request, redirect, g 
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)


class Product(db.Model):

    __tablename__ = 'products'
    product_id      = db.Column(db.String(200), primary_key=True)
    date_created    = db.Column(db.DateTime, default=datetime.utcnow)
    price = db.Column(db.Float)


    def __repr__(self):
        return '<Product %r>' % self.product_id

class Client(db.Model):

    __tablename__ = 'clients'
    client_id      = db.Column(db.String(200), primary_key=True)
    lastname     = db.Column(db.String(200))
    address     = db.Column(db.String(200))
    cod_post     = db.Column(db.Integer)
    date_created    = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Client %r>' % self.client_id

class Location(db.Model):
    __tablename__   = 'locations'
    location_id     = db.Column(db.String(200), primary_key=True)
    date_created    = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Location %r>' % self.location_id

class ProductMovement(db.Model):

    __tablename__   = 'productmovements'
    movement_id     = db.Column(db.Integer, primary_key=True)
    product_id      = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    client_id      = db.Column(db.Integer, db.ForeignKey('clients.client_id'))
    qty             = db.Column(db.Float)
    from_location   = db.Column(db.Integer, db.ForeignKey('locations.location_id'))
    to_location     = db.Column(db.Integer, db.ForeignKey('locations.location_id'))
    movement_time   = db.Column(db.DateTime, default=datetime.utcnow)

    product         = db.relationship('Product', foreign_keys=product_id)
    fromLoc         = db.relationship('Location', foreign_keys=from_location)
    toLoc           = db.relationship('Location', foreign_keys=to_location)
    
    def __repr__(self):
        return '<ProductMovement %r>' % self.movement_id


"""Función para la pagina principal de la app"""
@app.route('/', methods=["POST", "GET"])
def index():
        
    if (request.method == "POST") and ('product_name','product_price' in request.form):
        product_name    = request.form["product_name"]
        product_price = request.form["product_price"]
        new_product     = Product(product_id=product_name, price=product_price)

        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect("/")
        
        except:
            return "Ha habido un error añadiendo el paquete"

    if (request.method == "POST") and ('client_name','client_lastname','client_address', 'client_cod_post' in request.form):
        client_name    = request.form["client_name"]
        client_lastname = request.form["client_price"]
        client_address = request.form["client_address"]
        client_cod_post = request.form["client_cod_post"]
        new_client     = Client(client_id=client_name, lastname=client_lastname, address=client_address, cod_post=client_cod_post)
        
        try:
            db.session.add(new_client)
            db.session.commit()
            return redirect("/")
        
        except:
            return "Ha habido un error añadiendo el cliente"
    
    if (request.method == "POST") and ('location_name' in request.form):
        location_name    = request.form["location_name"]
        new_location     = Location(location_id=location_name)

        try:
            db.session.add(new_location)
            db.session.commit()
            return redirect("/")
        
        except:
            return "Ha habido un error añadiendo la ubicación"
    else:
        products    = Product.query.order_by(Product.date_created).all()
        locations   = Location.query.order_by(Location.date_created).all()
        return render_template("index.html", products = products, locations = locations)

"""Función para la pagina de Ubicaciones"""
@app.route('/locations/', methods=["POST", "GET"])
def viewLocation():
    if (request.method == "POST") and ('location_name' in request.form):
        location_name = request.form["location_name"]
        new_location = Location(location_id=location_name)

        try:
            db.session.add(new_location)
            db.session.commit()
            return redirect("/locations/")

        except:
            locations = Location.query.order_by(Location.date_created).all()
            return "Ha habido un error añadiendo la ubicación"
    else:
        locations = Location.query.order_by(Location.date_created).all()
        return render_template("locations.html", locations=locations)
        
"""Función para la pagina de Paquetes"""
@app.route('/products/', methods=["POST", "GET"])
def viewProduct():
    if (request.method == "POST") and ('product_name', 'product_price' in request.form):
        product_name = request.form["product_name"]
        product_price = request.form["product_price"]
        new_product = Product(product_id=product_name, price=product_price)

        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect("/products/")

        except:
            products = Product.query.order_by(Product.date_created).all()
            return "Ha habido un error añadiendo el producto"
    else:
        products = Product.query.order_by(Product.date_created).all()
        return render_template("products.html", products=products)

"""Función para la pagina de Clientes"""
@app.route('/clients/', methods=["POST", "GET"])
def viewClient():
    if (request.method == "POST") and ('client_name', 'client_lastname', 'client_address', 'client_cod_post' in request.form):
        client_name = request.form["client_name"]
        client_lastname = request.form["client_lastname"]
        client_address = request.form["client_address"]
        client_cod_post = request.form["client_cod_post"]
        new_client = Client(client_id=client_name, lastname=client_lastname, address=client_address, cod_post=client_cod_post)

        try:
            db.session.add(new_client)
            db.session.commit()
            return redirect("/clients/")

        except:
            clients = Client.query.order_by(Client.date_created).all()
            return "Ha habido un error añadiendo el cliente"
    else:
        clients = Client.query.order_by(Client.date_created).all()
        return render_template("clients.html", clients=clients)

@app.route("/update-product<name>", methods=["POST", "GET"])
def updateProduct(name):
    product = Product.query.get_or_404(name)
    old_product = product.product_id

    if request.method == "POST":
        product.product_id = request.form['product_name']

        try:
            db.session.commit()
            updateProductInMovements(
                old_product, request.form['product_name'])
            return redirect("/products/")

        except:
            return "Ha habido un error actualizando el producto"
    else:
        return render_template("update-product.html", product=product)

"""Función para eliminar un producto"""
@app.route("/delete-product/<name>")
def deleteProduct(name):
    product_to_delete = Product.query.get_or_404(name)

    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        return redirect("/products/")
    except:
        return "Ha habido un error eliminando el producto"

"""Función para eliminar un cliente"""
@app.route("/delete-client/<name>")
def deleteClient(name):
    client_to_delete = Client.query.get_or_404(name)

    try:
        db.session.delete(client_to_delete)
        db.session.commit()
        return redirect("/clients/")
    except:
        return "Ha habido un error eliminando el cliente"

"""Función para actualizar una ubicación"""
@app.route("/update-location/<name>", methods=["POST", "GET"])
def updateLocation(name):
    location = Location.query.get_or_404(name)
    old_location = location.location_id

    if request.method == "POST":
        location.location_id = request.form['location_name']

        try:
            db.session.commit()
            updateLocationInMovements(
                old_location, request.form['location_name'])
            return redirect("/locations/")

        except:
            return "Ha habido un error actualizando la ubicación"
    else:
        return render_template("update-location.html", location=location)

"""Función para eliminar una ubicación"""
@app.route("/delete-location/<name>")
def deleteLocation(name):
    location_to_delete = Location.query.get_or_404(name)

    try:
        db.session.delete(location_to_delete)
        db.session.commit()
        return redirect("/locations/")
    except:
        return "Ha habido un error eliminando la ubicación"

"""Función para la página de Movimientos"""
@app.route("/movements/", methods=["POST", "GET"])
def viewMovements():
    if request.method == "POST" :
        product_id      = request.form["productId"]
        client_id = request.form["clientId"]
        qty             = request.form["qty"]
        fromLocation    = request.form["fromLocation"]
        toLocation      = request.form["toLocation"]
        new_movement = ProductMovement(
            product_id=product_id, qty=qty, client_id=client_id, from_location=fromLocation, to_location=toLocation)

        try:
            db.session.add(new_movement)
            db.session.commit()
            return redirect("/movements/")

        except:
            return "Ha habido un error añadiendo un nuevo movimiento"
    else:
        products    = Product.query.order_by(Product.date_created).all()
        clients    = Client.query.order_by(Client.date_created).all()
        locations   = Location.query.order_by(Location.date_created).all()
        movs = ProductMovement.query\
        .join(Product, ProductMovement.product_id == Product.product_id,)\
        .join(Client, ProductMovement.client_id == Client.client_id,)\
        .add_columns(
            ProductMovement.movement_id,
            ProductMovement.qty,
            Product.product_id,
            ProductMovement.client_id,
            ProductMovement.from_location,
            ProductMovement.to_location,
            ProductMovement.movement_time)\
        .all()

        movements   = ProductMovement.query.order_by(
            ProductMovement.movement_time).all()
        return render_template("movements.html", movements=movs, products=products, clients=clients, locations=locations)

"""Función para actualizar un movimiento"""
@app.route("/update-movement/<int:id>", methods=["POST", "GET"])
def updateMovement(id):

    movement    = ProductMovement.query.get_or_404(id)
    products    = Product.query.order_by(Product.date_created).all()
    locations   = Location.query.order_by(Location.date_created).all()

    if request.method == "POST":
        movement.product_id  = request.form["productId"]
        movement.qty         = request.form["qty"]
        movement.to_location  = request.form["toLocation"]

        try:
            db.session.commit()
            return redirect("/movements/")

        except:
            return "Ha habido un error actualizando el movimiento del producto"
    else:
        return render_template("update-movement.html", movement=movement, locations=locations, products=products)

"""Función para eliminar un movimiento"""
@app.route("/delete-movement/<int:id>")
def deleteMovement(id):
    movement_to_delete = ProductMovement.query.get_or_404(id)

    try:
        db.session.delete(movement_to_delete)
        db.session.commit()
        return redirect("/movements/")
    except:
        return "Ha habido un error eliminando el movimiento del producto"


@app.route("/movements/get-from-locations/", methods=["POST"])
def getLocations():
    product = request.form["productId"]
    location = request.form["location"]
    locationDict = defaultdict(lambda: defaultdict(dict))
    locations = ProductMovement.query.\
        filter( ProductMovement.product_id == product).\
        filter(ProductMovement.to_location != '').\
        add_columns(ProductMovement.from_location, ProductMovement.to_location, ProductMovement.qty).\
        all()

    for key, location in enumerate(locations):
        if(locationDict[location.to_location] and locationDict[location.to_location]["qty"]):
            locationDict[location.to_location]["qty"] += location.qty
        else:
            locationDict[location.to_location]["qty"] = location.qty

    return locationDict


@app.route("/dub-locations/", methods=["POST", "GET"])
def getDublicate():
    location = request.form["location"]
    locations = Location.query.\
        filter(Location.location_id == location).\
        all()
    print(locations)
    if locations:
        return {"output": False}
    else:
        return {"output": True}

@app.route("/dub-products/", methods=["POST", "GET"])
def getPDublicate():
    product_name = request.form["product_name"]
    products = Product.query.\
        filter(Product.product_id == product_name).\
        all()
    print(products)
    if products:
        return {"output": False}
    else:
        return {"output": True}

@app.route("/dub-clients/", methods=["POST", "GET"])
def getCDublicate():
    client_name = request.form["client_name"]
    clients = Client.query.\
        filter(Client.client_id == client_name).\
        all()
    print(clients)
    if clients:
        return {"output": False}
    else:
        return {"output": True}

def updateLocationInMovements(oldLocation, newLocation):
    movement = ProductMovement.query.filter(ProductMovement.from_location == oldLocation).all()
    movement2 = ProductMovement.query.filter(ProductMovement.to_location == oldLocation).all()
    for mov in movement2:
        mov.to_location = newLocation
    for mov in movement:
        mov.from_location = newLocation
     
    db.session.commit()

def updateProductInMovements(oldProduct, newProduct):
    movement = ProductMovement.query.filter(ProductMovement.product_id == oldProduct).all()
    movement = ProductMovement.query.filter(ProductMovement.price == oldProduct).all()
    for mov in movement:
        mov.product_id = newProduct
    for mov in movement:
        mov.price = newProduct
        
    db.session.commit()

if (__name__ == "__main__"):
    app.run(debug=True)
