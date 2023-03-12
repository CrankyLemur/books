# Import modules
import sqlite3
import spacy
import csv
import os

# Get file path
file_path = os.path.dirname(os.path.abspath(__file__))

# Define functions
def add():
    id = int(input("Enter book ID: "))
    cursor.execute(f"SELECT * FROM books WHERE id = ?", (id,))
    book = cursor.fetchone()
    if book:
        print("A book with that ID already exists in the database:")
        print_book(book)
        choice = input("Update? (y/n)\n: ")
        if choice == "y":
            update(id)
            return
        elif choice == "n":
            return
    title = input("Enter book title: ")
    author = input("Enter author: ")
    description = input("Enter description: ")
    genre = input("Enter genre: ")
    qty = int(input("Enter quantity: "))
    cursor.execute(
        """INSERT INTO books(id,Title,Author,Description,Genre,Qty) 
        VALUES(?,?,?,?,?,?)""",
        (id, title, author, description, genre, qty),
    )
    db.commit()


def update(id=None):
    if not id:
        result = search()
        if result:
            if len(result) > 1:
                id = int(input("Enter ID of the book to update: "))
            else:
                id = result[0][0]
        else:
            return
    print("Which field would you like to update?\n")
    while True:
        choice = input(
            "Select one of the following:\n"
            "1 - Title\n"
            "2 - Author\n"
            "3 - Description\n"
            "4 - Genre\n"
            "5 - Quantity\n"
            "6 - All of the above\n"
            "0 - Exit\n"
            ": "
        )
        if choice == "1":
            field = "Title"
            new = (input("Enter new title: "),)
            break
        elif choice == "2":
            field = "Author"
            new = (input("Enter new author: "),)
            break
        elif choice == "3":
            field = "Description"
            new = (input("Enter new description: "),)
            break
        elif choice == "4":
            field = "Genre"
            new = (input("Enter new genre: "),)
            break
        elif choice == "5":
            field = "Qty"
            new = (input("Enter new quantity: "),)
            break
        elif choice == "6":
            title = "Title"
            author = "Author"
            description = "Description"
            genre = "Genre"
            qty = "Qty"
            new_title = input("Enter new title: ")
            new_author = input("Enter new author: ")
            new_description = input("Enter new description: ")
            new_genre = input("Enter new genre: ")
            new_qty = input("Enter new quantity: ")
            cursor.execute(
                f"""UPDATE books 
                SET {title} = ?, {author} = ?, {description} = ?, 
                {genre} = ?, {qty} = ?
                WHERE id = {id}""",
                (new_title, new_author, new_description, new_genre, new_qty),
            )
            break
        elif choice == "0":
            break
        else:
            print("Invalid choice")
    if choice in ["1", "2", "3", "4", "5"]:
        cursor.execute(
            f"""UPDATE books 
            SET {field} = ?
            WHERE id = {id}""",
            (new),
        )
    db.commit()


def delete():
    id = int(input("Enter book ID: "))
    cursor.execute(f"DELETE FROM books WHERE id = ?", (id,))
    db.commit()


def search():
    search = input("Enter search: ").lower()
    doc = nlp(search)
    keywords = [token for token in doc if not token.is_stop and not token.is_punct]
    try:
        query = f"""
            SELECT * FROM books
            WHERE LOWER(id) LIKE '{keywords[0]}' 
            OR LOWER(author) LIKE '{keywords[0]} %' OR 
            LOWER(author) LIKE '% {keywords[0]}' OR 
            LOWER(genre) LIKE '{keywords[0]}' OR
            LOWER(title) LIKE '{keywords[0]} %' OR 
            LOWER(title) LIKE '% {keywords[0]}' OR
            LOWER(title) LIKE '{keywords[0]}' OR LOWER(title) LIKE '% {keywords[0]} %'
            """
        for keyword in keywords[1:]:
            query += f"""
            OR LOWER(id) LIKE '{keyword}' OR 
            LOWER(author) LIKE '{keyword} %' OR LOWER(author) LIKE '% {keyword}' OR 
            LOWER(genre) LIKE '{keyword}' OR
            LOWER(title) LIKE '{keyword} %' OR LOWER(title) LIKE '% {keyword}' OR
            LOWER(title) LIKE '{keyword}' OR LOWER(title) LIKE '% {keyword} %'
            """
        cursor.execute(query)
        found_books = cursor.fetchall()
        for book in found_books:
            print_book(book)
        if not found_books:
            print("Can't find any results for that search.\n")
    except IndexError:
        print("Can't find any results for that search.\n")
    return found_books


def print_book(book):
    print(
        f"{'_' * 20}\n\n{book[0]}: {book[1]} by {book[2]}\n"
        f"genre: {book[4]}\nquantity: {book[5]}\n{'_' * 20}\n"
    )


def print_db():
    cursor.execute("SELECT id, Title, Author, Description, Genre, Qty FROM books")
    books = cursor.fetchall()
    for book in books:
        print(f"{book[0]}: {book[1]} by {book[2]} ({book[5]} left)")
    print("")


# Create database
db = sqlite3.connect(os.path.join(file_path, "ebookstore.db"))
cursor = db.cursor()
nlp = spacy.load("en_core_web_md")

# cursor.execute("DROP TABLE books")

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS books(
        id INTEGER PRIMARY KEY,
        Title TEXT,
        Author TEXT,
        Description TEXT,
        Genre TEXT,
        Qty INTEGER,
        UNIQUE(id,Title))"""
)

initial_books = []
with open(os.path.join(file_path, "books.csv"), "r+") as file:
    reader = csv.reader(file)
    for row in reader:
        book = (
            int(row[0]),
            row[1],
            row[2],
            row[3],
            row[4],
            int(row[5]),
        )
        initial_books.append(book)

cursor.executemany(
    """INSERT OR IGNORE INTO books(id,Title,Author,Description,Genre,Qty) 
    VALUES(?,?,?,?,?,?)""",
    initial_books,
)

db.commit()

# User menu
while True:
    choice = input(
        (
            "Select one of the following:\n"
            "1 - Add book\n"
            "2 - Update book\n"
            "3 - Delete book\n"
            "4 - Search books\n"
            "5 - Quick overview\n"
            "0 - Exit\n"
            ": "
        )
    )
    if choice == "1":
        add()
    elif choice == "2":
        update()
    elif choice == "3":
        delete()
    elif choice == "4":
        search()
    elif choice == "5":
        print_db()
    elif choice == "0":
        break
    else:
        print("Invalid choice")
db.close()
