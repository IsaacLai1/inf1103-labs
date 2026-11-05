import json
import os
from abc import ABC, abstractmethod

FILENAME = "inventory.json"


# ===================== Product (abstract class) =====================
# Responsibility: represent and manage ONE product.
# Abstract: a plain Product can never be created, only Physical or Digital.

class Product(ABC):
    def __init__(self, product_id, name, price, stock):
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.__stock = stock

    def get_product_id(self):
        return self.__product_id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_stock(self):
        return self.__stock

    def update_stock(self, quantity):
        if quantity < 0:
            print("Stock cannot be negative. Stock not updated.")
            return False
        self.__stock = quantity
        return True

    def display_information(self):
        # The common part that every product shares
        print("ID: " + self.__product_id +
              " | Name: " + self.__name +
              " | Price: $" + format(self.__price, ".2f") +
              " | Stock: " + str(self.__stock))

    @abstractmethod
    def get_fulfilment_info(self):
        # No implementation here: every child class MUST provide its own
        pass


# ===================== CanBeShipped (interface) =====================
# A contract: any class that "signs" it must be able to calculate shipping.

class CanBeShipped(ABC):
    @abstractmethod
    def calculate_shipping_cost(self):
        pass


# ===================== PhysicalProduct =====================
# A PhysicalProduct IS-A Product, and it CanBeShipped.

class PhysicalProduct(Product, CanBeShipped):
    def __init__(self, product_id, name, price, stock, weight):
        super().__init__(product_id, name, price, stock)   # reuse Product's constructor
        self.__weight = weight                               # new attribute (kg)

    def get_weight(self):
        return self.__weight

    def display_information(self):
        super().display_information()                       # parent prints the common part
        print("    Type: Physical | Weight: " + format(self.__weight, ".2f") + " kg" +
              " | Shipping: $" + format(self.calculate_shipping_cost(), ".2f"))
        print("    " + self.get_fulfilment_info())

    def get_fulfilment_info(self):
        return "Fulfilment: Requires physical shipping."

    def calculate_shipping_cost(self):
        # Simple rule: $5.00 base fee + $2.00 per kg
        return 5.00 + 2.00 * self.__weight


# ===================== DigitalProduct =====================
# A DigitalProduct IS-A Product. It does NOT implement CanBeShipped.

class DigitalProduct(Product):
    def __init__(self, product_id, name, price, stock, download_size):
        super().__init__(product_id, name, price, stock)
        self.__download_size = download_size                # new attribute (MB)

    def get_download_size(self):
        return self.__download_size

    def display_information(self):
        super().display_information()
        print("    Type: Digital | Download Size: " +
              format(self.__download_size, ".2f") + " MB")
        print("    " + self.get_fulfilment_info())

    def get_fulfilment_info(self):
        return "Fulfilment: Delivered digitally via download link."


# ===================== Inventory =====================
# Responsibility: manage a COLLECTION of products. Same as Lab 6.

class Inventory:
    def __init__(self):
        self.__products = []

    def add_product(self, product):
        if self.search_product(product.get_product_id()) is not None:
            return False
        self.__products.append(product)
        return True

    def search_product(self, product_id):
        for product in self.__products:
            if product.get_product_id().upper() == product_id.upper():
                return product
        return None

    def display_all(self):
        print("\nCurrent Inventory")
        print("-" * 60)
        if len(self.__products) == 0:
            print("No products in inventory.")
        else:
            for product in self.__products:
                product.display_information()   # each object shows itself
                print()
        print("-" * 60)

    def get_products(self):
        return list(self.__products)


# ===================== File handling =====================
# Responsibility: convert between objects and JSON, load and save.

def product_to_dict(product):
    # Take apart: object -> dictionary, including a "type" identifier
    data = {
        "id": product.get_product_id(),
        "name": product.get_name(),
        "price": product.get_price(),
        "stock": product.get_stock()
    }
    if isinstance(product, PhysicalProduct):
        data["type"] = "physical"
        data["weight"] = product.get_weight()
    elif isinstance(product, DigitalProduct):
        data["type"] = "digital"
        data["download_size"] = product.get_download_size()
    return data


