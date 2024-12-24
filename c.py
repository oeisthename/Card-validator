import tkinter as tk
from tkinter import PhotoImage, messagebox
from tkinter import ttk
import hashlib
import sqlite3
import requests
import re
import math
from collections import Counter

# Hashing Function for BIN Numbers
def hash_bin(bin_prefix):
    return hashlib.sha256(bin_prefix.encode()).hexdigest()

# Calculate entropy for a given BIN prefix
def calculate_entropy(bin_prefix):
    counts = Counter(bin_prefix)
    entropy = -sum((count / len(bin_prefix)) * math.log2(count / len(bin_prefix)) for count in counts.values())
    return entropy

# Check if a BIN prefix is likely fraudulent based on entropy
def is_fraudulent_bin(bin_prefix):
    entropy = calculate_entropy(bin_prefix)
    return entropy < 1.5 or entropy > 3.8  # Adjust thresholds based on analysis

# Create SQLite database and table
def create_database():
    conn = sqlite3.connect('bin_lookup.db')  # Create or connect to the database
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS bin_data (
            bin_hash TEXT PRIMARY KEY,
            bank_name TEXT,
            country TEXT,
            card_level TEXT,
            card_category TEXT,
            issuer_phone TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Save hashed BIN data to the database
def save_bin_to_db(bin_prefix, bank_name, country, card_level, card_category, issuer_phone):
    bin_hash = hash_bin(bin_prefix)
    conn = sqlite3.connect('bin_lookup.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT OR REPLACE INTO bin_data (bin_hash, bank_name, country, card_level, card_category, issuer_phone)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (bin_hash, bank_name, country, card_level, card_category, issuer_phone))
    conn.commit()
    conn.close()

# Check if the hashed BIN exists in the database
def get_bin_from_db(bin_prefix):
    bin_hash = hash_bin(bin_prefix)
    conn = sqlite3.connect('bin_lookup.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bin_data WHERE bin_hash = ?', (bin_hash,))
    result = cursor.fetchone()
    conn.close()
    return result

# Card Validation using Luhn Algorithm
def luhn_validate(card_number):
    card_number = [int(digit) for digit in str(card_number)]
    for i in range(len(card_number) - 2, -1, -2):
        doubled = card_number[i] * 2
        card_number[i] = doubled - 9 if doubled > 9 else doubled
    return sum(card_number) % 10 == 0

def format_card_number(event):
    text = entry_card.get().replace(" ", "")  # Remove existing spaces
    formatted = " ".join(text[i:i+4] for i in range(0, len(text), 4))
    entry_card.delete(0, tk.END)
    entry_card.insert(0, formatted)

def validate_card():
    # Clear previous results
    result_label.config(text="", foreground="blue")
    fraud_label.config(text="", foreground="red")
    entropy_label.config(text="", foreground="green")
    
    card_number = entry_card.get().replace(" ", "")  # Remove spaces for validation
    if len(card_number) != 16:
        messagebox.showerror("Input Error", "Card number must be 16 digits.")
        return

    if not card_number.isdigit():
        messagebox.showerror("Input Error", "Card number must contain digits only.")
        return

    if luhn_validate(card_number):
        result_label.config(text="\u2705 Valid Card Number", foreground="green")
    else:
        result_label.config(text="\u274C Invalid Card Number", foreground="red")

def lookup_bin():
    # Clear previous results
    result_label.config(text="", foreground="blue")
    fraud_label.config(text="", foreground="red")
    entropy_label.config(text="", foreground="green")
    
    card_number = entry_card.get().replace(" ", "")  # Remove spaces for BIN lookup
    if not card_number.isdigit() or len(card_number) < 6:
        messagebox.showerror("Input Error", "Card number must be at least 6 digits for BIN lookup.")
        return
    if not luhn_validate(card_number):
        messagebox.showerror("Invalid Card", "The card number is invalid. Please enter a valid card number.")
        return

    bin_prefix = card_number[:6]  # Get the first 6 digits (BIN)

    # Check if the result is cached in the database
    existing_data = get_bin_from_db(bin_prefix)
    result_text = ""

    # Calculate entropy
    entropy = calculate_entropy(bin_prefix)

    # Default fraud check status
    fraud_status = ""
    if is_fraudulent_bin(bin_prefix):
        fraud_status = "\u26A0 Fraudulent BIN Detected (Entropy Out of Range)"

    if existing_data:
        result_text = (
            f"\U0001F50E Card Type: {detect_card_type(card_number)}\n"
            f"Card Level: {existing_data[3]}\n"
            f"Card Category: {existing_data[4]}\n"
            f"Bank: {existing_data[1]}\n"
            f"Country: {existing_data[2]}\n"
            f"Issuer Phone: {existing_data[5]}"
        )
    else:
        # API URLs
        api_urls = [
            f"https://lookup.binlist.net/{bin_prefix}",  # First API
        ]

        for api_url in api_urls:
            try:
                response = requests.get(api_url)

                if response.status_code == 429:  # Rate limit error
                    result_label.config(text="\u274C Rate limit exceeded. Please try again later.")
                    return

                if response.status_code != 200:
                    continue  # Try the next API if the current one fails

                response_data = response.json()

                if "bank" in response_data:
                    bank_name = response_data["bank"].get("name", "Unknown Bank")
                    country = response_data["country"].get("name", "Unknown Country")
                    card_level = response_data.get("level", "Unknown Level")
                    card_category = response_data.get("type", "Unknown Type")
                    issuer_phone = response_data["bank"].get("phone", "No contact details available")

                    result_text = (
                        f"\U0001F50E Card Type: {detect_card_type(card_number)}\n"
                        f"Card Level: {card_level}\n"
                        f"Card Category: {card_category}\n"
                        f"Bank: {bank_name}\n"
                        f"Country: {country}\n"
                        f"Issuer Phone: {issuer_phone}"
                    )

                    save_bin_to_db(bin_prefix, bank_name, country, card_level, card_category, issuer_phone)
                    break  # Exit the loop if successful

            except Exception as e:
                print("Error during BIN lookup:", e)

    if result_text:
        result_label.config(text=result_text)
        if fraud_status:
            fraud_label.config(text=fraud_status, foreground="red")
            entropy_label.config(text="")
        else:
            fraud_label.config(text="")
            entropy_label.config(text=f"Entropy: {entropy:.2f}", foreground="green")
    else:
        result_label.config(text=f"\U0001F50E Card Network: Unknown (BIN not found)")
        if fraud_status:
            fraud_label.config(text=fraud_status, foreground="red")
            entropy_label.config(text="")
        else:
            fraud_label.config(text="")
            entropy_label.config(text=f"Entropy: {entropy:.2f}", foreground="green")

# Card Type Detection
def detect_card_type(card_number):
    if re.match(r"^4[0-9]{12}(?:[0-9]{3})?$", card_number):
        return "Visa"
    elif re.match(r"^5[1-5][0-9]{14}$", card_number):
        return "MasterCard"
    elif re.match(r"^3[47][0-9]{13}$", card_number):
        return "American Express"
    elif re.match(r"^3(?:0[0-5]|[68][0-9])[0-9]{11}$", card_number):
        return "Diners Club"
    elif re.match(r"^6(?:011|5[0-9]{2})[0-9]{12}$", card_number):
        return "Discover"
    elif re.match(r"^(?:2131|1800|35\d{3})\d{11}$", card_number):
        return "JCB"
    else:
        return "Unknown"

# Function to toggle card number visibility
def toggle_card_visibility():
    if entry_card.cget("show") == "*":
        entry_card.config(show="")
        eye_icon.config(image=eye_open_icon)  # Change to eye-open icon
    else:
        entry_card.config(show="*")
        eye_icon.config(image=eye_closed_icon)  # Change to eye-closed icon

# GUI Setup
root = tk.Tk()
root.title("Credit Card Validator & BIN Checker with Fraud Detection")
root.geometry("600x700")
root.configure(bg="#f7f7f7")

# Title label
title_label = ttk.Label(root, text="Credit Card Validator & BIN Checker", font=("Helvetica", 16, "bold"), background="#f7f7f7")
title_label.pack(pady=20)

# Label for entering card number
label_input = ttk.Label(root, text="Enter Credit Card Number:" ,font=("Helvetica", 12, "bold"), background="#f7f7f7")
label_input.pack(pady=5)

# Frame for the card number input and toggle button
input_frame = ttk.Frame(root)
input_frame.pack(pady=10)

# Entry widget for card number
entry_card = ttk.Entry(input_frame, width=30, font=("Helvetica", 14), show="*")
entry_card.pack(side=tk.LEFT, padx=5)

# Load and resize eye icons
eye_open_icon = PhotoImage(file="eye_open.png").subsample(21, 21)  # Rescale by a factor of 3
eye_closed_icon = PhotoImage(file="eye_closed.png").subsample(21, 21)

# Button with eye icon to toggle card visibility
eye_icon = ttk.Button(input_frame, image=eye_closed_icon, command=toggle_card_visibility, style="TButton")
eye_icon.pack(side=tk.LEFT)

# Bind the format_card_number function to entry_card to format the number as user types
entry_card.bind("<KeyRelease>", format_card_number)

# Result label for validation feedback
result_label = ttk.Label(root, text="", font=("Helvetica", 12), foreground="blue", background="#f7f7f7")
result_label.pack(pady=10)

# Fraud label
fraud_label = ttk.Label(root, text="", font=("Helvetica", 12), foreground="red", background="#f7f7f7")
fraud_label.pack(pady=5)

# Entropy label
entropy_label = ttk.Label(root, text="", font=("Helvetica", 12), foreground="green", background="#f7f7f7")
entropy_label.pack(pady=5)

# Style for the buttons
style = ttk.Style()
style.configure("TButton",
                font=("Helvetica", 14, "bold"),
                padding=10,
                relief="solid",
                width=20,
                anchor="center",
                background="#4CAF50",  # Green background
                foreground="black")

# Card validation button
btn_validate = ttk.Button(root, text="Validate Card", command=validate_card, style="TButton")
btn_validate.pack(pady=10)

# BIN lookup button
btn_lookup = ttk.Button(root, text="BIN Lookup", command=lookup_bin, style="TButton")
btn_lookup.pack(pady=10)

# Initialize the database
create_database()

root.mainloop()
