import csv

def validate_login(username, password):

    with open('user_accounts.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        print(reader)
        for row in reader:
            print(row)
            if row['username'] == username and row['password_hash'] == password:
                
                return True
    return False

    return result
