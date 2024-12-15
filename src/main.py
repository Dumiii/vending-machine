import time
import signal
import sys

from db_utils import DBUtils

db = DBUtils("vending_machine.db")
pence_values = [1, 2, 5, 10, 20, 50, 100, 200]

def extract_from_input(input, is_product):
    result = []
    aux = ()
    for element in input.split(";"):
        values = element.split(",")
        if is_product:
            aux = (
                values[0],
                float(values[1]),
                int(values[2])
            )
        else:
            aux = (
                values[0],
                int(values[1])
            )

        result.append(aux)
    return result


def calculate_total_change(changes):
    result = 0
    for i in range(len(pence_values)):
        result += pence_values[i] * changes[i][1]
    return result


def calculate_change_coins(customer_change_pence):
    result = []
    for value in reversed(pence_values):
        num_coins, customer_change_pence = customer_change_pence // value, customer_change_pence % value
        if num_coins > 0:
            type = ''
            if value is 200 or value is 100:
                type = '£' + str((int(value / 100)))
            else:
                type = str(value) + 'p'
            result.append((type, int(num_coins)))
    return result


def calculate_db_change(change_coins, current_changes):
    change_coins_list = [list(i) for i in change_coins]
    current_changes_list = [list(i) for i in current_changes]
    result = []
    for i in range(len(change_coins_list)):
        for current_change in current_changes_list:
            if(current_change[0] == change_coins[i][0]):
                result.append([current_change[1]-change_coins[i][1], current_change[0]])
    return [tuple(i) for i in result]


def operate_vending_machine(db):
    while True:
        products, changes = db.get_products_change()
        print("Current products available:")
        print("---------------------------------------")
        print('Item -- Name -- Price -- Quantity\n')
        for i in range(len(products)):
            print(f'{i+1}. {products[i][0]} -- £{products[i][1]} -- {products[i][2]}')
        print()

        total_change = calculate_total_change(changes)
        print(f"The machine currently has £{total_change / 100} total change.")
        print("Press Ctrl-C at any point to terminate the program.\n")

        selected_product = int(input(f"Please select your product (1-{len(products)}): "))
        selected_product_name = products[selected_product-1][0]
        selected_product_price = products[selected_product-1][1]
        selected_product_quantity = products[selected_product-1][2]

        if selected_product_quantity == 0:
            print(f"Unfortunately I have ran out of {selected_product_name}, please select another product.\n\n")
        else:
            inserted_money = float(input(f'Please insert money in pounds (example: 1.50): '))
            if (inserted_money - selected_product_price) > (total_change / 100):
                print(f"\n\nDispensing product...")
                time.sleep(1)
                print(f"The machine does not have enough change to dispense {selected_product_name}, please try again.\n\n")
            else:
                while inserted_money < selected_product_price:
                    amount_missing = selected_product_price - inserted_money
                    next_insertion = float(input(f"Insufficient funds provided, please insert more (missing {amount_missing}): "))
                    inserted_money += next_insertion
                
                customer_change = inserted_money - selected_product_price
                if customer_change > 0:
                    change_coins = calculate_change_coins(customer_change*100)
                    new_machine_changes = calculate_db_change(change_coins, changes)
                    db.update_changes(new_machine_changes)
            
                print(f"\n\nDispensing product...")
                time.sleep(1)
                print(f'''Dispensed product {selected_product_name} and gave back £{customer_change if customer_change > 0 else 0}\n\n''')
                db.update_product_quantity(
                    selected_product_name,
                    selected_product_quantity-1)
        

def main():
    if db.connect_and_create():
        products, changes = db.get_products_change()
        
        if len(products) == 0:
            print("No products found, please provide an initial list of products in this format -> name1,price1,quantity1;name2,price2,quantity2 :")
            products = input()
            products_to_insert = extract_from_input(products, True)

            print("Please give an initial amount of change for the machine in the following format: 1p,amount;2p,amount;5p,amount;10p,amount;20p,amount;50p,amount;£1,amount;£2,amount: ")
            changes = input()
            changes_to_insert = extract_from_input(changes, False)

            products, changes = products_to_insert, changes_to_insert

        db.create_products_change(products, changes)
        operate_vending_machine(db)
        db.save_and_disconnect()


def handler(signum, frame):
    print(f"\nReceived signal to end program, terminating db connection and shutting down.")
    db.save_and_disconnect()
    sys.exit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    print('''
*/$$****/$$**************************/$$*/$$***************************/$$******/$$*********************/$$*******/$$********************
|*$$***|*$$*************************|*$$|__/**************************|*$$$****/$$$********************|*$$******|__/********************
|*$$***|*$$*/$$$$$$**/$$$$$$$***/$$$$$$$*/$$*/$$$$$$$***/$$$$$$*******|*$$$$**/$$$$**/$$$$$$***/$$$$$$$|*$$$$$$$**/$$*/$$$$$$$***/$$$$$$*
|**$$*/*$$//$$__**$$|*$$__**$$*/$$__**$$|*$$|*$$__**$$*/$$__**$$******|*$$*$$/$$*$$*|____**$$*/$$_____/|*$$__**$$|*$$|*$$__**$$*/$$__**$$
*\**$$*$$/|*$$$$$$$$|*$$**\*$$|*$$**|*$$|*$$|*$$**\*$$|*$$**\*$$******|*$$**$$$|*$$**/$$$$$$$|*$$******|*$$**\*$$|*$$|*$$**\*$$|*$$$$$$$$
**\**$$$/*|*$$_____/|*$$**|*$$|*$$**|*$$|*$$|*$$**|*$$|*$$**|*$$******|*$$\**$*|*$$*/$$__**$$|*$$******|*$$**|*$$|*$$|*$$**|*$$|*$$_____/
***\**$/**|**$$$$$$$|*$$**|*$$|**$$$$$$$|*$$|*$$**|*$$|**$$$$$$$******|*$$*\/**|*$$|**$$$$$$$|**$$$$$$$|*$$**|*$$|*$$|*$$**|*$$|**$$$$$$$
****\_/****\_______/|__/**|__/*\_______/|__/|__/**|__/*\____**$$******|__/*****|__/*\_______/*\_______/|__/**|__/|__/|__/**|__/*\_______/
*******************************************************/$$**\*$$*************************************************************************
******************************************************|**$$$$$$/*************************************************************************
*******************************************************\______/**************************************************************************
                                                       _______________________
                                                      |                       |
                                                      |  [     ][     ][     ]|
                                                      |  [     ][     ][     ]|
                                                      |  [     ][     ][     ]|
                                                      |  [____ ][____ ][____ ]|
                                                      |                       |
                                                      |  [     ][     ][     ]|
                                                      |  [     ][     ][     ]|
                                                      |  [     ][     ][     ]|
                                                      |  [____ ][____ ][____ ]|
                                                      |                       |
                                                      |   ______     __       |
                                                      |  |      |   |  |      |
                                                      |  |  O   |   |  |      |
                                                      |  |______|   |__|      |
                                                      |_______________________|
          
          
          
          ''')
    time.sleep(1)
    print("Welcome to my Vending Machine!")
    time.sleep(1)
    print("Checking for existing products in the database...")
    time.sleep(2)
    main()