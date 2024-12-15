import sqlite3

class DBUtils:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect_and_create(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    name VARCHAR UNIQUE PRIMARY KEY,
                    price FLOAT,
                    quantity INTEGER
                );
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS change (
                    type VARCHAR UNIQUE PRIMARY KEY,
                    quantity INTEGER
                );
            ''')
            self.conn.commit()
            return True
        except sqlite3.Error as err:
            print(f"Error connecting to database: {err}")
            return False
        
    def create_products_change(self, products, change):
        try:
            self.cursor.executemany('''
                INSERT OR IGNORE 
                INTO products(name, price, quantity)
                VALUES (?, ?, ?)''', products)
            self.cursor.executemany('''
                INSERT OR IGNORE
                INTO change (type, quantity) 
                VALUES(?, ?) ''', change)
            self.conn.commit()
        except sqlite3.Error as err:
            print(f"Error inserting data: {err}")

    def get_products_change(self):
        try:
            products = self.cursor.execute("SELECT * FROM products;").fetchall()
            change = self.cursor.execute("SELECT * FROM change;").fetchall()
            return products, change
        except sqlite3.Error as err:
            print(f"Error retrieving data: {err}")

    # This function can be used to reload products later
    def update_product_quantity(self, product_name, new_quantity):
        try:
            self.cursor.execute('''
                UPDATE products
                SET quantity=?
                WHERE name=?;
            ''', [new_quantity, product_name])
            self.conn.commit()
        except sqlite3.Error as err:
            print(f"Error updating product data: {err}")
    
    # This function can be used to reload change later
    def update_changes(self, new_changes):
        try:
            self.cursor.executemany('''
                UPDATE change
                SET quantity=?
                WHERE type=?
            ''', new_changes)
            self.conn.commit()
        except sqlite3.Error as err:
            print(f"Error updating changes data: {err}")

    def save_and_disconnect(self):
        self.cursor.close()
        self.conn.close()

