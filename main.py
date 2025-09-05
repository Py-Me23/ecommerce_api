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


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Assume these are your data sources; they need to be defined
# somewhere, e.g., in products.py and users.py
# For this example, I'll define them here for clarity.
products = [
    {"id": 1, "name": "Laptop", "price": 1200},
    {"id": 2, "name": "Mouse", "price": 25},
    {"id": 3, "name": "Keyboard", "price": 75},
]

users = [
    {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "password": "password123",
    }
]


# Define a class for new users
class NewUser(BaseModel):
    id: int | None = None
    username: str
    email: str
    password: str


# Define a class for existing users
class ExistingUser(BaseModel):
    username: str
    password: str


app = FastAPI()

# An empty list to store users
# This is defined above, so no need for this comment here


@app.get("/")
def get_home():
    return {"message": "Welcome to our E-commerce API"}


# Lists of sample products
@app.get("/products")
def get_products():
    return {"products": products}


@app.get("/products/{product_id}")
def get_product_by_id(product_id: int):
    # Use a list comprehension or a generator expression for a more Pythonic approach
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        return {"products": product}
    raise HTTPException(status_code=404, detail="Product not found")


# Registering new users
@app.post("/register")
def register_user(user: NewUser):
    # Check if a user with the same username or email already exists.
    # We should raise an error immediately if either is a match.
    for existing_user in users:
        if existing_user["username"] == user.username:
            raise HTTPException(
                status_code=400,
                detail=f"User with username '{user.username}' already registered.",
            )
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=400,
                detail=f"User with email '{user.email}' already registered.",
            )

    # Assign a new ID to the user and add them to the list.
    # This logic should happen after the loop.
    user_dict = user.model_dump()
    user_dict["id"] = len(users) + 1
    users.append(user_dict)

    return {"message": "User registered successfully", "user": user_dict}


@app.post("/login")
def existing_user_login(login_information: ExistingUser):
    # Loop through all users to find a match.
    for existing_user in users:
        if (
            existing_user["username"] == login_information.username
            and existing_user["password"] == login_information.password
        ):
            return {"message": "Login successful"}

    # If the loop completes without finding a match, raise the exception.
    # This should be outside the loop, not inside.
    raise HTTPException(status_code=401, detail="Invalid username or password")
