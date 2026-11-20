import csv
import json
import os
from abc import ABC, abstractmethod

FILENAME = "inventory.json"


class Supplier:
    def __init__(self, supplier_id: str, name: str, contact_email: str):
        self.__supplier_id = supplier_id
        self.__name = name
        self.__contact_email = contact_email

    def get_supplier_id(self) -> str:
        return self.__supplier_id

    def get_name(self) -> str:
        return self.__name

    def get_contact_email(self) -> str:
        return self.__contact_email

    def display_information(self) -> None:
        print("Supplier ID: " + self.__supplier_id +
              " | Name: " + self.__name +
              " | Email: " + self.__contact_email)


class Product(ABC):
    def __init__(self, product_id: str, name: str, price: float,
                 stock: int, supplier: Supplier):
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
        if stock < 0:
            raise ValueError("Stock quantity cannot be negative.")
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.__stock = stock
        self.__supplier = supplier

    def get_product_id(self) -> str:
        return self.__product_id

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    def get_supplier(self) -> Supplier:
        return self.__supplier

    def update_stock(self, quantity: int) -> bool:
        if quantity < 0:
            print("Stock cannot be negative. Stock not updated.")
            return False
        self.__stock = quantity
        return True

    def display_information(self) -> None:
        print("ID: " + self.__product_id +
              " | Name: " + self.__name +
              " | Price: $" + format(self.__price, ".2f") +
              " | Stock: " + str(self.__stock) +
              " | Supplier: " + self.__supplier.get_name())

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass


class CanBeShipped(ABC):
    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass


class PhysicalProduct(Product, CanBeShipped):
    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, weight: float):
        super().__init__(product_id, name, price, stock, supplier)
        self.__weight = weight

    def get_weight(self) -> float:
        return self.__weight

    def display_information(self) -> None:
        super().display_information()
        print("    Type: Physical | Weight: " + format(self.__weight, ".2f") + " kg" +
              " | Shipping: $" + format(self.calculate_shipping_cost(), ".2f"))
        print("    " + self.get_fulfilment_info())

    def get_fulfilment_info(self) -> str:
        return "Fulfilment: Requires physical shipping."

    def calculate_shipping_cost(self) -> float:
        return 5.00 + 2.00 * self.__weight


class DigitalProduct(Product):
    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, download_size: float):
        super().__init__(product_id, name, price, stock, supplier)
        self.__download_size = download_size

    def get_download_size(self) -> float:
        return self.__download_size

    def display_information(self) -> None:
        super().display_information()
        print("    Type: Digital | Download Size: " +
              format(self.__download_size, ".2f") + " MB")
        print("    " + self.get_fulfilment_info())

    def get_fulfilment_info(self) -> str:
        return "Fulfilment: Delivered digitally via download link."


class ProductFactory:
    @staticmethod
    def create(product_type: str, product_id: str, name: str, price: float,
               stock_quantity: int, supplier: Supplier, extra: float = 0.0) -> Product:
        product_type = product_type.strip().lower()
        if product_type == "physical":
            return PhysicalProduct(product_id, name, price, stock_quantity, supplier, extra)
        elif product_type == "digital":
            return DigitalProduct(product_id, name, price, stock_quantity, supplier, extra)
        else:
            raise ValueError(f"Unknown product type: {product_type}")


class OrderLine:
    def __init__(self, product: Product, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        self.__product = product
        self.__quantity = quantity

    def get_product(self) -> Product:
        return self.__product

    def get_quantity(self) -> int:
        return self.__quantity

    def calculate_subtotal(self) -> float:
        return self.__product.get_price() * self.__quantity

    def display_information(self) -> None:
        print(self.__product.get_name() +
              " x " + str(self.__quantity) +
              " @ $" + format(self.__product.get_price(), ".2f") +
              " = $" + format(self.calculate_subtotal(), ".2f"))


class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, total: float) -> float:
        pass


class NoDiscount(DiscountStrategy):
    def apply(self, total: float) -> float:
        return total


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float):
        self.__percentage = percentage

    def apply(self, total: float) -> float:
        return total * (1 - self.__percentage / 100)


class BulkDiscount(DiscountStrategy):
    def __init__(self, threshold: float, amount: float):
        self.__threshold = threshold
        self.__amount = amount

    def apply(self, total: float) -> float:
        if total >= self.__threshold:
            return total - self.__amount
        return total


