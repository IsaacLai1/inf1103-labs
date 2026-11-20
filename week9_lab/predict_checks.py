import inventory_patterns

supplier = inventory_patterns.Supplier("S001", "TechSource Pte Ltd", "sales@techsource.com")

print("=== 2.3: order adds up to 250 ===")
lamp = inventory_patterns.PhysicalProduct("P001", "Desk Lamp", 25.00, 10, supplier, 1.0)
order = inventory_patterns.Order("O001", inventory_patterns.BulkDiscount(200, 20))
order.add_order_line(lamp, 10)
print("BulkDiscount(200, 20):", order.calculate_total())
order.set_discount(inventory_patterns.PercentageDiscount(10))
print("PercentageDiscount(10):", order.calculate_total())

print("\n=== 3.2: unknown product type ===")
try:
    inventory_patterns.ProductFactory.create("service", "S001", "Installation", 30.00, 5, supplier)
except ValueError as error:
    print("ValueError:", error)

print("\n=== 5.2: loading products.csv ===")
inventory = inventory_patterns.Inventory()
inventory_patterns.load_products("products.csv", inventory, supplier)

print("\n=== 5.1: type abc, then -5, then 12.50 ===")
value = inventory_patterns.get_positive_float("Enter a price: ")
print("Returned:", value)
