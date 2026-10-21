import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from db_manager import RestaurantDB
from PIL import Image, ImageTk
import os
import sys
import datetime


THEME_NAME = "cosmo"

#all the colors we need throught the program
COLOR_PRIMARY = "#673AB7"  # purple
COLOR_SUCCESS = "#00C853"  # green
COLOR_DANGER = "#D50000"   # red
COLOR_WARNING = "#FFC107"  # yellow
COLOR_DARK = "#343a40"     # grey

# fonts
HEADER_FONT = ("Segoe UI", 20, "bold")
LOGO_FONT = ("Segoe UI", 24, "bold")
NORMAL_FONT = ("Segoe UI", 12)
TABLE_FONT = ("Segoe UI", 11, "bold")

# start data base except there is no data base
try:
    db = RestaurantDB()
except Exception as e:
    messagebox.showerror("Database Error", f"Could not start database: {e}")


# load the image
class ImageLoader:
    cache = {}

    @staticmethod
    def get_base_path():
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return base_path

    @staticmethod
    def get_image(filename, size=(100, 80)):
        if not filename: return None
        if filename in ImageLoader.cache: return ImageLoader.cache[filename]
        try:
            base_folder = ImageLoader.get_base_path()
            full_path = os.path.join(base_folder, filename)
            if os.path.exists(full_path):
                image = Image.open(full_path)
                image = image.resize(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                ImageLoader.cache[filename] = photo
                return photo
            return None
        except Exception as e:
            print(f"Error loading image {filename}: {e}")
            return None


# app
class RestaurantApp(tb.Window):
    def __init__(self):
        #inherit theme
        super().__init__(themename=THEME_NAME)
        #makes it so that closing one window doesn't collapse the whole program
        self.withdraw()

        style = tb.Style()
        style.configure("Primary.TFrame", background=COLOR_PRIMARY)
        style.configure("Primary.TLabel", background=COLOR_PRIMARY, foreground="white")
        style.configure("Success.TButton", background=COLOR_SUCCESS, borderwidth=0, font=TABLE_FONT)
        style.map("Success.TButton", background=[('active', '#009624')])
        style.configure("Danger.TButton", background=COLOR_DANGER, borderwidth=0, font=TABLE_FONT)
        style.map("Danger.TButton", background=[('active', '#B71C1C')])
        style.configure("TButton", font=NORMAL_FONT)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

        LoginWindow(self)


# login
class LoginWindow(tb.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title("Staff Login")
        self.geometry("400x500")
        self.root = root
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        header = tb.Frame(self, bootstyle="primary", padding=20)
        header.pack(fill=X)
        tb.Label(header, text="OPTIMUS POS", font=LOGO_FONT, bootstyle="inverse-primary").pack()

        frame = tb.Frame(self, padding=40)
        frame.pack(expand=True, fill=BOTH)

        tb.Label(frame, text="Staff Login", font=("Segoe UI", 16), foreground=COLOR_PRIMARY).pack(pady=(0, 20))

        self.ent_user = tb.Entry(frame, font=NORMAL_FONT)
        self.ent_user.pack(pady=10, fill=X, ipady=5)
        #prefill
        self.ent_user.insert(0, "admin")
        #hide the actual password with star sign
        self.ent_pass = tb.Entry(frame, show="*", font=NORMAL_FONT)
        self.ent_pass.pack(pady=10, fill=X, ipady=5)
        #prefill
        self.ent_pass.insert(0, "1234")

        tb.Button(frame, text="LOGIN", bootstyle="success", width=10,
                  command=self.login).pack(pady=40, fill=X, ipady=10)

    def login(self):
        #login if you match the user and pass from the data base if not give error
        if db.check_login(self.ent_user.get(), self.ent_pass.get()):
            self.withdraw()
            MainMenu(self.root)
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    def on_close(self):
        #prevents collapsing altogether
        self.root.destroy()


# main menu 4 buttons
class MainMenu(tb.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title("Main Menu")
        self.geometry("800x600")
        self.root = root
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        header = tb.Frame(self, padding=20)
        header.configure(bootstyle="primary")
        header.pack(fill=X)

        tb.Label(header, text="OPTIMUS", font=LOGO_FONT, foreground="white", background=COLOR_PRIMARY).pack(side=LEFT)
        tb.Label(header, text="POS", font=LOGO_FONT, foreground="white", background=COLOR_PRIMARY).pack(side=LEFT,
                                                                                                        padx=5)

        btn_frame = tb.Frame(self)
        btn_frame.pack(expand=True)

        tb.Button(btn_frame, text="SALON / TABLES", bootstyle="success", width=30,
                  command=lambda: FloorPlan(self.root)).pack(pady=15, ipady=15)

        tb.Button(btn_frame, text="INVENTORY", bootstyle="info", width=30,
                  command=lambda: InventoryWindow(self.root)).pack(pady=15, ipady=15)

        tb.Button(btn_frame, text="REPORTS", bootstyle="warning", width=30,
                  command=lambda: HistoryWindow(self.root)).pack(pady=15, ipady=15)

        tb.Button(btn_frame, text="EXIT", bootstyle="danger", width=30,
                  command=self.on_close).pack(pady=40, ipady=5)

    def on_close(self):
        self.root.destroy()


#
class FloorPlan(tb.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title("Salon")
        self.geometry("1000x750")

        header = tb.Frame(self, height=80, padding=10)
        header.configure(style="Primary.TFrame")
        header.pack(fill=X)

        tb.Button(header, text="← Back", bootstyle="light", command=self.destroy).pack(side=LEFT, padx=10)
        tb.Label(header, text="OPTIMUS SALON", font=HEADER_FONT, background=COLOR_PRIMARY, foreground="white").pack(
            side=LEFT, padx=20)

        self.grid_frame = tb.Frame(self, padding=20)
        self.grid_frame.pack(expand=True, fill=BOTH)

        self.refresh_tables()
        self.after(60000, self.refresh_tables)

    def refresh_tables(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        for i in range(1, 21):
            #loop through all the tables
            row = (i - 1) // 5
            col = (i - 1) % 5

            total = db.get_table_total(i)
            start_time = db.get_table_start_time(i)

            time_str = ""
            if start_time:
                #get the occupied time
                diff = datetime.datetime.now() - start_time
                minutes = int(diff.total_seconds() / 60)
                time_str = f"{minutes // 60:02d}:{minutes % 60:02d}"

            if total > 0:
                #if total is greater than 0 meaning it is occupied make the layout red
                btn_text = f"{time_str:>15}\n\n{i:02d}\nOccupied\n${total:.2f}"
                btn_style = "danger"
            else:
                #else it is not occupied it means its normal
                btn_text = f"\n\n{i:02d}\nFree"
                btn_style = "success"

            btn = tb.Button(self.grid_frame, text=btn_text, bootstyle=btn_style, width=15,
                            command=lambda t=i: self.open_table(t))
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew", ipady=20)

        for r in range(4): self.grid_frame.rowconfigure(r, weight=1)
        for c in range(5): self.grid_frame.columnconfigure(c, weight=1)

    def open_table(self, table_id):
        TableDetailWindow(self.master, table_id, self)


# order table
class TableDetailWindow(tb.Toplevel):
    def __init__(self, root, table_id, floor_plan):
        super().__init__(root)
        self.title(f"Table {table_id}")
        self.geometry("1200x800")
        self.table_id = table_id
        self.floor_plan = floor_plan
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        header = tb.Frame(self, padding=10, style="Primary.TFrame")
        header.pack(fill=X)
        tb.Label(header, text=f"Table {table_id} Order", font=HEADER_FONT, background=COLOR_PRIMARY,
                 foreground="white").pack(side=LEFT, padx=10)

        content = tb.Frame(self)
        content.pack(fill=BOTH, expand=True)

        left_panel = tb.Frame(content, padding=10)
        left_panel.pack(side=LEFT, fill=BOTH, expand=True)

        notebook = ttk.Notebook(left_panel)
        notebook.pack(fill=BOTH, expand=True)

        for cat in ["Food", "Drink", "Dessert"]:
            frame = tb.Frame(notebook, padding=10)
            notebook.add(frame, text=cat)
            self.create_menu_grid(frame, cat)

        right_panel = tb.Frame(content, padding=10, bootstyle="light")
        right_panel.pack(side=RIGHT, fill=BOTH, expand=False, ipadx=20)

        self.order_tree = ttk.Treeview(right_panel, columns=("Item", "Price", "Qty"), show="headings", height=20)
        self.order_tree.heading("Item", text="Item");
        self.order_tree.column("Item", width=150)
        self.order_tree.heading("Price", text="Price");
        self.order_tree.column("Price", width=60)
        self.order_tree.heading("Qty", text="Qty");
        self.order_tree.column("Qty", width=40)
        self.order_tree.pack(fill=BOTH, expand=True, pady=(0, 10))

        tb.Button(right_panel, text="🗑️ Remove Selected", bootstyle="danger", command=self.delete_item).pack(fill=X,
                                                                                                             pady=5)
        self.lbl_total = tb.Label(right_panel, text="Total: $0.00", font=("Segoe UI", 22, "bold"),
                                  bootstyle="inverse-light", foreground=COLOR_PRIMARY)
        self.lbl_total.pack(pady=20)
        tb.Button(right_panel, text="PAY & CLOSE", bootstyle="warning", width=20, command=self.pay_bill).pack(
            side=BOTTOM, fill=X, pady=10, ipady=10)

        self.update_order_list()

    def create_menu_grid(self, parent, category):
        items = db.get_menu_by_category(category)
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        cols = 3
        for i, item in enumerate(items):
            #item 0 row 0 col 0
            #item 1 row 0 col 1
            #item 2 row 0 col 2
            # ..................
            #add items with their image stock and price
            name, price, img_file = item[1], item[3], item[5]
            stock = db.get_available_stock(name)
            photo = ImageLoader.get_image(img_file)
            txt = f"{name}\n${price:.2f}\nStock: {stock}"
            style = "info-outline" if stock > 0 else "secondary"
            btn = tb.Button(scrollable_frame, text=txt, image=photo, compound=TOP, bootstyle=style,
                            command=lambda n=name, p=price: self.add_item(n, p))
            if not photo: btn.config(text=f"\n{txt}\n")
            btn.grid(row=i // cols, column=i % cols, padx=5, pady=5, sticky="nsew", ipady=10)
        for i in range(cols): scrollable_frame.columnconfigure(i, weight=1)

    def add_item(self, name, price):
        #if quantity drops to 0 error popsup
        if db.get_available_stock(name) <= 0:
            messagebox.showwarning("Stock", "Out of stock!", parent=self)
            return
        db.add_to_table(self.table_id, name, price, 1)
        self.update_order_list()

    def delete_item(self):
        sel = self.order_tree.selection()
        if sel:
            #get the name of the item from selected row
            name = self.order_tree.item(sel[0])['values'][0]
            if messagebox.askyesno("Remove", f"Remove '{name}'?", parent=self):
                db.delete_order_item(self.table_id, name)
                self.update_order_list()
        else:
            messagebox.showinfo("Select", "Select an item first", parent=self)

    def update_order_list(self):
        for i in self.order_tree.get_children(): self.order_tree.delete(i)
        items = db.get_table_items(self.table_id)
        #calculate new order Stek 25,0 , 1 Cola  3,5 2
        total = sum(i[1] * i[2] for i in items)
        for i in items: self.order_tree.insert("", "end", values=i)
        self.lbl_total.config(text=f"Total: ${total:.2f}")
        self.current_total = total

    def pay_bill(self):
        if self.current_total > 0:
            db.deduct_stock_on_payment(self.table_id)
            db.record_sale(self.table_id, self.current_total)
            db.clear_table(self.table_id)
            self.close_window()
        else:
            messagebox.showinfo("Info", "Table empty", parent=self)

    def close_window(self):
        self.floor_plan.refresh_tables()
        self.destroy()


# inventory
class InventoryWindow(tb.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.geometry("850x600")
        h = tb.Frame(self, padding=15, style="Primary.TFrame")
        h.pack(fill=X)
        tb.Label(h, text="INVENTORY MANAGER", font=HEADER_FONT, background=COLOR_PRIMARY, foreground="white").pack(
            side=LEFT)
        tb.Button(h, text="Close", bootstyle="light", command=self.destroy).pack(side=RIGHT)

        form = tb.Labelframe(self, text="Add Item", padding=20)
        form.pack(fill=X, padx=20, pady=20)
        self.en = tb.Entry(form, width=20);
        self.en.pack(side=LEFT, padx=5);
        self.en.insert(0, "Item Name")
        self.cat = tb.Combobox(form, values=["Food", "Drink", "Dessert"], width=10);
        self.cat.pack(side=LEFT, padx=5);
        self.cat.current(0)
        self.ep = tb.Entry(form, width=10);
        self.ep.pack(side=LEFT, padx=5);
        self.ep.insert(0, "Price")
        self.eq = tb.Entry(form, width=10);
        self.eq.pack(side=LEFT, padx=5);
        self.eq.insert(0, "Qty")
        tb.Button(form, text="ADD/UPDATE", bootstyle="success", command=self.add).pack(side=LEFT, padx=20)

        self.tree = ttk.Treeview(self, columns=("Name", "Category", "Price", "Stock"), show="headings", height=15)
        for c in ("Name", "Category", "Price", "Stock"): self.tree.heading(c, text=c)
        self.tree.pack(fill=BOTH, expand=True, padx=20, pady=20)
        self.refresh()

    def add(self):
        try:
            #add items to the inventory
            db.add_menu_item(self.en.get(), self.cat.get(), float(self.ep.get()), int(self.eq.get()))
            self.refresh()
            self.en.delete(0, END);
            self.ep.delete(0, END);
            self.eq.delete(0, END)
        except:
            messagebox.showerror("Error", "Check inputs", parent=self)

    def refresh(self):
        #refresh after entering it to the inventory for quick adding
        for i in self.tree.get_children(): self.tree.delete(i)
        for i in db.get_menu(): self.tree.insert("", "end", values=(i[1], i[2], f"${i[3]:.2f}", i[4]))


# chart sales etc.
class HistoryWindow(tb.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.geometry("900x750")

        h = tb.Frame(self, padding=15, style="Primary.TFrame")
        h.pack(fill=X)
        tb.Label(h, text="SALES REPORTS (Today)", font=HEADER_FONT, background=COLOR_PRIMARY, foreground="white").pack(
            side=LEFT)
        tb.Button(h, text="Close", bootstyle="light", command=self.destroy).pack(side=RIGHT)


        tb.Label(self, text="Transaction Log", font=("Segoe UI", 12, "bold"), padding=(20, 10, 0, 0)).pack(anchor="w")
        self.tree = ttk.Treeview(self, columns=("ID", "Table", "Total", "Time"), show="headings", height=8)
        for c in ("ID", "Table", "Total", "Time"): self.tree.heading(c, text=c)
        self.tree.pack(fill=X, padx=20, pady=5)

        # chart
        tb.Label(self, text="Total Daily Sales (Tables 1-20)", font=("Segoe UI", 12, "bold"),
                 padding=(20, 10, 0, 0)).pack(anchor="w")
        self.canvas = tk.Canvas(self, bg="white", height=300, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True, padx=20, pady=20)

        self.load_data()

    def load_data(self):
        sales = db.get_sales_history()
        for s in sales:
            self.tree.insert("", "end", values=(s[0], s[1], f"${s[2]:.2f}", s[3][:16]))

        # Chart Logic
        table_totals = {i: 0.0 for i in range(1, 21)}
        today_str = datetime.date.today().isoformat()

        for s in sales:
            if s[3].startswith(today_str):
                t_id = s[1]
                if 1 <= t_id <= 20: table_totals[t_id] += s[2]

        self.canvas.delete("all")
        max_total = max(table_totals.values())
        if max_total == 0: max_total = 100

        c_width = 860;
        c_height = 300;
        x_margin = 40;
        y_base = 250
        available_width = c_width - (2 * x_margin)
        slot_width = available_width / 20
        bar_width = slot_width * 0.6

        for i in range(1, 21):
            total = table_totals[i]
            bar_height = (total / max_total) * 200
            x_center = x_margin + (i - 1) * slot_width + (slot_width / 2)

            color = COLOR_PRIMARY if total > 0 else "#e0e0e0"
            self.canvas.create_rectangle(x_center - bar_width / 2, y_base - bar_height, x_center + bar_width / 2,
                                         y_base, fill=color, outline="")

            if total > 0:
                self.canvas.create_text(x_center, y_base - bar_height - 10, text=f"${int(total)}", font=("Segoe UI", 8),
                                        fill=COLOR_DARK)

            self.canvas.create_text(x_center, y_base + 15, text=f"{i:02d}", font=("Segoe UI", 9))


if __name__ == "__main__":
    app = RestaurantApp()
    app.mainloop()