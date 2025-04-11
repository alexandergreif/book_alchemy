import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
from datetime import datetime

print("Current working directory:", os.getcwd())

app = Flask(__name__)

# Use an absolute path for the SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'library.sqlite')

# Initialize SQLAlchemy with the app
db.init_app(app)

# Create the database tables if they don't exist yet
with app.app_context():
    db.create_all()

@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    success_message = None  # variable to hold our success message
    if request.method == "POST":
        # Retrieve the form data from the template
        name = request.form.get('name')
        birthdate_str = request.form.get('birthdate')  # field name is 'birthdate'
        date_of_death_str = request.form.get('date_of_death')

        # Convert date strings to date objects; if conversion fails, leave as None
        birth_date = None
        date_of_death = None

        try:
            if birthdate_str:
                birth_date = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
        except ValueError:
            print("Conversion of birthdate failed. Will be left as None")

        try:
            if date_of_death_str:
                date_of_death = datetime.strptime(date_of_death_str, "%Y-%m-%d").date()
        except ValueError:
            print("Conversion of death date failed. Will be left as None")

        # Create and add the new Author record using the model's autoincrement id
        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(new_author)
        db.session.commit()

        success_message = f"Author '{name}' added successfully!"

    # Render the provided template, passing success_message (if any) to it.
    # Even if the template doesn't display it, this meets the assignment instructions.
    return render_template("add_author.html", success_message=success_message)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    success_message = None

    # Get the list of authors to populate the dropdown menu.
    authors = Author.query.all()

    if request.method == "POST":
        isbn = request.form.get('isbn')
        title = request.form.get('title')
        publication_year_str = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        # Convert publication_year if provided.
        publication_year = int(publication_year_str) \
            if (publication_year_str and publication_year_str.isdigit()) \
            else None



        # Create the new Book instance. Notice that author_id is received as string, but that's acceptable
        # as long as your database column is an integer and SQLAlchemy can convert it.
        new_book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
        db.session.add(new_book)
        db.session.commit()

        success_message = f"Book '{title}' added successfully!"

        # Refresh the authors list in case any changes have occurred in the meantime (optional)
        authors = Author.query.all()

    # Render the add_book.html template while passing the list of authors and any success message.
    return render_template("add_book.html", authors=authors, success_message=success_message)


@app.route("/", methods=["GET"])
def home():
    sort_by = request.args.get("sort_by", "title")  # Default to sorting by title.
    keyword = request.args.get("q")
    success_message = request.args.get("success_message")  # Retrieve the message if present.

    # Start building the query.
    query = Book.query

    # If a keyword search is provided, filter using ilike (case-insensitive).
    if keyword:
        query = query.filter(Book.title.ilike(f"%{keyword}%"))

    # Apply sorting.
    if sort_by == "title":
        query = query.order_by(Book.title)
    elif sort_by == "publication_year":
        query = query.order_by(Book.publication_year)
    elif sort_by == "author":
        query = query.join(Author).order_by(Author.name)
    else:
        query = query.order_by(Book.title)

    books = query.all()

    return render_template(
        "home.html",
        books=books,
        current_sort=sort_by,
        success_message=success_message
    )


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    # Retrieve the book, or return a 404 if not found.
    book = Book.query.get_or_404(book_id)
    title = book.title  # Save title for message display.
    author = book.author

    # Delete the book.
    db.session.delete(book)
    db.session.commit()

    # Check if the author has any books remaining.
    if not author.books:
        db.session.delete(author)
        db.session.commit()

    # Redirect to the home page, passing the success message as a query parameter.
    success_message = f"Book '{title}' deleted successfully!"
    return redirect(url_for("home", success_message=success_message))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5002)