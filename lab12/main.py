import os
import random
from datetime import datetime, timedelta, time

from dotenv import load_dotenv
from faker import Faker
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# -----------------------
# CONFIGURATIONS
# -----------------------
# Adjust these as you like to generate more/fewer documents
COUNT_USERS = 2000
COUNT_DOCTORS = 300
COUNT_DONORS = 700
COUNT_MODERATORS = 50
COUNT_HOSPITALS = 50
COUNT_DRIVERS = 200
COUNT_NURSES = 200
COUNT_FACILITIES = 100
COUNT_ORDERS = 500
COUNT_BLOODBAGS = 3000

load_dotenv()
uri = os.getenv("MONGODB_URI")

if not uri:
    print("Database URI not found. Please set MONGODB_URI in your .env file.")
    exit(1)

client = MongoClient(uri, server_api=ServerApi('1'))

db = client["krwiodawcy"]

fake_pl = Faker("pl_PL")

try:
    client.admin.command('ping')
    print("Pinged your deployment. Successfully connected to MongoDB!")
except Exception as e:
    print("Connection error:", e)
    exit(1)

# -----------------------------------
# 1. Insert USERS
# -----------------------------------
users_collection = db["users"]

users_data = []
for _ in range(COUNT_USERS):
    users_data.append({
        "password": fake_pl.password(),
        "profiles": [],  # or fill with relevant profile data if you like
        "phone_number": fake_pl.phone_number(),
        "login": fake_pl.user_name(),
        "email": fake_pl.email()
    })

users_insert_result = users_collection.insert_many(users_data)
users_ids = list(users_insert_result.inserted_ids)
print(f"Inserted {len(users_ids)} users.")

# -----------------------------------
# 2. Insert DOCTORS
#    Each references a random user_id
# -----------------------------------
doctors_collection = db["doctors"]

doctors_data = []
for _ in range(COUNT_DOCTORS):
    random_user_id = random.choice(users_ids)
    first_name = fake_pl.first_name()
    last_name = fake_pl.last_name()
    doctors_data.append({
        "user_id": random_user_id,
        "name": first_name,
        "last_name": last_name,
        "facilities": []  # Later you could populate with facility IDs if desired
    })

doctors_insert_result = doctors_collection.insert_many(doctors_data)
doctors_ids = list(doctors_insert_result.inserted_ids)
print(f"Inserted {len(doctors_ids)} doctors.")

# -----------------------------------
# 3. Insert DONORS
#    Each references a random user_id
# -----------------------------------
donors_collection = db["donors"]

# Helper for random enum picks
possible_sexes = ["Male", "Female"]
possible_blood_types = ["0", "A", "B", "AB"]
possible_rh = ["+", "-"]

donors_data = []
for _ in range(COUNT_DONORS):
    random_user_id = random.choice(users_ids)
    birth_date = fake_pl.date_of_birth(minimum_age=18, maximum_age=65)
    birth_date = datetime.combine(birth_date, datetime.min.time())
    # Generate some random examinations
    exam_count = random.randint(1, 5)
    examinations = []
    for __ in range(exam_count):
        exam_date = fake_pl.date_between_dates(date_start=birth_date, date_end=datetime.now())
        exam_date = datetime.combine(exam_date, datetime.min.time())
        weight = round(random.uniform(50, 100), 1)   # 50.0 - 100.0
        height = round(random.uniform(150, 200), 1)  # 150.0 - 200.0
        is_qual = random.choice([True, False])
        examinations.append({
            "date": exam_date,
            "weight": weight,
            "height": height,
            "is_qualified": is_qual
        })

    donors_data.append({
        "user_id": random_user_id,
        "examinations": examinations,
        "birth_date": birth_date,
        "sex": random.choice(possible_sexes),
        "blood_type": random.choice(possible_blood_types),
        "blod_rh": random.choice(possible_rh),
        "name": fake_pl.first_name(),
        "last_name": fake_pl.last_name(),
        "pesel": fake_pl.pesel(),
    })

