
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


