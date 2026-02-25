import re
# import requests

# (?i)
# [a-z0-9]+
# (?:[._-][a-z0-9]+)*
# @
# [a-z]+
# (?:\.[a-z]+)*
# \.
# [a-z]{2,}
#

email_regexp = re.compile(r'(?i)[a-z0-9]+(?:[._-][a-z0-9]+)*@[a-z]+(?:\.[a-z]+)*\.[a-z]{2,}')


def is_email(input_email: str):
    return bool(email_regexp.fullmatch(input_email))


def find_emails_in_text(text: str):
    return email_regexp.findall(text)


# def find_emails_on_link(input_link: str):
#     try:
#         response = requests.get(input_link, timeout=20)
#         response.raise_for_status()
#         text = response.text
#         return find_emails_in_text(text)
#     except requests.RequestException as e:
#         print(f"Ошибка при загрузке страницы: {e}")
#         return None


def find_emails_in_file(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return find_emails_in_text(text)
    except IOError as e:
        print(f"Ошибка при чтении файла: {e}")
        return None


def cancel(user_command: str):
    if user_command != '0':
        return True
    else:
        print('отмена')
        return False


if __name__ == "__main__":
    print('\n'
          '9. Проверка и поиск синтаксически корректных e-mail.\n\n'
          'Доступные команды:\n\n'
          '1 - проверка строки\n'
          '2 - поиск по ссылке\n'
          '3 - поиск в файле\n'
          '9 - выход\n'
          '0 - для отмены\n')
    while True:
        command = input("введите команду: ")
        if command in ['9', 'q', 'exit']:
            print('выход')
            break
        elif command == '':
            pass
        elif command == '1':
            print('введите строку')
            email = input()
            if cancel(email):
                print(is_email(email))
        elif command == '2':
            print('введите ссылку')
            link = input()
            if cancel(link):
                # print(find_emails_on_link(link))
                print('опция отключена')
        elif command == '3':
            print('введите путь к файлу')
            path = input()
            if cancel(path):
                print(find_emails_in_file(path))
        else:
            print('ошибка ввода команды')


# ресурсы:
# https://www.tumblr.com/codefool/15288874550/list-of-valid-and-invalid-email-addresses
# text.txt
# re.search()
# Программисты называют своих детей так, что по имени понятно зачем они рождены и что делают
