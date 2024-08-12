from collections import UserDict
import re
from datetime import datetime, timedelta


class Field:
    def __init__(self, value) -> None:
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if len(value) != 0:
            super().__init__(value)
        else:
            raise ValueError("Name cannot be empty")

class Phone(Field):
    def __init__(self, number):
        if self.validate_number(number):
            super().__init__(number)
        else:
            raise ValueError("Invalid phone number")

    def validate_number(self, number):
        return len(number) == 10 and re.match(r"^\d+$", number)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Phone):
            return self.value == other.value
        return False

    def __repr__(self):
        return self.value

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        number = Phone(phone_number)
        self.phones.append(number)

    def remove_phone(self, phone_number):
        phone_obj = Phone(phone_number)
        for obj in self.phones:
            if obj == phone_obj:
                self.phones.remove(obj)
                break

    def edit_phone(self, old_number, new_number):
        self.remove_phone(old_number)
        self.add_phone(new_number)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        else:
            raise ValueError("Phone number not found")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __repr__(self):
        return f"Record(name={self.name}, phones={self.phones}, birthday={self.birthday})"

class AddressBook(UserDict):
    def add_record(self, record_item):
        self.data[record_item.name.value] = record_item

    def find(self, key):
        if key in self:
            return self[key]
        else:
            raise KeyError("Record not found")

    def delete_record(self, name):
        if name in self.data:
            del self.data[name]
            return f"Contact {name} deleted"
        else:
            return f"Contact {name} not found"

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                next_birthday = record.birthday.value.replace(year=today.year)
                if today <= next_birthday <= today + timedelta(days=7):
                    upcoming_birthdays.append({
                        'name': record.name.value,
                        'birthday': next_birthday.strftime('%d.%m.%Y')
                    })
        return upcoming_birthdays

# Декоратор для обработки ошибок
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"ValueError: {e}"
        except KeyError as e:
            return f"KeyError: {e}"
        except IndexError:
            return "IndexError: Invalid input, please try again."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
    return wrapper

# Функции-обработчики команд
@input_error
def add_contact(args, address_book):
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    address_book.add_record(record)
    return f"Contact {name} added with phone number {phone}"

@input_error
def change_phone(args, address_book):
    name, old_phone, new_phone = args
    record = address_book.find(name)
    record.edit_phone(old_phone, new_phone)
    return f"Phone number for {name} changed from {old_phone} to {new_phone}"

@input_error
def show_phones(args, address_book):
    name = args[0]
    record = address_book.find(name)
    return f"{name}'s phones: {', '.join(str(phone) for phone in record.phones)}"

@input_error
def show_all_contacts(address_book):
    result = []
    for record in address_book.values():
        phones = ', '.join(str(phone) for phone in record.phones)
        birthday = record.birthday.value.strftime('%d.%m.%Y') if record.birthday else "No birthday"
        result.append(f"Name: {record.name}, Phones: {phones}, Birthday: {birthday}")
    return '\n'.join(result)

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip().lower()
        command, *args = user_input.split()

        try:
            if command in ["close", "exit"]:
                print("Good bye!")
                break

            elif command == "hello":
                print("How can I help you?")

            elif command == "add":
                print(add_contact(args, book))

            elif command == "change":
                print(change_phone(args, book))

            elif command == "phone":
                print(show_phones(args, book))

            elif command == "all":
                print(show_all_contacts(book))

            elif command == "delete":
                if args:
                    name = args[0]
                    print(book.delete_record(name))
                else:
                    print("Please provide the name of the contact to delete.")

            elif command == "add-birthday":
                if len(args) == 2:
                    name, birthday = args
                    record = book.data.get(name)
                    if record:
                        try:
                            record.add_birthday(birthday)
                            print(f"Birthday for {name} added.")
                        except ValueError as e:
                            print(e)
                    else:
                        print(f"Contact {name} not found.")
                else:
                    print("Please provide both the contact name and the birthday date.")

            elif command == "show-birthday":
                if args:
                    name = args[0]
                    record = book.data.get(name)
                    if record and record.birthday:
                        print(f"{name}'s birthday is {record.birthday.value.strftime('%d.%m.%Y')}")
                    else:
                        print(f"No birthday found for {name}.")
                else:
                    print("Please provide the contact name.")

            elif command == "birthdays":
                upcoming_birthdays = book.get_upcoming_birthdays()
                if upcoming_birthdays:
                    for contact in upcoming_birthdays:
                        print(f"Name: {contact['name']}, Birthday: {contact['birthday']}")
                else:
                    print("No upcoming birthdays in the next 7 days.")

            else:
                print("Invalid command.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()




