from fastapi import FastAPI, Query, Response
from pydantic import BaseModel, Field
import math

app = FastAPI()

# ----------------------
# STEP 1: Home
# ----------------------
@app.get("/")
def home():
    return {"message": "Welcome to Food Delivery App"}


# ----------------------
# STEP 2: Menu
# ----------------------
menu = [
    {"id": 1, "name": "Pizza", "price": 200, "category": "Food", "is_available": True},
    {"id": 2, "name": "Burger", "price": 120, "category": "Food", "is_available": True},
    {"id": 3, "name": "Coke", "price": 50, "category": "Drink", "is_available": True},
    {"id": 4, "name": "Fries", "price": 80, "category": "Food", "is_available": False},
    {"id": 5, "name": "Ice Cream", "price": 90, "category": "Dessert", "is_available": True},
    {"id": 6, "name": "Sandwich", "price": 100, "category": "Food", "is_available": True},
]


@app.get("/menu")
def get_menu():
    return {"total": len(menu), "items": menu}


# ----------------------
# STEP 9: Filter Menu
# ----------------------
def filter_menu_logic(category=None, max_price=None, is_available=None):
    filtered = []

    for item in menu:
        if category is not None and item["category"].lower() != category.lower():
            continue

        if max_price is not None and item["price"] > max_price:
            continue

        if is_available is not None and item["is_available"] != is_available:
            continue

        filtered.append(item)

    return filtered


@app.get("/menu/filter")
def filter_menu(category: str = None, max_price: int = None, is_available: bool = None):
    filtered_items = filter_menu_logic(category, max_price, is_available)

    return {"total": len(filtered_items), "items": filtered_items}


# ----------------------
# STEP 16: Search Menu
# ----------------------
@app.get("/menu/search")
def search_menu(keyword: str):
    results = []

    for item in menu:
        if keyword.lower() in item["name"].lower() or keyword.lower() in item["category"].lower():
            results.append(item)

    if not results:
        return {"message": "No items found"}

    return {"total_found": len(results), "items": results}


# ----------------------
# STEP 17: Sort Menu
# ----------------------
@app.get("/menu/sort")
def sort_menu(sort_by: str = "price", order: str = "asc"):
    valid_fields = ["price", "name", "category"]

    if sort_by not in valid_fields:
        return {"error": "Invalid sort field"}

    if order not in ["asc", "desc"]:
        return {"error": "Invalid order"}

    reverse = True if order == "desc" else False

    sorted_menu = sorted(menu, key=lambda x: x[sort_by], reverse=reverse)

    return {"sort_by": sort_by, "order": order, "items": sorted_menu}


# ----------------------
# STEP 18: Pagination
# ----------------------
@app.get("/menu/page")
def paginate_menu(page: int = 1, limit: int = 3):
    total = len(menu)

    start = (page - 1) * limit
    end = start + limit

    items = menu[start:end]

    total_pages = math.ceil(total / limit)

    return {
        "page": page,
        "limit": limit,
        "total_items": total,
        "total_pages": total_pages,
        "items": items,
    }


# ----------------------
# STEP 20: Smart Browse
# ----------------------
@app.get("/menu/browse")
def browse_menu(
    keyword: str = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4,
):
    filtered = menu

    if keyword:
        filtered = [
            item
            for item in menu
            if keyword.lower() in item["name"].lower()
            or keyword.lower() in item["category"].lower()
        ]

    valid_fields = ["price", "name", "category"]

    if sort_by not in valid_fields:
        return {"error": "Invalid sort field"}

    if order not in ["asc", "desc"]:
        return {"error": "Invalid order"}

    reverse = True if order == "desc" else False

    filtered = sorted(filtered, key=lambda x: x[sort_by], reverse=reverse)

    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit

    paginated = filtered[start:end]

    total_pages = math.ceil(total / limit)

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_items": total,
        "total_pages": total_pages,
        "items": paginated,
    }


# ----------------------
# STEP 3: Get Item
# ----------------------
@app.get("/menu/{item_id}")
def get_item(item_id: int):
    for item in menu:
        if item["id"] == item_id:
            return item
    return {"error": "Item not found"}


# ----------------------
# STEP 4: Orders
# ----------------------
orders = []
order_counter = 1


@app.get("/orders")
def get_orders():
    return {"total_orders": len(orders), "orders": orders}


# ----------------------
# STEP 5: Models
# ----------------------
class OrderRequest(BaseModel):
    customer_name: str = Field(min_length=2)
    item_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=20)
    delivery_address: str = Field(min_length=10)
    order_type: str = "delivery"


class NewMenuItem(BaseModel):
    name: str = Field(min_length=2)
    price: int = Field(gt=0)
    category: str = Field(min_length=2)
    is_available: bool = True


