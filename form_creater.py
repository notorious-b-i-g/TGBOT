import json

def create_user_json():
    user_list = []

    while True:
        number = input("Введите номер: ")
        password = input("Введите пароль: ")
        admin_rights = input("Есть ли у пользователя права админа? (yes/no): ")

        user_data = {
            "number": number,
            "password": password,
            "admin_rights": admin_rights.lower()
        }

        user_list.append(user_data)

        continue_input = input("Продолжить запись? (yes/no): ").lower()
        if continue_input == "no":
            break

    with open("user_data.json", "w") as json_file:
        json.dump(user_list, json_file, indent=2)


create_user_json()
