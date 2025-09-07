from faker import Faker
from models import User
from services.database import SessionLocal

# --------------------------------------------------------------------------
# Warning: Before running this script, it is best to delete the old first.db file to ensure a clean start.
# --------------------------------------------------------------------------

users = [
    "London Wagner",
    "Enzo Nichols", 
    "Aliyah Stanton",
    "Zyair Frye",
    "Raya Frye",
    "Franco Farley",
    "Wrenley Stevenson",
    "Callan Tyler", 
    "Helena Vaughn",
    "Remy McCann",
    "Joyce Arias",
    "Alec Davila",
    "Rayne Nicholson",
    "Rodrigo Frye",
    "Raya Stevenson",   
    "Callan Ibarra",
    "Madilynn Harvey",
    "Cayden Friedman",
    "Aspyn Monroe",
    "Colby Acevedo",
]

def seed_database():
    """
    Fill the database with fictitious user data.
    """
    # 1. Initialize Faker and database session
    faker = Faker()
    db = SessionLocal()

    print("Start filling the database...")

    # 2. Create 20 fictitious users
    for i in range(len(users)):
        # Generate a unique username
        username = users[i]
        email = "user" + str(i) + "@example.com"
        
        # Create user instance
        new_user = User(username=username, email=email)
        
        # Set a simple default password for all fictitious users: "password"
        new_user.set_password("password")
        
        # Add new user to session
        db.add(new_user)
        print(f"Create user: {username}")

    # 3. Submit all changes to database
    db.commit()
    
    # 4. Close session
    db.close()
    print("\nDatabase filled successfully!")
    print("You can now use these users to log in, with the password 'password'.")

if __name__ == "__main__":
    seed_database()