class CheckoutRequest(BaseModel):
    customer_name: str = Field(min_length=2)
    delivery_address: str = Field(min_length=10)


# ----------------------
# STEP 6: Helpers
# ----------------------
def find_item(item_id):
    for item in menu:
        if item["id"] == item_id:
            return item
    return None


def calculate_bill(price, quantity, order_type):
    total = price * quantity
    if order_type == "delivery":
        total += 30
    return total


# ----------------------
# STEP 7 & 8: Create Order
# ----------------------
@app.post("/orders")
def create_order(order: OrderRequest):
    global order_counter

    item = find_item(order.item_id)

    if not item:
        return {"error": "Item not found"}

    if not item["is_available"]:
        return {"error": "Item not available"}

    total = calculate_bill(item["price"], order.quantity, order.order_type)

    new_order = {
        "order_id": order_counter,
        "customer_name": order.customer_name,
        "item": item["name"],
        "quantity": order.quantity,
        "total_price": total,
        "order_type": order.order_type,
        "delivery_address": order.delivery_address,
    }

    orders.append(new_order)
    order_counter += 1

    return new_order


# ----------------------
# STEP 10: Add Menu
# ----------------------
@app.post("/menu")
def add_menu_item(item: NewMenuItem, response: Response):
    for m in menu:
        if m["name"].lower() == item.name.lower():
            return {"error": "Item already exists"}

    new_id = len(menu) + 1

    new_item = {
        "id": new_id,
        "name": item.name,
        "price": item.price,
        "category": item.category,
        "is_available": item.is_available,
    }

    menu.append(new_item)
    response.status_code = 201

    return new_item


# ----------------------
# STEP 11: Update Menu
# ----------------------
@app.put("/menu/{item_id}")
def update_menu(item_id: int, price: int = None, is_available: bool = None):
    item = find_item(item_id)

    if not item:
        return {"error": "Item not found"}

    if price is not None:
        item["price"] = price

    if is_available is not None:
        item["is_available"] = is_available

    return {"message": "Updated", "item": item}


# ----------------------
# STEP 12: Delete Menu
# ----------------------
@app.delete("/menu/{item_id}")
def delete_menu(item_id: int):
    item = find_item(item_id)

    if not item:
        return {"error": "Item not found"}

    menu.remove(item)

    return {"message": f"{item['name']} deleted"}


# ----------------------
# STEP 13: Cart
# ----------------------
cart = []


@app.post("/cart/add")
def add_to_cart(item_id: int, quantity: int = 1):
    item = find_item(item_id)

    if not item:
        return {"error": "Item not found"}

    if not item["is_available"]:
        return {"error": "Item not available"}

    for c in cart:
        if c["item_id"] == item_id:
            c["quantity"] += quantity
            return {"message": "Updated quantity", "cart": cart}

    cart.append(
        {
            "item_id": item_id,
            "name": item["name"],
            "quantity": quantity,
            "price": item["price"],
        }
    )

    return {"message": "Added to cart", "cart": cart}


@app.get("/cart")
def view_cart():
    total = sum(i["price"] * i["quantity"] for i in cart)
    return {"cart": cart, "grand_total": total}


# ----------------------
# STEP 14: Remove Cart Item
# ----------------------
@app.delete("/cart/{item_id}")
def remove_cart(item_id: int):
    for item in cart:
        if item["item_id"] == item_id:
            cart.remove(item)
            return {"message": "Removed", "cart": cart}

    return {"error": "Item not in cart"}


# ----------------------
# STEP 15: Checkout
# ----------------------
@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):
    global order_counter

    if not cart:
        return {"error": "Cart is empty"}

    placed = []
    total = 0

    for item in cart:
        price = calculate_bill(item["price"], item["quantity"], "delivery")

        order = {
            "order_id": order_counter,
            "customer_name": data.customer_name,
            "item": item["name"],
            "quantity": item["quantity"],
            "total_price": price,
            "order_type": "delivery",
            "delivery_address": data.delivery_address,
        }

        orders.append(order)
        placed.append(order)

        total += price
        order_counter += 1

    cart.clear()

    return {"message": "Order placed", "orders": placed, "grand_total": total}


# ----------------------
# STEP 19: Orders Search & Sort
# ----------------------
@app.get("/orders/search")
def search_orders(customer_name: str):
    result = [
        o
        for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not result:
        return {"message": "No orders found"}

    return {"total": len(result), "orders": result}


@app.get("/orders/sort")
def sort_orders(order: str = "asc"):
    if order not in ["asc", "desc"]:
        return {"error": "Invalid order"}

    reverse = order == "desc"

    return {"orders": sorted(orders, key=lambda x: x["total_price"], reverse=reverse)}