donors_insert_result = donors_collection.insert_many(donors_data)
donors_ids = list(donors_insert_result.inserted_ids)
print(f"Inserted {len(donors_ids)} donors.")

# -----------------------------------
# 4. Insert MODERATORS
#    Each references a random user_id
# -----------------------------------
moderators_collection = db["moderators"]

moderators_data = []
for _ in range(COUNT_MODERATORS):
    random_user_id = random.choice(users_ids)
    moderators_data.append({
        "user_id": random_user_id,
        "name": fake_pl.first_name(),
        "last_name": fake_pl.last_name()
    })

moderators_insert_result = moderators_collection.insert_many(moderators_data)
moderators_ids = list(moderators_insert_result.inserted_ids)
print(f"Inserted {len(moderators_ids)} moderators.")

# -----------------------------------
# 5. Insert HOSPITALS
#    Each references a random user_id
# -----------------------------------
hospitals_collection = db["hospitals"]

hospitals_data = []
for _ in range(COUNT_HOSPITALS):
    random_user_id = random.choice(users_ids)
    hospitals_data.append({
        "user_id": random_user_id,
        "name": f"Szpital {fake_pl.city()}",
        "address": fake_pl.address().replace("\n", ", ")
    })

hospitals_insert_result = hospitals_collection.insert_many(hospitals_data)
hospitals_ids = list(hospitals_insert_result.inserted_ids)
print(f"Inserted {len(hospitals_ids)} hospitals.")

# -----------------------------------
# 6. Insert DRIVERS
# -----------------------------------
drivers_collection = db["drivers"]

drivers_data = []
for _ in range(COUNT_DRIVERS):
    drivers_data.append({
        "name": fake_pl.first_name(),
        "last_name": fake_pl.last_name()
    })

drivers_insert_result = drivers_collection.insert_many(drivers_data)
drivers_ids = list(drivers_insert_result.inserted_ids)
print(f"Inserted {len(drivers_ids)} drivers.")

# -----------------------------------
# 7. Insert NURSES
# -----------------------------------
nurses_collection = db["nurses"]

nurses_data = []
for _ in range(COUNT_NURSES):
    nurses_data.append({
        "name": fake_pl.first_name(),
        "last_name": fake_pl.last_name(),
        "phone_number": fake_pl.phone_number()
    })

nurses_insert_result = nurses_collection.insert_many(nurses_data)
nurses_ids = list(nurses_insert_result.inserted_ids)
print(f"Inserted {len(nurses_ids)} nurses.")

# -----------------------------------
# 8. Insert FACILITIES
#    - "doctors": array of embedded { user_id, name, last_name }
#    - "nurses": array of embedded { name, last_name, phone_number, nurse_id }
# -----------------------------------
facilities_collection = db["facilities"]

# For convenience, build a small list of "doctor objects" we can embed
# from the existing doctors. We'll store (user_id, name, last_name)
doctors_cursor = doctors_collection.find({})
all_doctors_for_embed = []
for doc in doctors_cursor:
    all_doctors_for_embed.append({
        "user_id": doc["user_id"],  # already an ObjectId from the user collection
        "name": doc["name"],
        "last_name": doc["last_name"]
    })

# Similarly build a list for nurses
nurses_cursor = nurses_collection.find({})
all_nurses_for_embed = []
for nurse in nurses_cursor:
    all_nurses_for_embed.append({
        "name": nurse["name"],
        "last_name": nurse["last_name"],
        "phone_number": nurse["phone_number"],
        "nurse_id": nurse["_id"]  # references the nurse objectId
    })

facilities_data = []
for _ in range(COUNT_FACILITIES):
    # Pick a random subset of doctors and nurses to embed
    random_doctors_count = random.randint(1, 5)
    random_nurses_count = random.randint(1, 5)
    random_doctors = random.sample(all_doctors_for_embed, random_doctors_count)
    random_nurses = random.sample(all_nurses_for_embed, random_nurses_count)

    facilities_data.append({
        "doctors": random_doctors,
        "name": f"Centrum Krwiodawstwa {fake_pl.city()}",
        "address": fake_pl.address().replace("\n", ", "),
        "phone_number": fake_pl.phone_number(),
        "available_blood_bags": [],  # left empty for now
        "nurses": random_nurses,
        "email": fake_pl.email()
    })

