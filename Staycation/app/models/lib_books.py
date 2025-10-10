# from app import db

# class Book(db.Document):
#     meta = {'collection': 'books'}  # defined name of the book collection

#     #Book info
#     genres = db.ListField(db.StringField()) # List of str
#     title = db.StringField(required=True, unique=True) # str (keeping required/unique for good measure)
#     category = db.StringField() # str
#     url = db.StringField() # str
#     description = db.ListField(db.StringField()) # List of str
#     authors = db.ListField(db.StringField(), required=True) # List of str (keeping required)
#     pages = db.IntField() # int
#     available = db.IntField(default=0) # int (keeping default for practical use)
#     copies = db.IntField(default=1) # int (keeping default for practical use)

#     def __str__(self):
#         return f"{self.title} by {', '.join(self.authors)}"

#     # Optional: method to check stock
#     def is_available(self):
#         return self.available > 0

#     # Static methods to query
#     @staticmethod
#     def getBook(title):
#         return Book.objects(title=title).first()

#     @staticmethod
#     def getAllBooks():
#         return Book.objects()

#     @staticmethod
#     def createBook(title, authors, genres, category, url, description, pages, available, copies):
#         book = Book(
#             title=title,
#             authors=authors,
#             genres=genres,
#             category=category,
#             url=url,
#             description=description,
#             pages=pages,
#             available=available,
#             copies=copies
#         )
#         return book.save()  # returns the saved Book instance

#     def borrow(self):
#         if self.available_copies > 0:
#             self.available_copies -= 1
#             self.save()
#             return True
#         return False

#     def return_book(self):
#         if self.available_copies < self.total_copies:
#             self.available_copies += 1
#             self.save()
#             return True
#         return False


    
from app import db

class Book(db.Document):
    meta = {'collection': 'books'}

    # Book info
    genres = db.ListField(db.StringField())  # List of str
    title = db.StringField(required=True, unique=True)  # str
    category = db.StringField()  # str
    url = db.StringField()  # str (e.g. image or external link)
    description = db.ListField(db.StringField())  # List of str
    authors = db.ListField(db.StringField(), required=True)  # List of str
    pages = db.IntField()  # int
    available = db.IntField(default=0)  # currently available copies
    copies = db.IntField(default=1)  # total number of copies

    def __str__(self):
        return f"{self.title} by {', '.join(self.authors)}"

    # ---- AVAILABILITY CHECK ----
    def is_available(self):
        """Return True if there are available copies."""
        return self.available > 0

    # ---- STATIC QUERY METHODS ----
    @staticmethod
    def getBook(title):
        return Book.objects(title=title).first()

    @staticmethod
    def getAllBooks():
        return Book.objects()

    @staticmethod
    def createBook(title, authors, genres, category, url, description, pages, available, copies):
        """Factory method to create and save a new Book."""
        book = Book(
            title=title,
            authors=authors,
            genres=genres,
            category=category,
            url=url,
            description=description,
            pages=pages,
            available=available,
            copies=copies
        )
        return book.save()

    # ---- BORROW METHOD ----
    def borrow(self):
        """Borrow a book if available."""
        if self.available > 0:
            self.available -= 1
            self.save()
            print(f"Borrowed '{self.title}'. Available copies left: {self.available}")
            return True
        else:
            print(f"'{self.title}' is not available for borrowing.")
            return False

    # ---- RETURN METHOD ----
    def return_book(self):
        """Return a borrowed book if not exceeding total copies."""
        if self.available < self.copies:
            self.available += 1
            self.save()
            print(f"Returned '{self.title}'. Available copies: {self.available}")
            return True
        else:
            print(f"All copies of '{self.title}' are already in stock.")
            return False


