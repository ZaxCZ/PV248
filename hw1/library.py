# library.py
# xvalent4


class Person:
    def __init__(self, name):
        self.name = name


class Author(Person):
    def __init__(self, name, bday, dday):
        Person.__init__(self, name)
        self.born = bday
        self.died = dday


class Reader(Person):
    def __init__(self, name, bday):
        Person.__init__(self, name)
        self.born = bday

    def borrow(self, book, clerk):
        book.borrow(self, clerk)

    def give_back(self, book):
        book.give_back()


class Clerk(Person):
    def __init__(self, name):
        Person.__init__(self, name)


class Department:
    def __init__(self):
        self.s = []
        self.b = []

    def books(self):
        return self.b

    def staff(self):
        return self.s

    def available_books(self):
        available = []
        for book in self.b:
            if not book.is_borrowed():
                available.append(book)
        return available

    def add_staff(self, whom):
        if whom.__class__ == Clerk:
            if whom in self.s:
                return whom
            else:
                clerk = whom
        else:
            clerk = Clerk(whom)

        self.s.append(clerk)
        return clerk


class Library:
    def __init__(self):
        self.authors = []
        self.depts = []
        self.readers = []

    def departments(self):
        return self.depts

    def books(self):
        b = []
        for dept in self.depts:
            deptbooks = dept.books()
            b.extend(deptbooks)
        return b

    def available_books(self):
        b = []
        for dept in self.depts:
            deptbooks = dept.available_books()
            b.extend(deptbooks)
        return b

    def staff(self):
        clerks = []
        for dept in self.depts:
            deptclerks = dept.staff()
            for deptclerk in deptclerks:
                if deptclerk not in clerks:
                    clerks.append(deptclerk)
        return clerks

    def add_book(self, name, authors, date_published, publisher, isbn, department):
        book = Book(name, authors, date_published, publisher, isbn)
        department.b.append(book)

        if department not in self.depts:
            self.depts.append(department)

        return book

    def add_author(self, name, born, died):
        for author in self.authors:
            if author.name == name:
                if author.born == born:
                    if author.died == died:
                        return author
        author = Author(name, born, died)
        self.authors.append(author)
        return author

    def add_reader(self, name, born):
        reader = Reader(name, born)
        self.readers.append(reader)
        return reader

    def add_department(self):
        dept = Department()
        self.depts.append(dept)
        return dept


class Book:
    def __init__(self, name, authors, date_published, publisher, isbn):
        self.name = name
        self.authors = authors
        self.date_published = date_published
        self.publisher = publisher
        self.isbn = isbn

        self.borrowed = False
        self.b_by = None
        self.l_by = None

    def borrow(self, reader, clerk):
        self.borrowed = True
        self.b_by = reader
        self.l_by = clerk

    def give_back(self):
        self.borrowed = False
        self.b_by = None
        self.l_by = None

    def is_borrowed(self):
        return self.borrowed

    def borrowed_by(self):
        if self.is_borrowed():
            return self.b_by
        else:
            return None

    def lent_by(self):
        if self.is_borrowed():
            return self.l_by
        else:
            return None
