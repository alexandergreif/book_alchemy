from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    #define the table name
    __tablename__ = 'authors'

    #define the  columns for the authors table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)


    def __init__(self, name, birth_date=None, date_of_death=None):
        """
        Initializes a new Author instance.
        :param name:The name of the Author(required)
        :param birth_date: The birthdate of the author(optional)
        :param date_of_death: The death date of the author(option)
        """
        self.name = name
        self.birth_date = birth_date
        self.date_of_death = date_of_death

    def __repr__(self):
        """
        Returns a string represention of the Author instance.
        """
        return f"<Author {self.name}>"

    def __str__(self):
        """
        Returns a user firendly string representation of the Author instance.
        """
        birth = self.birth_date.strftime("%Y-%m-%d") if self.birth_date else "Unknown"
        death = self.date_of_death.strftime("%Y-%m-%d") if self.date_of_death else "Still Living"
        return f"Author: {self.name}, Born: {birth}, Died: {death}"


class Book(db.Model):
    __tablename__ = 'books'

    # Define columns for the Book table
    id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing primary key for Book
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)

    # Define a foreign key to connect the Book model to the Author model.
    # This assumes the authors table (defined in the Author model) is used.
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    # Relationship to access the Author model directly, insane technique
    author = db.relationship("Author", backref="books")

    def __init__(self, isbn, title, publication_year, author_id):
        """
        Initializes a new Book instance.
        :param isbn: The ISBN of the book (required).
        :param title: The title of the book (required).
        :param publication_year: The publication year (optional).
        :param author_id: The id of the author from the Author model (required as a foreign key).
        """
        self.isbn = isbn
        self.title = title
        self.publication_year = publication_year
        self.author_id = author_id

    def __repr__(self):
        """
        Returns a concise string representation of the Book instance.
        Useful for debugging.
        """
        return f"<Book {self.title}>"

    def __str__(self):
        """
        Returns a more descriptive string representation of the Book instance.
        """
        return f"Book: {self.title}, ISBN: {self.isbn}, Year: {self.publication_year}"