class StudentDiscount(DiscountStrategy):
    def apply(self, total: float) -> float:
        return total * 0.95


class Order:
    def __init__(self, order_id: str, discount: DiscountStrategy | None = None):
        self.__order_id = order_id
        self.__order_lines: list[OrderLine] = []
        if discount is None:
            discount = NoDiscount()
        self.__discount = discount

    def get_order_id(self) -> str:
        return self.__order_id

    def set_discount(self, discount: DiscountStrategy) -> None:
        self.__discount = discount

    def add_order_line(self, product: Product, quantity: int) -> None:
        order_line = OrderLine(product, quantity)
        self.__order_lines.append(order_line)

    def remove_order_line(self, product_id: str) -> bool:
        for order_line in self.__order_lines:
            if order_line.get_product().get_product_id().upper() == product_id.upper():
                self.__order_lines.remove(order_line)
                return True
        return False

    def calculate_total(self) -> float:
        total = 0.0
        for order_line in self.__order_lines:
            total += order_line.calculate_subtotal()
        return self.__discount.apply(total)

    def get_order_lines(self) -> list[OrderLine]:
        return list(self.__order_lines)

    def display_order(self) -> None:
        print("\nOrder " + self.__order_id)
        print("-" * 60)
        if len(self.__order_lines) == 0:
            print("No order lines.")
        for order_line in self.__order_lines:
            order_line.display_information()
        print("-" * 60)
        print("Total: $" + format(self.calculate_total(), ".2f"))


class Inventory:
    def __init__(self):
        self.__products: list[Product] = []

    def add_product(self, product: Product) -> bool:
        if self.find_product(product.get_product_id()) is not None:
            return False
        self.__products.append(product)
        return True

    def remove_product(self, product_id: str) -> bool:
        product = self.find_product(product_id)
        if product is None:
            return False
        self.__products.remove(product)
        return True

    def find_product(self, product_id: str) -> Product | None:
        for product in self.__products:
            if product.get_product_id().upper() == product_id.upper():
                return product
        return None

    def display_all(self) -> None:
        print("\nCurrent Inventory")
        print("-" * 60)
        if len(self.__products) == 0:
            print("No products in inventory.")
        else:
            for product in self.__products:
                product.display_information()
                print()
        print("-" * 60)

    def get_products(self) -> list[Product]:
        return list(self.__products)


def get_positive_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Please enter a number greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number, e.g. 12.50")


def get_non_negative_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Please enter a whole number of zero or more.")
                continue
            return value
        except ValueError:
            print("Please enter a valid whole number, e.g. 10")


def load_products(path: str, inventory: Inventory, supplier: Supplier) -> None:
    loaded = 0
    try:
        file = open(path, newline="")
    except FileNotFoundError:
        print(f"Products file not found: {path}")
    else:
        with file:
            reader = csv.reader(file)
            next(reader, None)
            for row_number, row in enumerate(reader, start=2):
                if not row:
                    continue
                try:
                    product_type, product_id, name, price, stock_quantity = row
                    product = ProductFactory.create(product_type, product_id, name,
                                                    float(price), int(stock_quantity), supplier)
                except ValueError as error:
                    print(f"Row {row_number} skipped: {error}")
                    continue
                if inventory.add_product(product):
                    loaded += 1
                else:
                    print(f"Row {row_number} skipped: product ID {product_id} already exists")
        print(f"{loaded} products loaded.")
    finally:
        print("Load attempt finished.")


def product_to_dict(product: Product) -> dict[str, str | float | int]:
    supplier = product.get_supplier()
    data: dict[str, str | float | int] = {
        "id": product.get_product_id(),
        "name": product.get_name(),
        "price": product.get_price(),
        "stock": product.get_stock(),
        "supplier_id": supplier.get_supplier_id(),
        "supplier_name": supplier.get_name(),
        "supplier_email": supplier.get_contact_email()
    }
    if isinstance(product, PhysicalProduct):
        data["type"] = "physical"
        data["weight"] = product.get_weight()
    elif isinstance(product, DigitalProduct):
        data["type"] = "digital"
        data["download_size"] = product.get_download_size()
    return data


