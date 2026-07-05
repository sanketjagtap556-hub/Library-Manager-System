import os
import sys
import json
import random
from typing import List, Dict, Optional

# ================= CONFIGURATION =================

ADMIN_PASSWORD = "123456@Sanket_Library"

def get_data_dir() -> str:
    """
    Returns the directory of the executable or script.
    This ensures persistent data storage when converted to an .exe.
    """
    if getattr(sys, 'frozen', False):
        # Running as a compiled PyInstaller executable
        return os.path.dirname(sys.executable)
    # Running as a standard Python script
    return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_data_dir()
BOOK_FILE = os.path.join(APP_DIR, "lib_data.json")
MEMBER_FILE = os.path.join(APP_DIR, "lib_member.json")


# ================= LIBRARY CLASS =================

class Library:
    def __init__(self, name: str):
        self.name = name
        # Load data into memory on startup
        self.books = self._load_data(BOOK_FILE)
        self.members = self._load_data(MEMBER_FILE)

    # ---------- FILE HANDLING ----------

    def _load_data(self, file_name: str) -> List[Dict]:
        """Loads JSON data safely. Returns empty list if file is missing."""
        if not os.path.exists(file_name):
            return []
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save_data(self, file_name: str, data: List[Dict]) -> None:
        """Saves data back to the JSON file."""
        try:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"\n[Error] Could not save data: {e}")

    def _save_books(self) -> None:
        self._save_data(BOOK_FILE, self.books)

    def _save_members(self) -> None:
        self._save_data(MEMBER_FILE, self.members)

    # ---------- SEARCHING ----------

    def find_book(self, title: str) -> Optional[Dict]:
        for book in self.books:
            if book["Title"].lower() == title.lower():
                return book
        return None

    def find_member(self, member_id: str) -> Optional[Dict]:
        for member in self.members:
            if member["ID"] == member_id:
                return member
        return None

    # ---------- ADMIN FUNCTIONS ----------

    def add_book(self, title: str, author: str, quantity: int) -> str:
        if quantity <= 0:
            return "Quantity must be greater than 0."

        existing_book = self.find_book(title)
        if existing_book:
            existing_book["Quantity"] += quantity
            self._save_books()
            return "Book quantity updated successfully."

        # Generate a simple unique ID
        new_id = f"B{len(self.books) + 1:04d}"
        
        self.books.append({
            "Id": new_id,
            "Title": title,
            "Author": author,
            "Status": "Available",
            "Quantity": quantity
        })
        self._save_books()
        return "Book added successfully."

    def remove_book(self, title: str) -> str:
        book = self.find_book(title)
        if book:
            self.books.remove(book)
            self._save_books()
            return "Book removed successfully."
        return "Book not found."

    def show_books(self) -> None:
        if not self.books:
            print("\nNo books available.\n")
            return

        print("\n" + "="*15 + " BOOK LIST " + "="*15)
        for index, book in enumerate(self.books, start=1):
            status = "Available" if book.get("Quantity", 0) > 0 else "Unavailable"
            print(f"{index:02d}. {book['Title']:<35} | {book.get('Author', 'Unknown'):<20} | Qty: {book.get('Quantity', 0):<3} | {status}")
        print("="*41 + "\n")

    # ---------- MEMBER FUNCTIONS ----------

    def search_by_title(self, title: str) -> str:
        book = self.find_book(title)
        if not book:
            return "Book not found."

        status = "Available" if book.get("Quantity", 0) > 0 else "Unavailable"
        return f"\nTitle: {book['Title']}\nAuthor: {book.get('Author', 'Unknown')}\nQuantity: {book.get('Quantity', 0)}\nStatus: {status}\n"

    def search_by_author(self, author: str) -> str:
        found = [b for b in self.books if b.get("Author", "").lower() == author.lower()]
        if not found:
            return "No books found by this author."

        result = "\n"
        for book in found:
            status = "Available" if book.get("Quantity", 0) > 0 else "Unavailable"
            result += f"- {book['Title']} (Qty: {book.get('Quantity', 0)}) [{status}]\n"
        return result

    def borrow_book(self, title: str) -> str:
        book = self.find_book(title)
        if book:
            if book.get("Quantity", 0) <= 0:
                return "Book is currently unavailable."
            book["Quantity"] -= 1
            if book["Quantity"] == 0:
                book["Status"] = "Unavailable"
            self._save_books()
            return f"'{book['Title']}' borrowed successfully."
        return "Book not found."

    def return_book(self, title: str) -> str:
        book = self.find_book(title)
        if book:
            book["Quantity"] = book.get("Quantity", 0) + 1
            book["Status"] = "Available"
            self._save_books()
            return f"'{book['Title']}' returned successfully."
        return "Book not found."

    def check_availability(self, title: str) -> str:
        book = self.find_book(title)
        if not book:
            return "Book not found."
        return "Book is available." if book.get("Quantity", 0) > 0 else "Book is unavailable."

    def add_member(self, name: str) -> str:
        while True:
            member_id = f"M{random.randint(1000, 9999)}"
            if not self.find_member(member_id):
                break

        self.members.append({"Name": name, "ID": member_id})
        self._save_members()
        return member_id


