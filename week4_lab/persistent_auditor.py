def load_inventory():
    #reads inventory.txt. First line = total, remaining lines = history list.
    #if file doesn't exist, starts fresh with 0 and an empty list.
    try:
        file = open("inventory.txt", "r")
        lines = file.readlines()
        file.close()

        if len(lines) == 0:
            return 0, []

        total = int(lines[0].strip())
        history = []
        for line in lines[1:]:
            history.append(int(line.strip()))

        return total, history

    except FileNotFoundError:
        print("No file yet, starting fresh")
        return 0, []


def save_inventory(total, history):
    #writes the final total on the first line, then each transaction on its own line
    file = open("inventory.txt", "w")
    file.write(str(total) + "\n")
    for amount in history:
        file.write(str(amount) + "\n")
    file.close()


def get_valid_input():
    entry = input("Enter stock quantity ")

    if entry.lower() == "quit":
        return "quit"

    elif entry.isdigit() == False:
        print("Invalid input. Please enter a valid stock quantity or type 'quit' to exit.")
        return None
    else:
        varQuantity = int(entry)

        if varQuantity < 0:
            print("ERROR")
            return None
        else:
            return varQuantity


def calculate_tax(amount):
    tax = amount * 0.10
    return tax


def process_delivery(current_total, new_value):
    new_total = current_total + new_value
    return new_total


def generate_report(total_units, failed_attempts):
    print("Total units processed: " + str(total_units))
    print("Failed entries: " + str(failed_attempts))


# ----- Main Program -----

varInventory, varHistory = load_inventory()
varTotalUnitsProcessed = 0
varNumberofFailedEntries = 0
varTax = 0

print("Smart Inventory Auditor")
print("Starting inventory loaded: " + str(varInventory))

while True:
    entry = get_valid_input()

    if entry == "quit":
        print("Exiting the program.")
        save_inventory(varInventory, varHistory)
        print("Inventory saved to inventory.txt")
        break

    elif entry is None:
        varNumberofFailedEntries = varNumberofFailedEntries + 1

    else:
        varInventory = process_delivery(varInventory, entry)
        varHistory.append(entry)
        varTotalUnitsProcessed = varTotalUnitsProcessed + 1
        varTax = calculate_tax(entry)
        print("Accepted. Current inventory: " + str(varInventory))
        print("Accepted. Current tax: " + str(varTax))

        if varInventory > 500:
            print("Inventory limit exceeded. Please review stock levels.")
            save_inventory(varInventory, varHistory)
            print("Inventory saved to inventory.txt")
            break

generate_report(varTotalUnitsProcessed, varNumberofFailedEntries)