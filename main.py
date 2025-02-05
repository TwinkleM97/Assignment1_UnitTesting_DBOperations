from user import Database, UserService


def main():
    db = Database('users.db')
    user_service = UserService(db)
    
    while True:
        action = input("Would you like to 'get' a user or 'create' a user? (type 'exit' to quit): ").strip().lower()
        if action == 'exit':
            break
        # 
        elif action == 'get':
            user_id = int(input("Enter user ID: "))
            user_data, status_code = user_service.get_user(user_id)
            print(f"Response: {user_data} (Status Code: {status_code})")
            
        elif action == 'create':
            name = input("Enter user name: ")
            age = int(input("Enter user age: "))
            user_data, status_code = user_service.create_user(name, age)
            print(f"Response: {user_data} (Status Code: {status_code})")
            
        else:
            print("Invalid action. Please type 'get' or 'create'.")

if __name__ == '__main__':
    main()