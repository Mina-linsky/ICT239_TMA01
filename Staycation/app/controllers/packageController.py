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
from flask import Blueprint, request, render_template
from models.lib_books import Book
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
    book = Book.objects(id=book_id).first()

    if not book:
        return "Book not found", 404

    if request.method == 'POST':
        member_id = request.form.get('member_id')
        borrow_date = request.form.get('borrowDate')
        return_date = request.form.get('returnDate')

        # Create a new Loan document
        loan = Loan(
            member=member_id,
            book=book,
            borrowDate=borrow_date,
            returnDate=return_date,
        )
        loan.save()

        # Optional: reduce available count if it exists
        if hasattr(book, 'available_count'):
            book.available_count -= 1
            book.save()

        flash('Loan successfully created!', 'success')
        return redirect(url_for('show_books'))  # Or wherever you list books

    return render_template('make_loan.html', book=book)


