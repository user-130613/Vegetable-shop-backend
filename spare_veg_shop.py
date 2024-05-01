import mysql.connector
import time

def connect_to_database(host, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def display_initial_menu(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM initial_menu2")
    rows = cursor.fetchall()
    print("Menu:")
    for row in rows:
        print(row)
    return rows

def display_sorted_menu(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM sorted_menu2")
    rows = cursor.fetchall()
    print("\nSorted Menu:")
    for row in rows:
        print(row)

def add_to_cart(connection, phn_no, veg_id, weight):
    cursor = connection.cursor()
    table_name = f"cart_{phn_no}"
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, veg_id INT, weight_in_kilograms DECIMAL(10, 2))")
    cursor.execute(f"INSERT INTO {table_name} (veg_id, weight_in_kilograms) VALUES (%s, %s)", (veg_id, weight))
    connection.commit()
    cursor.execute("SELECT amount_per_kg FROM initial_menu2 WHERE id = %s", (veg_id,))
    amount_per_kg = cursor.fetchone()[0]
    total_cost = amount_per_kg * weight
    print(f"\nAdded vegetable {veg_id} and weight {weight} kg to cart. \nTotal cost: Rs.{total_cost:.2f}")

def remove_from_cart_2(connection, phn_no, veg_id, weight):
    cursor = connection.cursor()
    table_name = f"cart_{phn_no}"
    cursor.execute(f"INSERT INTO {table_name} (veg_id, weight_in_kilograms) VALUES (%s, %s)", (veg_id, weight))
    connection.commit()
    cursor.execute("SELECT amount_per_kg FROM initial_menu2 WHERE id = %s", (veg_id,))
    amount_per_kg = cursor.fetchone()[0]
    total_cost = amount_per_kg * weight
    print(f"\nRemoved vegetable {veg_id} and {weight} kg(s) still in cart.\nTotal cost: Rs.{total_cost:.2f}")

def remove_from_cart(connection, phn_no, cart_id):
    cursor = connection.cursor()
    table_name = f"cart_{phn_no}"
    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE veg_id = %s", (cart_id,))
    count = cursor.fetchone()[0]
    if count > 0:
        cursor.execute(f"DELETE FROM {table_name} WHERE veg_id = %s", (cart_id,))
        connection.commit()
        print(f"\nRemoved item with ID {cart_id} from the cart.")
    else:
        print(f"\nItem with ID {cart_id} is not in the cart, so it cannot be removed.")

def display_individual_bill(connection, phn_no):
    cursor = connection.cursor()
    table_name = f"cart_{phn_no}"
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    if count == 0:
        print("No items in the cart. Cannot generate bill.")
        return

    cursor.execute(f"SELECT c.veg_id, i.name, c.weight_in_kilograms, i.amount_per_kg FROM {table_name} c JOIN initial_menu2 i ON c.veg_id = i.id")
    rows = cursor.fetchall()

    total_bill = 0
    print("\nIndividual Bill:")
    for row in rows:
        veg_id, veg_name, weight, amount_per_kg = row


        total_cost = float(amount_per_kg) * float(weight)
        total_bill += total_cost
        print(f"Vegetable ID: {veg_id}, Name: {veg_name}, Weight: {weight} kg, Total Cost: Rs.{total_cost:.2f}")

    print(f"\nTotal Bill for Customer {phn_no}: Rs.{total_bill:.2f}")
    connection.commit()
    cursor.close()

def salesman(connection,phn_no):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM cart")
    count = cursor.fetchone()[0]
    if count == 0:
        print("No items in the cart. Cannot generate bill.")
        return

    cursor.execute("SELECT c.veg_id, i.name, SUM(c.weight_in_kilograms) AS quantity, i.amount_per_kg FROM cart c JOIN initial_menu2 i ON c.veg_id = i.id GROUP BY c.veg_id, i.name, i.amount_per_kg")
    rows = cursor.fetchall()

    total_bill = 0
    print("\nSales Details:")
    for row in rows:
        veg_id, veg_name, quantity, amount_per_kg = row
        total_cost = amount_per_kg * quantity
        total_bill += total_cost
        print(f"Vegetable ID: {veg_id}, Name: {veg_name}, Quantity: {quantity}, Total Cost: Rs.{total_cost:.2f}")

    print(f"\nTotal Sales: Rs.{total_bill:.2f}")
    connection.commit()
    cursor.close()

def main():
    host = 'localhost'
    user = 'root'
    password = 'Glwec@2003'
    database = 'veg_shop'

    connection = connect_to_database(host, user, password, database)
    if connection is None:
        return
    print("**************WELCOME TO MY STORE**************")
    time.sleep(5)
    phn_no = input("Enter your phone number: ")

    while True:
        print("\n1. Display Initial Menu")
        time.sleep(1)
        print("2. Display Sorted Veggies")
        time.sleep(1)
        print("3. Add Vegetable to Cart")
        time.sleep(1)
        print("4. Remove Item from Cart")
        time.sleep(1)
        print("5. Bill Display")
        time.sleep(1)
        print("6. Total sales today")
        time.sleep(1)
        print("7. Exit")
        time.sleep(3)
        opt = input("Enter your choice (1-7): ")

        if opt == '1':
            initial_menu_rows = display_initial_menu(connection)
        elif opt == '2':
            display_sorted_menu(connection)
        elif opt == '3':
            veg_id = int(input("Enter the ID of the vegetable to add to the cart: "))
            weight = float(input("Enter the weight in kilograms: "))
            initial_menu_rows = display_initial_menu(connection)
            if any(row[0] == veg_id for row in initial_menu_rows):
                add_to_cart(connection, phn_no, veg_id, weight)
            else:
                print("\nInvalid vegetable ID.")
        elif opt == '4':
            print("1. Want to remove the vegetable completely")
            time.sleep(1)
            print("2. Want to remove a certain amount from the veg in cart")
            time.sleep(2)
            iid = int(input("Enter your option ID: "))
            rmv = int(input("Enter the ID of the item to remove from the cart: "))
            if iid == 1:
                remove_from_cart(connection, phn_no, rmv)
            elif iid == 2:
                rmv_kg = int(input("Enter the weight in kilograms (kgs): "))
                if weight < rmv_kg:
                    print("Weight entered is more than the kgs added in the cart")
                else:
                    remove_from_cart(connection, phn_no, rmv)
                    weight -= rmv_kg
                    initial_menu_rows = display_initial_menu(connection)
                    if any(row[0] == veg_id for row in initial_menu_rows):
                        remove_from_cart_2(connection, phn_no, veg_id, weight)
        elif opt == '5':
            display_individual_bill(connection, phn_no)
        elif opt == '6':
            psw = "manu_the_great"
            pswd = input("\nEnter the password to access: ")
            if psw == pswd:
                salesman(connection, phn_no)
            else:
                print("Incorrect Password")
        elif opt == '7':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

    connection.close()

if __name__ == "__main__":
    main()
