import sqlite3
import datetime


class RestaurantDB:

    def __init__(self, db_name="restaurant.db"):
        self.db_name = db_name
        self.create_tables()
        self.seed_data()


    def create_tables(self):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)""")

            cur.execute("""CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, stock_quantity INTEGER, image_filename TEXT)""")

            cur.execute("""CREATE TABLE IF NOT EXISTS table_orders (
                id INTEGER PRIMARY KEY, table_id INTEGER, product_name TEXT, price REAL, quantity INTEGER, timestamp DATETIME)""")

            cur.execute("""CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY, table_id INTEGER, total_amount REAL, timestamp DATETIME)""")

    def seed_data(self):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()

            cur.execute("SELECT count(*) FROM users")
            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))

            cur.execute("SELECT count(*) FROM menu")
            if cur.fetchone()[0] == 0:
                items = [

                    ("Steak Frites", "Food", 25.00, 50, "steakfries.png"),
                    ("Roast Chicken", "Food", 18.50, 40, "RoasChicken.png"),
                    ("Creme Brulee", "Food", 15.00, 60, "CremeBrulee.png"),
                    ("Caesar Salad", "Food", 12.00, 50, "CeaserSlad.png"),
                    ("Fish & Chips", "Food", 16.00, 40, "FishAndChips.png"),
                    ("Carbonara", "Food", 17.00, 45, "PastaCarbonara.png"),
                    ("Club Sandwich", "Food", 14.00, 50, "ClubSandwich.png"),
                    ("Pizza", "Food", 9.00, 60, "pizza.png"),


                    ("Mineral Water", "Drink", 3.00, 100, "MineralWater.png"),
                    ("Cola", "Drink", 3.50, 100, "Cola.png"),
                    ("Lemonade", "Drink", 4.00, 80, "Lemonade.png"),
                    ("Iced Tea", "Drink", 3.50, 80, "IceTea.png"),
                    ("House Wine", "Drink", 8.00, 50, "Wine.png"),
                    ("Draft Beer", "Drink", 6.00, 60, "Beer.png"),
                    ("Espresso", "Drink", 3.00, 100, "Espresso.png"),


                    ("NY Cheesecake", "Dessert", 8.50, 30, "nycheesecake.png"),
                    ("Lava Cake", "Dessert", 9.00, 30, "lavacake.png"),
                    ("Apple Pie", "Dessert", 7.50, 30, "applepie.png"),
                    ("Creme Brulee", "Dessert", 8.00, 25, "CremeBrulee.png"),
                    ("Tiramisu", "Dessert", 8.50, 25, "tiramisu.png"),
                    ("Ice Cream", "Dessert", 6.00, 40, "icecream.png"),
                    ("Brownie", "Dessert", 5.00, 50, "brownie.png")
                ]
                cur.executemany(
                    "INSERT INTO menu (name, category, price, stock_quantity, image_filename) VALUES (?, ?, ?, ?, ?)",
                    items)


    def get_connection(self):
        return sqlite3.connect(self.db_name)
#sort the database for username and password,return True if match is found,False otherwise
    def check_login(self, username, password):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            return cur.fetchone() is not None


#retrieve id,name,category,price,stock quant,and image from menu
    def get_menu(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, category, price, stock_quantity, image_filename FROM menu")
            return cur.fetchall()
#only return rows where category is matched,
    def get_menu_by_category(self, category):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, category, price, stock_quantity, image_filename FROM menu WHERE category=?",
                        (category,))
            return cur.fetchall()

    def add_menu_item(self, name, category, price, qty, img_name=""):
        with self.get_connection() as conn:
            cur = conn.cursor()
            #need to check if you need to add the existing item for example 5 more cola to cola with quantity 40
            cur.execute("SELECT id, stock_quantity FROM menu WHERE name=? AND category=? AND price=?",
                        (name, category, price))
            row = cur.fetchone()
            #update the existing database
            if row:
                new_qty = row[1] + qty
                cur.execute("UPDATE menu SET stock_quantity=? WHERE id=?", (new_qty, row[0]))
            else:
                #insert the new product
                cur.execute(
                    "INSERT INTO menu (name, category, price, stock_quantity, image_filename) VALUES (?, ?, ?, ?, ?)",
                    (name, category, price, qty, img_name))

    #find how many stock you have for that item compared to if its in occupied or in the inventory
    def get_available_stock(self, product_name):
        with self.get_connection() as conn:
            cur = conn.cursor()
            #select for example 10 existing pizza for pizza product
            cur.execute("SELECT stock_quantity FROM menu WHERE name=?", (product_name,))
            res = cur.fetchone()
            if not res: return 0
            total_stock = res[0]
            #look for how many of those items are being eaten(occupied) table 1 = 1 burgers table 2 = 2 active_qty = 3 ; return total stock;
            #it is to see how many more we can sell.
            #You had 10 burger , 3 are occupied by table 1 and table 2 and table 3 just came in and wanted 15 burgers.Normally
            #system would say yes but with this logic active_qty are frozen in time for the time being
            cur.execute("SELECT SUM(quantity) FROM table_orders WHERE product_name=?", (product_name,))
            res_active = cur.fetchone()
            active_qty = res_active[0] if res_active[0] else 0
            return total_stock - active_qty

    def deduct_stock_on_payment(self, table_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            #get the table order with product name and quantity with table id Steak,2 Cola,3
            cur.execute("SELECT product_name, quantity FROM table_orders WHERE table_id=?", (table_id,))
            items = cur.fetchall()
            for name, qty in items:
                #remove the items
                cur.execute("UPDATE menu SET stock_quantity = stock_quantity - ? WHERE name=?", (qty, name))
            conn.commit()


    def get_table_items(self, table_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT product_name, price, quantity FROM table_orders WHERE table_id=?", (table_id,))
            return cur.fetchall()

    def get_table_total(self, table_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            #get the receipts for the table's not the irrelevant tables
            #grab total price price*quantity burger 12,50,1 Cola,3,2
            cur.execute("SELECT SUM(price * quantity) FROM table_orders WHERE table_id=?", (table_id,))
            result = cur.fetchone()[0]
            return result if result else 0.0

    def get_table_start_time(self, table_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            #select the minimum(earliest)time for occupied time for example Food 12:30 drink 12:35 and dessert 12.50
            cur.execute("SELECT MIN(timestamp) FROM table_orders WHERE table_id=?", (table_id,))
            res = cur.fetchone()
            if res and res[0]:
                #if an a table is empty it will return none
                return datetime.datetime.fromisoformat(res[0])
            return None

    def add_to_table(self, table_id, name, price, qty):
        with self.get_connection() as conn:
            cur = conn.cursor()
            now = datetime.datetime.now().isoformat()
            #check if it has already the same item for example table 4 has pizza and order pizzar then make 2 pizza
            cur.execute("SELECT quantity FROM table_orders WHERE table_id=? AND product_name=?", (table_id, name))
            row = cur.fetchone()
            if row:
                #update the row
                new_qty = row[0] + qty
                cur.execute("UPDATE table_orders SET quantity=? WHERE table_id=? AND product_name=?",
                            (new_qty, table_id, name))
            else:
                #add the new item form example cola wasn't found,add it
                cur.execute(
                    "INSERT INTO table_orders (table_id, product_name, price, quantity, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (table_id, name, price, qty, now))

    def delete_order_item(self, table_id, name):
        with self.get_connection() as conn:
            cur = conn.cursor()
            #delete the ordered item from that specific table
            cur.execute("DELETE FROM table_orders WHERE table_id=? AND product_name=?", (table_id, name))

    def clear_table(self, table_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            #delete the table from existing all together indicating that table has just been emptied
            cur.execute("DELETE FROM table_orders WHERE table_id=?", (table_id,))

    def record_sale(self, table_id, total):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO sales (table_id, total_amount, timestamp) VALUES (?, ?, ?)",
                        (table_id, total, datetime.datetime.now()))

    def get_sales_history(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, table_id, total_amount, timestamp FROM sales ORDER BY id DESC")
            return cur.fetchall()

    def get_sales_grouped_by_table(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT table_id, SUM(total_amount) FROM sales GROUP BY table_id ORDER BY table_id")
            return cur.fetchall()