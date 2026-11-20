import pytest

import inventory_patterns


@pytest.fixture
def supplier():
    return inventory_patterns.Supplier("S001", "TechSource Pte Ltd", "sales@techsource.com")


@pytest.fixture
def order_of_250(supplier):
    lamp = inventory_patterns.PhysicalProduct("P001", "Desk Lamp", 25.00, 10, supplier, 1.0)
    order = inventory_patterns.Order("O001")
    order.add_order_line(lamp, 10)
    return order


def test_no_discount_is_default(order_of_250):
    assert order_of_250.calculate_total() == 250.0


def test_percentage_discount(order_of_250):
    order_of_250.set_discount(inventory_patterns.PercentageDiscount(10))
    assert order_of_250.calculate_total() == pytest.approx(225.0)


def test_bulk_discount_applies_at_threshold(order_of_250):
    order_of_250.set_discount(inventory_patterns.BulkDiscount(200, 20))
    assert order_of_250.calculate_total() == pytest.approx(230.0)


def test_bulk_discount_not_applied_below_threshold(supplier):
    lamp = inventory_patterns.PhysicalProduct("P001", "Desk Lamp", 25.00, 10, supplier, 1.0)
    order = inventory_patterns.Order("O002", inventory_patterns.BulkDiscount(200, 20))
    order.add_order_line(lamp, 2)
    assert order.calculate_total() == pytest.approx(50.0)


def test_set_discount_changes_existing_order(order_of_250):
    order_of_250.set_discount(inventory_patterns.BulkDiscount(200, 20))
    first = order_of_250.calculate_total()
    order_of_250.set_discount(inventory_patterns.PercentageDiscount(10))
    assert first != order_of_250.calculate_total()


def test_student_discount(order_of_250):
    order_of_250.set_discount(inventory_patterns.StudentDiscount())
    assert order_of_250.calculate_total() == pytest.approx(237.5)


def test_new_strategy_works_without_changing_order(order_of_250):
    class HalfPrice(inventory_patterns.DiscountStrategy):
        def apply(self, total: float) -> float:
            return total / 2

    order_of_250.set_discount(HalfPrice())
    assert order_of_250.calculate_total() == pytest.approx(125.0)


def test_discount_strategy_is_abstract():
    with pytest.raises(TypeError):
        inventory_patterns.DiscountStrategy()


def test_factory_creates_physical(supplier):
    product = inventory_patterns.ProductFactory.create("physical", "P001", "Lamp", 25.0, 10, supplier, 1.5)
    assert isinstance(product, inventory_patterns.PhysicalProduct)
    assert product.get_weight() == 1.5


def test_factory_creates_digital(supplier):
    product = inventory_patterns.ProductFactory.create("digital", "D001", "Editor", 49.9, 100, supplier, 2048)
    assert isinstance(product, inventory_patterns.DigitalProduct)
    assert isinstance(product, inventory_patterns.Product)


def test_factory_rejects_unknown_type(supplier):
    with pytest.raises(ValueError, match="Unknown product type: service"):
        inventory_patterns.ProductFactory.create("service", "S001", "Install", 30.0, 5, supplier)


@pytest.mark.parametrize("price", [0, -5])
def test_invalid_price_rejected(supplier, price):
    with pytest.raises(ValueError, match="Price must be greater than zero"):
        inventory_patterns.ProductFactory.create("physical", "P001", "Lamp", price, 10, supplier)


def test_negative_stock_rejected(supplier):
    with pytest.raises(ValueError, match="Stock quantity cannot be negative"):
        inventory_patterns.ProductFactory.create("digital", "D001", "Editor", 10.0, -1, supplier)


@pytest.mark.parametrize("quantity", [0, -3])
def test_invalid_order_quantity_rejected(supplier, quantity):
    lamp = inventory_patterns.PhysicalProduct("P001", "Desk Lamp", 25.00, 10, supplier, 1.0)
    with pytest.raises(ValueError, match="Quantity must be greater than zero"):
        inventory_patterns.OrderLine(lamp, quantity)


def test_get_positive_float_asks_again(monkeypatch, capsys):
    answers = iter(["abc", "-5", "12.50"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    assert inventory_patterns.get_positive_float("Price: ") == 12.5
    output = capsys.readouterr().out
    assert "Please enter a valid number, e.g. 12.50" in output
    assert "Please enter a number greater than zero." in output


def test_missing_products_file(tmp_path, supplier, capsys):
    inventory = inventory_patterns.Inventory()
    inventory_patterns.load_products(str(tmp_path / "missing.csv"), inventory, supplier)
    output = capsys.readouterr().out
    assert "Products file not found" in output
    assert "Load attempt finished." in output
    assert inventory.get_products() == []


def test_bad_rows_skipped_and_good_rows_loaded(tmp_path, supplier, capsys):
    path = tmp_path / "products.csv"
    path.write_text("product_type,product_id,name,price,stock_quantity\n"
                    "physical,P001,Desk Lamp,25.00,10\n"
                    "digital,D001,Photo Editor,49.90,100\n"
                    "service,S001,Installation,30.00,5\n"
                    "physical,P002,Office Chair,abc,3\n"
                    "physical,P003,Monitor Stand,39.50,7\n")
    inventory = inventory_patterns.Inventory()
    inventory_patterns.load_products(str(path), inventory, supplier)
    output = capsys.readouterr().out
    assert len(inventory.get_products()) == 3
    assert "Row 4 skipped" in output
    assert "Row 5 skipped" in output
    assert "3 products loaded." in output
    assert output.strip().endswith("Load attempt finished.")
