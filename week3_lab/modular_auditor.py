
def get_valid_input():    #function to get valid input from the user      
    entry = input("Enter stock quantity ")  

    if entry.lower() == "quit":    #if the user enters "quit", the function returns "quit" to exit the program
        return "quit"

    elif entry.isdigit() == False:    #if the user enters a non-digit value, the function prints an error message and returns None
        print("Invalid input. Please enter a valid stock quantity or type 'quit' to exit.")
        return None
    else:
        varQuantity = int(entry)    #if the user enters a valid digit, the function checks if it is negative. If it is negative, it prints an error message and returns None. Otherwise, it returns the valid quantity.

        if varQuantity < 0:    #if the user enters a negative value, the function prints an error message and returns None
            print("ERROR")
            return None   
        else:
            return varQuantity    #if the user enters a valid positive value, the function returns the valid quantity

def calculate_tax(amount):    #function to calculate tax based on the amount entered by the user
    tax = amount * 0.10
    return tax

def process_delivery(current_total, new_value): #function to process the delivery and update the total inventory
    new_total = current_total + new_value
    return new_total

def generate_report(total_units, failed_attempts):  #function to generate a report of the total units processed and the number of failed attempts
    print("Total units processed: " + str(total_units))
    print("Failed entries: " + str(failed_attempts))

varInventory = 0 
varTotalUnitsProcessed = 0 
varNumberofFailedEntries = 0
varTax = 0

print("Smart Inventory Auditor")

while True:
    entry = get_valid_input()

    if entry == "quit":    #if the user enters "quit", the program prints a message and exits the loop
        print("Exiting the program.")
        break

    elif entry is None:
        print("Invalid input. Please enter a valid stock quantity or type 'quit' to exit.")    #if the user enters an invalid input, the program prints an error message and increments the failed attempts counter
        varNumberofFailedEntries = varNumberofFailedEntries + 1
        

    else:
        varInventory = process_delivery(varInventory, entry)    #if the user enters a valid input, the program updates the total inventory and increments the total units processed counter. It also calculates the tax based on the entered amount and prints the current inventory and tax. If the inventory exceeds 500, it prints a warning message.
        varTotalUnitsProcessed = varTotalUnitsProcessed + 1
        varTax = calculate_tax(entry)
        print("Accepted. Current inventory: " + str(varInventory))
        print("Accepted. Current tax: " + str(varTax))

        if varInventory > 500:    #if the total inventory exceeds 500, the program prints a warning message
            print("Inventory limit exceeded. Please review stock levels.")
            break
            
generate_report(varTotalUnitsProcessed, varNumberofFailedEntries)    #the program generates a report of the total units processed and the number of failed attempts