def dict_to_product(item: dict[str, str | float | int],
                    suppliers: dict[str, Supplier]) -> Product:
    supplier_id = str(item.get("supplier_id", "UNKNOWN"))
    if supplier_id in suppliers:
        supplier = suppliers[supplier_id]
    else:
        supplier = Supplier(supplier_id,
                            str(item.get("supplier_name", "Unknown Supplier")),
                            str(item.get("supplier_email", "N/A")))
        suppliers[supplier_id] = supplier

    product_type = str(item.get("type", "physical"))
    if product_type == "digital":
        extra = float(item.get("download_size", 0.0))
    else:
        extra = float(item.get("weight", 0.0))
    return ProductFactory.create(product_type, str(item["id"]), str(item["name"]),
                                 float(item["price"]), int(item["stock"]), supplier, extra)


def load_inventory() -> Inventory:
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

    suppliers: dict[str, Supplier] = {}
    for item in data:
        try:
            inventory.add_product(dict_to_product(item, suppliers))
        except (KeyError, ValueError) as error:
            print(f"Skipped a product with invalid information: {error}")

    print("inventory.json found.")
    print("Inventory loaded successfully.")
    return inventory


def save_inventory(inventory: Inventory) -> None:
    data = []
    for product in inventory.get_products():
        data.append(product_to_dict(product))

    file = open(FILENAME, "w")
    json.dump(data, file, indent=4)
    file.close()


def collect_suppliers(inventory: Inventory) -> dict[str, Supplier]:
    suppliers: dict[str, Supplier] = {}
    for product in inventory.get_products():
        supplier = product.get_supplier()
        suppliers[supplier.get_supplier_id()] = supplier
    return suppliers


def choose_supplier(suppliers: dict[str, Supplier]) -> Supplier | None:
    supplier_id = input("Supplier ID: ").strip().upper()
    if supplier_id == "":
        print("Supplier ID cannot be empty.")
        return None

    if supplier_id in suppliers:
        print("Using existing supplier: " + suppliers[supplier_id].get_name())
        return suppliers[supplier_id]

    name = input("Supplier Name: ").strip()
    email = input("Supplier Email: ").strip()
    supplier = Supplier(supplier_id, name, email)
    suppliers[supplier_id] = supplier
    return supplier


def add_product_menu(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("\nAdd New Product")
    print("Product Type:")
    print("1. Physical Product")
    print("2. Digital Product")
    choice = input("Choose type (1 or 2): ").strip()

    if choice == "1":
        product_type = "physical"
    elif choice == "2":
        product_type = "digital"
    else:
        print("Invalid type. Product not added.")
        return

    product_id = input("Product ID: ").strip().upper()

    if product_id == "":
        print("Product ID cannot be empty.")
        return

    if inventory.find_product(product_id) is not None:
        print("A product with that ID already exists.")
        return

    name = input("Product Name: ").strip()
    price = get_positive_float("Price: ")
    stock = get_non_negative_int("Stock Quantity: ")
    if product_type == "physical":
        extra = get_positive_float("Weight (kg): ")
    else:
        extra = get_positive_float("Download Size (MB): ")

    supplier = choose_supplier(suppliers)
    if supplier is None:
        print("Product not added.")
        return

    try:
        new_product = ProductFactory.create(product_type, product_id, name, price,
                                            stock, supplier, extra)
    except ValueError as error:
        print(f"Product not added: {error}")
        return

    inventory.add_product(new_product)
    print("\nProduct added successfully!")


def update_stock_menu(inventory: Inventory) -> None:
    print("\nUpdate Stock")
    product_id = input("Enter Product ID: ").strip()
    product = inventory.find_product(product_id)

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found:")
    print("Name: " + product.get_name())
    print("Current Stock: " + str(product.get_stock()))

    new_stock = get_non_negative_int("\nNew Stock Quantity: ")
    if product.update_stock(new_stock):
        print("\nStock updated successfully!")


def search_product_menu(inventory: Inventory) -> None:
    print("\nSearch Product")
    product_id = input("Enter Product ID: ").strip()
    product = inventory.find_product(product_id)

    if product is None:
        print("\nProduct not found.")
    else:
        print("\nProduct Found")
        print("-" * 60)
        product.display_information()
        print("-" * 60)


def show_menu() -> None:
    print("\n----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("----------------------------")


def main() -> None:
    print("=" * 40)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 40)
    print()

    inventory = load_inventory()
    suppliers = collect_suppliers(inventory)

    while True:
        show_menu()
        option = input("\nEnter option: ").strip()

        if option == "1":
            inventory.display_all()

        elif option == "2":
            add_product_menu(inventory, suppliers)

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


if __name__ == "__main__":
    main()