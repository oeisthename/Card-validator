import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd

def display_table_in_gui(file_name):
    try:
        # Connect to the database
        conn = sqlite3.connect(file_name)
        cursor = conn.cursor()

        # Fetch the table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
            return
        
        # Fetch data from the first table (modify as needed for multiple tables)
        table_name = tables[0][0]
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

        # Close the database connection
        conn.close()

        # Create the GUI window
        root = tk.Tk()
        root.title(f"Database Viewer: {file_name}")

        # Create a Treeview widget to display the table
        tree = ttk.Treeview(root, columns=list(df.columns), show='headings')

        # Add column headings
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor=tk.CENTER)  # Adjust width as needed

        # Add rows to the Treeview
        for _, row in df.iterrows():
            tree.insert("", tk.END, values=list(row))

        # Pack the Treeview widget
        tree.pack(expand=True, fill=tk.BOTH)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Run the GUI
        root.mainloop()

    except Exception as e:
        print(f"Error displaying database content: {e}")

# Call the function with your database file name
display_table_in_gui("bin_lookup.db")