facilities_insert_result = facilities_collection.insert_many(facilities_data)
facilities_ids = list(facilities_insert_result.inserted_ids)
print(f"Inserted {len(facilities_ids)} facilities.")

# -----------------------------------
# 9. Insert ORDERS
#    - "hospital": { "address", "user_id"(int!), "name", "hospital_id" }
#    - "realizations": optional, we can add them
# -----------------------------------
orders_collection = db["orders"]

# We'll load existing hospitals to embed properly
hospitals_docs = list(hospitals_collection.find({}))
orders_data = []

for _ in range(COUNT_ORDERS):
    # Pick a random hospital doc
    h = random.choice(hospitals_docs)
    hospital_embed = {
        "address": h["address"],  # schema says "address" (double-d)
        "user_id": random.randint(1, 9999),  # must be int (the schema mismatch)
        "name": h["name"],
        "hospital_id": h["_id"]
    }
    # Possibly random realizations with random drivers
    realization_count = random.randint(0, 3)
    reals = []
    for __ in range(realization_count):
        reals.append({
            "date": datetime.combine(fake_pl.date_between_dates(date_start=datetime(2020, 1, 1), date_end=datetime.now()), time.min),
            "transport": {
            "driver_id": random.choice(drivers_ids)
            },
            "blood_bags": []  # We can fill later or leave empty
        })

    orders_data.append({
        "is_urgent": fake_pl.boolean(chance_of_getting_true=30),
        "state": random.choice(["partially_completed", "completed", "awaiting", "cancelled"]),
        "hospital": hospital_embed,
        "realizations": reals
    })

orders_insert_result = orders_collection.insert_many(orders_data)
orders_ids = list(orders_insert_result.inserted_ids)
print(f"Inserted {len(orders_ids)} orders.")

# -----------------------------------
# 10. Insert BLOOD_BAGS
#     - "volume": double
#     - "donation": { "date", "donor_id", "nurse_id" }
#     - "facility_id": ObjectId
#     - "order": ObjectId (optional)
#     - "lab_result" (optional, but let's fill it in)
# -----------------------------------
blood_bags_collection = db["blood_bags"]

facilities_docs = list(facilities_collection.find({}))
donors_docs = list(donors_collection.find({}))
nurses_docs = list(nurses_collection.find({}))

orders_docs = list(orders_collection.find({}))
blood_bags_data = []

for _ in range(COUNT_BLOODBAGS):
    # random references
    facility = random.choice(facilities_docs)
    donor = random.choice(donors_docs)
    nurse = random.choice(nurses_docs)

    # random chance to reference an order or not
    maybe_order = random.choice([None, random.choice(orders_docs)])

    donation_date = datetime.combine(fake_pl.date_between_dates(date_start=donor["birth_date"], date_end=datetime.now()), time.min)

    bag = {
        "volume": float(random.choice([450, 500, 300, 350])),  # typical volumes
        "donation": {
            "date": donation_date,
            "donor_id": donor["_id"],
            "nurse_id": nurse["_id"]
        },
        "facility_id": facility["_id"]
    }
    # lab_result is optional but let's add it
    bag["lab_result"] = {
        "date": donation_date + timedelta(days=1),
        "is_qualified": fake_pl.boolean(chance_of_getting_true=80)
    }

    if maybe_order:
        bag["order"] = maybe_order["_id"]

    blood_bags_data.append(bag)

# Insert in chunks to avoid extremely large single insert
CHUNK_SIZE = 1000
for i in range(0, len(blood_bags_data), CHUNK_SIZE):
    chunk = blood_bags_data[i:i+CHUNK_SIZE]
    blood_bags_collection.insert_many(chunk)

print(f"Inserted {len(blood_bags_data)} blood_bags.")

print("\nSeeding completed successfully!")