def dict_to_product(item):
    # Rebuild: dictionary -> the correct subclass, using the "type" identifier
    # Old Lab 6 data has no "type", so it is treated as physical with weight 0.
    product_type = item.get("type", "physical")

    if product_type == "digital":
        return DigitalProduct(item["id"], item["name"], item["price"],
                              item["stock"], item.get("download_size", 0.0))
    else:
        return PhysicalProduct(item["id"], item["name"], item["price"],
                               item["stock"], item.get("weight", 0.0))


def load_inventory():
    inventory = Inventory()

    if not os.path.exists(FILENAME):
        print("inventory.json not found. Starting with an empty inventory.")
        return inventory

    try:
        file = open(FILENAME, "r")
        data = json.load(file)
        file.close()
    except json.JSONDecodeError:
        print("inventory.json is corrupted. Starting with an empty inventory.")
        return inventory

    for item in data:
        try:
            inventory.add_product(dict_to_product(item))
        except KeyError:
            print("Skipped a product with missing information.")

    print("inventory.json found.")
    print("Inventory loaded successfully.")
    return inventory


def save_inventory(inventory):
    data = []
    for product in inventory.get_products():
        data.append(product_to_dict(product))

    file = open(FILENAME, "w")
    json.dump(data, file, indent=4)
    file.close()


# ===================== Menu functions =====================
# Responsibility: ask the user for input and call the right methods.

def add_product_menu(inventory):
    print("\nAdd New Product")
    print("Product Type:")
    print("1. Physical Product")
    print("2. Digital Product")
    product_type = input("Choose type (1 or 2): ").strip()

    if product_type not in ("1", "2"):
        print("Invalid type. Product not added.")
        return

    product_id = input("Product ID: ").strip().upper()

    if product_id == "":
        print("Product ID cannot be empty.")
        return

    if inventory.search_product(product_id) is not None:
        print("A product with that ID already exists.")
        return

    name = input("Product Name: ").strip()

    try:
        price = float(input("Price: "))
        stock = int(input("Stock Quantity: "))
        if product_type == "1":
            extra = float(input("Weight (kg): "))
        else:
            extra = float(input("Download Size (MB): "))
    except ValueError:
        print("Invalid number entered. Product not added.")
        return

    if price < 0 or stock < 0 or extra < 0:
        print("Values cannot be negative. Product not added.")
        return

    if product_type == "1":
        new_product = PhysicalProduct(product_id, name, price, stock, extra)
    else:
        new_product = DigitalProduct(product_id, name, price, stock, extra)

    inventory.add_product(new_product)
    print("\nProduct added successfully!")


def update_stock_menu(inventory):
    print("\nUpdate Stock")
    product_id = input("Enter Product ID: ").strip()
    product = inventory.search_product(product_id)

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found:")
    print("Name: " + product.get_name())
    print("Current Stock: " + str(product.get_stock()))

    try:
        new_stock = int(input("\nNew Stock Quantity: "))
    except ValueError:
        print("Invalid quantity. Stock not updated.")
        return

    if product.update_stock(new_stock):
        print("\nStock updated successfully!")


def search_product_menu(inventory):
    print("\nSearch Product")
    product_id = input("Enter Product ID: ").strip()
    product = inventory.search_product(product_id)

    if product is None:
        print("\nProduct not found.")
    else:
        print("\nProduct Found")
        print("-" * 60)
        product.display_information()
        print("-" * 60)


def show_menu():
    print("\n----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("----------------------------")


# ===================== Main Program =====================

def main():
    print("=" * 40)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 40)
    print()

    inventory = load_inventory()

    while True:
        show_menu()
        option = input("\nEnter option: ").strip()

        if option == "1":
            inventory.display_all()

        elif option == "2":
            add_product_menu(inventory)

        elif option == "3":
            update_stock_menu(inventory)

        elif option == "4":
            search_product_menu(inventory)

        elif option == "5":
            print("\nSaving inventory...")
            save_inventory(inventory)
            print("Inventory saved successfully to inventory.json.")

        elif option == "6":
            print("\nSaving inventory before exit...")
            save_inventory(inventory)
            print("Inventory saved successfully.")
            print("\nThank you for using Inventory Management System.")
            print("Program terminated.")
            break

        else:
            print("Invalid option. Please enter a number from 1 to 6.")


# Only run the menu when this file is run directly
# (not when another file, like lab7_tests.py, imports it)
if __name__ == "__main__":
    main()