# from flask_login import login_user, login_required, logout_user, current_user
# from flask import Blueprint, request, redirect, render_template, url_for

# from models.forms import BookForm

# from models.users import User
# from models.package import Package
# from models.lib_books import Book
# from app.books import all_books #question 2a to populate the books

# package = Blueprint('packageController', __name__)

# @package.route('/')
# @package.route("/BookTitles")
# # def book_titles():
# #    # all_books = Book.getAllBooks()
# #     return render_template('books.html', panel="BOOK TITLES", all_books=all_books)

# def book_titles():
#     # Get category from query parameter (default = All)
#     selected_category = request.args.get('category', 'All')

#     # ✅ Filter by category if not 'All'
#     if selected_category == 'All':
#         filtered_books = all_books
#     else:
#         filtered_books = [b for b in all_books if b['category'] == selected_category]

#     # ✅ Sort filtered books alphabetically by title
#     sorted_books = sorted(filtered_books, key=lambda b: b['title'].lower())

#     # ✅ Keep only the first and last paragraphs of description
#     for book in sorted_books:
#         desc_list = book.get('description', [])
#         if len(desc_list) > 1:
#             short_desc = f"{desc_list[0]}\n\n{desc_list[-1]}"
#         elif desc_list:
#             short_desc = desc_list[0]
#         else:
#             short_desc = "No description available."
#         book['short_description'] = short_desc

#     return render_template(
#         'books.html',
#         panel="BOOK TITLES",
#         all_books=sorted_books,
#         selected_category=selected_category
#     )

    

# @package.route("/viewBookDetail/<book_title>")
# def viewBookDetail(book_title):
#     # Find the book by title
#     the_book = next((b for b in all_books if b['title'] == book_title), None)
    
#     if not the_book:
#         return render_template('error.html', message="Book not found."), 404

#     return render_template(
#         'BookDetailsPage.html',
#         panel="BOOK DETAIL",
#         book=the_book
#     )
from flask import Blueprint, request, render_template, redirect, url_for
from datetime import datetime, timedelta
import random
from flask_login import current_user, login_required
from bson import ObjectId
from datetime import datetime
from models.lib_books import Book
from app.models.Loan import Loan
from app.models.users import User
from app.books import all_books    # still needed for DB initialization


# from app.books import all_books #question 2a to populate the books

package = Blueprint('packageController', __name__)

# Populate MongoDB from all_books if collection empty
def initialize_books():
    if Book.objects.count() == 0:
        for b in all_books:
            Book(**b).save()
        print("✅ MongoDB populated with books from all_books.")
    else:
        print("✅ Book collection already populated.")

# @package.route('/')
# @package.route("/BookTitles")
# # def book_titles():
# #    # all_books = Book.getAllBooks()
# #     return render_template('books.html', panel="BOOK TITLES", all_books=all_books)

# def book_titles():
#     # Get category from query parameter (default = All)
#     selected_category = request.args.get('category', 'All')

#     # ✅ Filter by category if not 'All'
#     if selected_category == 'All':
#         filtered_books = all_books
#     else:
#         filtered_books = [b for b in all_books if b['category'] == selected_category]

#     # ✅ Sort filtered books alphabetically by title
#     sorted_books = sorted(filtered_books, key=lambda b: b['title'].lower())

#     # ✅ Keep only the first and last paragraphs of description
#     for book in sorted_books:
#         desc_list = book.get('description', [])
#         if len(desc_list) > 1:
#             short_desc = f"{desc_list[0]}\n\n{desc_list[-1]}"
#         elif desc_list:
#             short_desc = desc_list[0]
#         else:
#             short_desc = "No description available."
#         book['short_description'] = short_desc

#     return render_template(
#         'books.html',
#         panel="BOOK TITLES",
#         all_books=sorted_books,
#         selected_category=selected_category
#     )

    

# @package.route("/viewBookDetail/<book_title>")
# def viewBookDetail(book_title):
#     # Find the book by title
#     the_book = next((b for b in all_books if b['title'] == book_title), None)
    
#     if not the_book:
#         return render_template('error.html', message="Book not found."), 404

#     return render_template(
#         'BookDetailsPage.html',
#         panel="BOOK DETAIL",
#         book=the_book
#     )

@package.route('/')
@package.route("/BookTitles")
def book_titles():
    selected_category = request.args.get('category', 'All')

    # ✅ Fetch books from MongoDB
    if selected_category == 'All':
        books = Book.objects()  # all documents
    else:
        books = Book.objects(category=selected_category)

    # ✅ Sort alphabetically
    sorted_books = sorted(books, key=lambda b: b.title.lower())

    # ✅ Generate short description
    for book in sorted_books:
        desc_list = getattr(book, 'description', [])
        if len(desc_list) > 1:
            book.short_description = f"{desc_list[0]}\n\n{desc_list[-1]}"
        elif desc_list:
            book.short_description = desc_list[0]
        else:
            book.short_description = "No description available."

    return render_template(
        'books.html',
        panel="BOOK TITLES",
        all_books=sorted_books,
        selected_category=selected_category
    )

@package.route("/viewBookDetail/<book_title>")
def viewBookDetail(book_title):
    # Find by title (case-insensitive)
    book = Book.objects(title__iexact=book_title).first()

    if not book:
        return render_template('error.html', message="Book not found."), 404

    return render_template(
        'BookDetailsPage.html',
        panel="BOOK DETAIL",
        book=book
    )

@package.route('/make_loan/<book_id>', methods=['GET', 'POST'])
def make_loan(book_id):
    try:
        # Get the book as a Document object
        book = Book.objects(id=book_id).first()
        if not book:
            return redirect(url_for('packageController.book_titles'))

        message = None

        if request.method == 'POST':
            borrow_date = datetime.now() - timedelta(days=random.randint(10, 20))

            # Debug: Check types before creating loan
            print(f"User type: {type(current_user)}")
            print(f"Book type: {type(book)}")
            print(f"Book ID: {book.id}")

            # Try to create a loan
            loan, msg = Loan.create_loan(current_user, book, borrow_date)
            message = msg

            if loan:
                # Update book availability
                book.available -= 1
                book.save()
                return redirect(url_for('packageController.book_titles'))

        return render_template('make_loan.html', book=book, message=message)
    
    except Exception as e:
        print(f"Error in make_loan: {str(e)}")
        return redirect(url_for('packageController.book_titles'))