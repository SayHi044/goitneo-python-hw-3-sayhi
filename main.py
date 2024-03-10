from datetime import datetime
from collections import UserDict


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name):
        super().__init__(name)


class Phone(Field):
    def __init__(self, phone):
        if not (len(phone) == 10 and phone.isdigit()):
            raise ValueError("Phone number must be 10 digits long")

        super().__init__(phone)


class Birthday(Field):
    def __init__(self, birthday):
        try:
            date = datetime.strptime(birthday, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Birthday must be in the format DD.MM.YYYY")

        super().__init__(date)


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.birthday = Birthday(birthday) if birthday else None
        self.phones = []

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def edit_phone(self, old_number, new_number):
        phone = self.find_phone(old_number)
        if phone:
            phone.value = new_number
            return True
        return False

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        if isinstance(record, Record):
            self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_birthdays_per_week(self):
        today = datetime.today().date()
        output: dict[str, list[str]] = {}

        users = [self.data[name] for name in self.data.keys()]
        users.sort(key=lambda x: (x.birthday.value.month, x.birthday.value.day))

        for user in users:
            name = user.name.value
            birthday = user.birthday.value
            next_birthday = birthday.replace(year=today.year)
            if next_birthday < today:
                next_birthday = birthday.replace(year=today.year + 1)

            delta_days = (next_birthday - today).days
            if delta_days < 7:
                day = next_birthday.strftime("%A")
                day = 'Monday' if day in ('Saturday', 'Sunday') else day

                if not output.get(day):
                    output[day] = []

                output[day].append(name)

        return output


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            if str(e) in ["Phone number must be 10 digits long", "Birthday must be in the format DD.MM.YYYY"]:
                return str(e)
            else:
                return "Give me correct data please"
        except IndexError:
            return "Missing arguments"
        except KeyError:
            return "Not found"
    return inner


@input_error
def add_contact(args, book):
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)

    return "Contact added."


@input_error
def change_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.edit_phone(record.phones[0].value, phone)
        return "Contact updated."
    else:
        return "Not found."


@input_error
def show_phone(args, book):
    [name] = args
    record = book.find(name)
    if record:
        return ', '.join(map(str, record.phones))
    else:
        return "Not found."


@input_error
def show_all(book):
    if not book.data:
        return "No contacts stored."

    return '\n'.join([f"{record.name}: {', '.join(map(str, record.phones))}" for record in book.data.values()])


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact not found."


@input_error
def show_birthday(args, book):
    [name] = args
    record = book.find(name)
    if record and record.birthday:
        return str(record.birthday)
    else:
        return "No birthday found for this contact."


@input_error
def show_birthdays_next_week(book):
    birthdays_next_week = book.get_birthdays_per_week()
    if not birthdays_next_week:
        return "No birthdays next week."

    response = []
    for day, names in birthdays_next_week.items():
        response.append(f"{day}: {', '.join(names)}")

    return "\n".join(response)


def hello_command():
    return "How can I help you?"


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command == "hello":
            print(hello_command())
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(show_birthdays_next_week(book))
        elif command in ["close", "exit"]:
            print("Good bye!")
            break
        else:
            print(f"Command '{command}' not recognized")


if __name__ == "__main__":
    main()
