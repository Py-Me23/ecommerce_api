# FastAPI E-Commerce
# 1. Setup
# Install FastAPI.
# Create a simple main.py with a root endpoint:
# GET / → return "Welcome to our E-commerce API"


# 2. Products
# Create a list of sample products in Python (id, name, description, price, image).
# Implement routes:
# GET /products → return all products.
# GET /products/{id} → return details of one product (use id to search in the list).


# 3. Users (Basic Auth Simulation)
# Create a list to store users (id, username, email, password).
# Routes:
# POST /register → accept user details and add to the list.
# POST /login → check username/email + password, return "Login successful" or "Invalid credentials".


# 4. Cart
# Use a dictionary to simulate carts: {user_id: [ {product_id, quantity}, … ] }.
# Routes:
# POST /cart → add product + quantity to a user’s cart.
# GET /cart/{user_id} → return the items in that user’s cart.


# 5. Checkout
# Calculate the subtotal (price * quantity) for each cart item.
# Add them together for a total.
# Route:
# POST /checkout/{user_id} → return an order summary (cart items + total).


from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from bson.objectid import ObjectId
from typing import List, Optional

# Assuming these are defined in your project
from db import products_collection, user_collection, carts_collection
from utils import replace_mongo_id


# Pydantic Models
class Product(BaseModel):
    name: str
    description: str
    price: float
    image: str
    stock: int


class CartModel(BaseModel):
    user_id: str
    product_id: str
    quantity: int


class NewUser(BaseModel):
    username: str
    email: str
    password: str


class ExistingUser(BaseModel):
    username: str
    password: str


# API Application
app = FastAPI()

# --- Main API Routes ---


@app.get("/")
def get_home():
    return {"message": "Welcome to our E-commerce API"}


@app.get("/products")
def get_products():
    products = list(products_collection.find({}))
    tidy_products = [replace_mongo_id(p) for p in products]
    return {"products": tidy_products}


@app.post("/products")
def post_products(product: Product):
    products_collection.insert_one(product.model_dump())
    return {"message": "Product added successfully."}


@app.get("/products/{product_id}")
def get_product_by_id(product_id: str):
    product = products_collection.find_one({"_id": ObjectId(product_id)})
    if product:
        return {"product": replace_mongo_id(product)}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
    )


# --- User Management Routes ---


@app.get("/users")
def get_users():
    users = user_collection.find().to_list()
    return {"users": list(map(replace_mongo_id, users))}


@app.post("/register")
def register_user(user: NewUser):
    # Check if a user with the same username or email already exists.
    existing_username = user_collection.find_one({"username": user.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username '{user.username}' already registered.",
        )

    existing_email = user_collection.find_one({"email": user.email})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{user.email}' already registered.",
        )

    # If no existing user is found, insert the new user.
    user_collection.insert_one(user.model_dump())
    return {"message": "User registered successfully"}


@app.post("/login")
def existing_user_login(login_information: ExistingUser):
    # Find a user by username and password.
    existing_user = user_collection.find_one(
        {"username": login_information.username, "password": login_information.password}
    )

    if existing_user:
        return {"message": "Login successful"}

    # If no match is found, raise an exception.
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
    )


@app.post("/cart")
def add_to_cart(item: CartModel):
    carts_collection.insert_one(item.model_dump())

    if item.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    return {"message": f"{item.quantity} item(s) added to cart"}


@app.get("/cart/{user_id}")
def get_cart(user_id: str):
    users_cart_items = list(carts_collection.find({"user_id": user_id}))
    items = [replace_mongo_id(item) for item in users_cart_items]

    return {"cart_items": items}


@app.post("/checkout/{user_id}")
def checkout(user_id: str, product: Product):
    cart_items = carts_collection.find({"user_id": str(ObjectId(user_id))})

    if not cart_items:
        raise HTTPException(status_code=404, detail="No items in cart")

    detailed_cart = []
    total = 0.0

    for item in cart_items:

        product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
        if not product:
            continue

        quantity = item["quantity"]
        subtotal = product["price"] * quantity
        total += subtotal

        detailed_cart.append(
            {
                "product_id": str(product["_id"]),
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity,
            }
        )

    return {"cart_items": detailed_cart, "total": total}
