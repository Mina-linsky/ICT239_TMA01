from app import db
from datetime import datetime, timedelta
import random

class Loan(db.Document):
    member = db.ReferenceField('User', required=True)
    book = db.ReferenceField('Book', required=True)
    borrowDate = db.DateTimeField(required=True, default=datetime.utcnow)
    returnDate = db.DateTimeField(null=True)
    renewCount = db.IntField(default=0)

    meta = {'collection': 'loans'}

    def __str__(self):
        return f"Loan({self.member}, {self.book}, {self.borrowDate.strftime('%Y-%m-%d')})"

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @classmethod
    def create_loan(cls, user, book, borrow_date):
        """
        Create a new loan if:
        - The user does NOT already have an unreturned loan for this book.
        - The book's available count > 0.
        - Then update the book's available count.
        """
        # Check if user already has an active (unreturned) loan for this book
        existing_loan = cls.objects(member=user, book=book, returnDate=None).first()
        if existing_loan:
            return None, "You already have an active loan for this book."

        # Check if book is available
        if book.available <= 0:
            return None, "No copies available for this book."

        # Create loan
        new_loan = cls(member=user, book=book, borrowDate=borrow_date)
        new_loan.save()

        # Update book availability
        book.available -= 1
        book.save()

        return new_loan, "Loan successfully created."

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @classmethod
    def get_user_loans(cls, user):
        """Retrieve all loan records belonging to this user, sorted by borrowDate (descending)."""
        return cls.objects(member=user).order_by('-borrowDate')

    @classmethod
    def get_loan_by_id(cls, loan_id):
        """Retrieve a specific loan by its ID."""
        return cls.objects(id=loan_id).first()

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def renew(self):
        """
        Renew this loan if:
        - It is not overdue.
        - renewCount < 2.
        Update borrowDate and increment renewCount.
        """
        # Check overdue or renew limit
        if self.is_overdue():
            return "Cannot renew overdue loan."
        if self.renewCount >= 2:
            return "Renew limit reached (2 times max)."

        # Generate a new borrow date 10–20 days after the current borrow date
        days_after = random.randint(10, 20)
        new_borrow_date = self.borrowDate + timedelta(days=days_after)

        # Borrow date cannot be after today
        if new_borrow_date > datetime.now():
            new_borrow_date = datetime.now()

        # Update loan info
        self.borrowDate = new_borrow_date
        self.renewCount += 1
        self.save()

        return "Loan successfully renewed."

    def return_book(self):
        """
        Mark this loan as returned:
        - Set returnDate.
        - Increment the book's available count.
        """
        if self.returnDate:
            return "Book already returned."

        # Generate return date 10–20 days after borrow date, but not after today
        days_after = random.randint(10, 20)
        return_date = self.borrowDate + timedelta(days=days_after)
        if return_date > datetime.now():
            return_date = datetime.now()

        self.returnDate = return_date
        self.save()

        # Update book availability
        self.book.available += 1
        self.book.save()

        return "Book successfully returned."

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------
    def delete_loan(self):
        """
        Delete this loan record only if:
        - It has been returned (returnDate is not None).
        """
        if not self.returnDate:
            return "You can only delete returned loans."

        self.delete()
        return "Loan record deleted successfully."

    # --------------------------------------------------
    # HELPER FUNCTIONS
    # --------------------------------------------------
    def is_overdue(self):
        """Check if the loan is overdue (due date = borrowDate + 14 days)."""
        due = self.borrowDate + timedelta(days=14)
        return datetime.now() > due and self.returnDate is None

    def due_date(self):
        """Return the due date (borrowDate + 14 days)."""
        return self.borrowDate + timedelta(days=14)
