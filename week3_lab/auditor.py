varInventory = 0 
varTotalUnitsProcessed = 0 
varNumberofFailedEntries = 0

print("Smart Inventory Auditor")

while True:
    entry = input("Enter stock quantity ")

    if entry.lower() == "quit":
        print("Exiting the program.")
        break

    elif entry.isdigit() == False:
        print("Invalid input. Please enter a valid stock quantity or type 'quit' to exit.")
        varNumberofFailedEntries = varNumberofFailedEntries + 1

    else :
        varQuantity = int(entry)

        if varQuantity < 0:
            print("ERROR")
            varNumberofFailedEntries = varNumberofFailedEntries + 1

        else:
            varInventory = varInventory + varQuantity
            varTotalUnitsProcessed = varTotalUnitsProcessed + 1
            print("Accepted. Current inventory: " + str(varInventory))

            if varInventory > 500:
                print("Inventory limit exceeded. Please review stock levels.")
            
print("Total units processed: " + str(varTotalUnitsProcessed))
print("Failed entries: " + str(varNumberofFailedEntries))