# ================= MAIN MENU LOGIC =================

def main():
    library = Library("Sanket Library")
    
    print(f"\n{'='*10} Welcome to {library.name} {'='*10}\n")
    print(f"Data directory: {APP_DIR}")

    while True:
        try:
            user_id = input("\nEnter Member ID (or 'admin' / 'exit'): ").strip()
        except KeyboardInterrupt:
            print("\nExiting program...")
            break

        if user_id.lower() == "exit":
            print("Goodbye!")
            break

        # ================= ADMIN =================
        if user_id.lower() == "admin":
            password = input("Enter Admin Password: ").strip()
            if password != ADMIN_PASSWORD:
                print("Wrong password.\n")
                continue

            while True:
                print("\n========= ADMIN MENU =========")
                print("1. Add Book")
                print("2. Remove Book")
                print("3. Show All Books")
                print("4. Exit Admin Mode")
                
                choice = input("Enter choice: ").strip()
                
                if choice == "1":
                    title = input("Enter title: ").strip()
                    author = input("Enter author: ").strip()
                    try:
                        quantity = int(input("Enter quantity: "))
                        print(library.add_book(title, author, quantity))
                    except ValueError:
                        print("Invalid quantity. Must be a number.\n")
                elif choice == "2":
                    title = input("Enter title: ").strip()
                    print(library.remove_book(title))
                elif choice == "3":
                    library.show_books()
                elif choice == "4":
                    print("Exiting admin mode...\n")
                    break
                else:
                    print("Invalid choice.\n")

        # ================= MEMBER =================
        else:
            member = library.find_member(user_id)
            
            if not member:
                register = input("Member not found. Register? (y/n): ").strip().lower()
                if register == "y":
                    name = input("Enter your name: ").strip()
                    if name:
                        new_id = library.add_member(name)
                        print(f"Registration successful. Your Member ID: {new_id}\n")
                    else:
                        print("Name cannot be empty.")
                continue

            print(f"\nWelcome, {member['Name']}!")

            while True:
                print("\n========= MEMBER MENU =========")
                print("1. Search Book By Title")
                print("2. Search Books By Author")
                print("3. Show All Books")
                print("4. Borrow Book")
                print("5. Return Book")
                print("6. Check Availability")
                print("7. Logout")
                
                choice = input("Enter choice: ").strip()

                if choice == "1":
                    print(library.search_by_title(input("Enter title: ").strip()))
                elif choice == "2":
                    print(library.search_by_author(input("Enter author: ").strip()))
                elif choice == "3":
                    library.show_books()
                elif choice == "4":
                    print(library.borrow_book(input("Enter title: ").strip()))
                elif choice == "5":
                    print(library.return_book(input("Enter title: ").strip()))
                elif choice == "6":
                    print(library.check_availability(input("Enter title: ").strip()))
                elif choice == "7":
                    print("Logging out...\n")
                    break
                else:
                    print("Invalid choice.\n")

if __name__ == "__main__":
    main()