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


from fastapi import FastAPI
from products import products
from users import users
from pydantic import BaseModel
from fastapi import HTTPException


# define a class for new users
class CreateUserModel(BaseModel):
    id: str
    username: str
    email: str
    password: str


# define a class for existing users
class ExistingUserModel(BaseModel):
    username: str
    password: str


app = FastAPI()
# an empty list to store users
users = []


@app.get("/")
def get_home():
    return {"message": "Welcome to our E-commerce API"}


# lists of sample products
@app.get("/products")
def get_products():
    return {"products": products}


@app.get("/products/{product_id}")
def get_product_by_id(product_id: int):
    # return {"product_id": product_id}
    for product in products:
        if product["id"] == product_id:
            return {"products": product}
    return {"error": "Product not found"}


# registering new users
@app.post("/register")
def register_user(user: CreateUserModel):
    # checks if user exists
    for existing_user in users:
        # print(existing_user)
        if (
            existing_user["username"] == user["username"]
            or existing_user["email"] == user["email"]
        ):
            return {"error": "Username or email alrealy exist"}

        user["id"] = len(users) + 1
        print("user successfully registered.")
        users.append(user.model_dump())
    return {"message": "User registered successfully"}


@app.post("/login")
def existing_user_login(login_information: ExistingUserModel):
    for existing_user in users:
        if (
            existing_user["username"] != login_information["username"]
            or existing_user["password"] != login_information["password"]
        ):
            raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}
