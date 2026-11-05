from inventory_inheritance import (Product, PhysicalProduct, DigitalProduct,
                                   CanBeShipped, Inventory,
                                   product_to_dict, dict_to_product)

print("===== Test 1: Display physical and digital products =====")
guitar = PhysicalProduct("P101", "Guitar", 350.00, 5, 3.5)
windows = DigitalProduct("D201", "Windows 11", 199.00, 100, 5000)
guitar.display_information()
windows.display_information()

print("\n===== Test 2: get_fulfilment_info() on both subclasses =====")
print(guitar.get_fulfilment_info())
print(windows.get_fulfilment_info())

print("\n===== Test 3: Abstract Product cannot be created =====")
try:
    p = Product("X001", "Generic", 10.00, 1)
    print("Product was created (this should NOT happen)")
except TypeError as error:
    print("TypeError:", error)

print("\n===== Test 4: Shipping cost for different weights =====")
for weight in [0.5, 2.0, 10.0]:
    item = PhysicalProduct("T1", "Box", 1.00, 1, weight)
    print(str(weight) + " kg -> $" + format(item.calculate_shipping_cost(), ".2f"))

print("\n===== Test 5: Digital products do not implement shipping =====")
print("Guitar CanBeShipped? ", isinstance(guitar, CanBeShipped))
print("Windows CanBeShipped?", isinstance(windows, CanBeShipped))

print("\n===== Test 6: Inventory operations still work =====")
inventory = Inventory()
inventory.add_product(guitar)
inventory.add_product(windows)
print("Duplicate ID rejected:", inventory.add_product(guitar) is False)
inventory.search_product("P101").update_stock(8)
print("Guitar stock after update:", inventory.search_product("P101").get_stock())

print("\n===== Test 7: JSON conversion keeps the correct types =====")
for product in [guitar, windows]:
    data = product_to_dict(product)
    rebuilt = dict_to_product(data)
    print(data["type"], "->", type(rebuilt).__name__)