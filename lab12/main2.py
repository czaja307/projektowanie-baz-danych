import os
import random
from datetime import datetime, time, timedelta

from dotenv import load_dotenv
from faker import Faker
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

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

users_collection = db["users"]
users_collection.delete_many({})

users_data = []
for _ in range(COUNT_USERS):
    users_data.append({
        "password": fake_pl.password(),
        "profiles": [],
        "phone_number": fake_pl.phone_number(),
        "login": fake_pl.user_name(),
        "email": fake_pl.email()
    })

users_insert_result = users_collection.insert_many(users_data)
users_ids = list(users_insert_result.inserted_ids)
print(f"Inserted {len(users_ids)} users.")

doctors_collection = db["doctors"]
doctors_collection.delete_many({})

doctors_data = []
for _ in range(COUNT_DOCTORS):
    random_user_id = random.choice(users_ids)
    doctors_data.append({
        "user_id": random_user_id,
        "name": fake_pl.first_name(),
        "last_name": fake_pl.last_name(),
        "facilities": []
    })

doctors_insert_result = doctors_collection.insert_many(doctors_data)
doctors_ids = list(doctors_insert_result.inserted_ids)
print(f"Inserted {len(doctors_ids)} doctors.")

donors_collection = db["donors"]
donors_collection.delete_many({})

possible_sexes = ["Male", "Female"]
possible_blood_types = ["0", "A", "B", "AB"]
possible_rh = ["+", "-"]

donors_data = []
for _ in range(COUNT_DONORS):
    random_user_id = random.choice(users_ids)

    birth_date = fake_pl.date_of_birth(minimum_age=18, maximum_age=65)
    birth_date = datetime.combine(birth_date, time.min)

    exam_count = random.randint(1, 5)
    examinations = []
    for __ in range(exam_count):
        exam_date = fake_pl.date_between_dates(
            date_start=birth_date.date(),
            date_end=datetime.now().date()
        )
        exam_date = datetime.combine(exam_date, time.min)

        weight = round(random.uniform(50, 100), 1)
        height = round(random.uniform(150, 200), 1)
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

moderators_collection = db["moderators"]
moderators_collection.delete_many({})

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

hospitals_collection = db["hospitals"]
hospitals_collection.delete_many({})

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

drivers_collection = db["drivers"]
drivers_collection.delete_many({})

drivers_data = []
for _ in range(COUNT_DRIVERS):
    drivers_data.append({
        "name": fake_pl.first_name(),
        "last_name": fake_pl.last_name()
    })

drivers_insert_result = drivers_collection.insert_many(drivers_data)
drivers_ids = list(drivers_insert_result.inserted_ids)
print(f"Inserted {len(drivers_ids)} drivers.")

nurses_collection = db["nurses"]
nurses_collection.delete_many({})

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

facilities_collection = db["facilities"]
facilities_collection.delete_many({})

all_doctors_for_embed = list(doctors_collection.find({}, {"user_id": 1, "name": 1, "last_name": 1, "_id": 0}))

all_nurses_for_embed = []
for nurse in nurses_collection.find({}):
    all_nurses_for_embed.append({
        "name": nurse["name"],
        "last_name": nurse["last_name"],
        "phone_number": nurse["phone_number"],
        "nurse_id": nurse["_id"]
    })

facilities_data = []
for _ in range(COUNT_FACILITIES):
    random_doctors_count = random.randint(1, 5)
    random_nurses_count = random.randint(1, 5)
    random_doctors = random.sample(all_doctors_for_embed, random_doctors_count)
    random_nurses = random.sample(all_nurses_for_embed, random_nurses_count)

    facilities_data.append({
        "doctors": random_doctors,
        "name": f"Centrum Krwiodawstwa {fake_pl.city()}",
        "address": fake_pl.address().replace("\n", ", "),
        "phone_number": fake_pl.phone_number(),
        "available_blood_bags": [],
        "nurses": random_nurses,
        "email": fake_pl.email()
    })

facilities_insert_result = facilities_collection.insert_many(facilities_data)
facilities_ids = list(facilities_insert_result.inserted_ids)
print(f"Inserted {len(facilities_ids)} facilities.")

orders_collection = db["orders"]
orders_collection.delete_many({})

hospitals_docs = list(hospitals_collection.find({}))
orders_data = []
for _ in range(COUNT_ORDERS):

    h = random.choice(hospitals_docs)
    hospital_embed = {
        "address": h["address"],
        "user_id": h["user_id"],
        "name": h["name"],
        "hospital_id": h["_id"]
    }

    realization_count = random.randint(0, 3)
    reals = []
    for __ in range(realization_count):
        real_date = fake_pl.date_between_dates(
            date_start=datetime(2020, 1, 1).date(),
            date_end=datetime.now().date()
        )
        real_date = datetime.combine(real_date, time.min)
        reals.append({
            "date": real_date,
            "transport": {
                "driver_id": random.choice(drivers_ids)
            },
            "blood_bags": []
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

blood_bags_collection = db["blood_bags"]
blood_bags_collection.delete_many({})

facilities_docs = list(facilities_collection.find({}))
donors_docs = list(donors_collection.find({}))
nurses_docs = list(nurses_collection.find({}))
orders_docs = list(orders_collection.find({}))

blood_bags_data = []
for _ in range(COUNT_BLOODBAGS):
    facility = random.choice(facilities_docs)
    donor = random.choice(donors_docs)
    nurse = random.choice(nurses_docs)
    maybe_order = random.choice([None, random.choice(orders_docs)])

    donation_date = fake_pl.date_between_dates(
        date_start=donor["birth_date"].date(),
        date_end=datetime.now().date()
    )
    donation_date = datetime.combine(donation_date, time.min)

    bag = {
        "volume": float(random.choice([300, 350, 450, 500])),
        "donation": {
            "date": donation_date,
            "donor_id": donor["_id"],
            "nurse_id": nurse["_id"]
        },
        "facility_id": facility["_id"]
    }

    lab_date = donation_date + timedelta(days=random.randint(1, 7))
    bag["lab_result"] = {
        "date": lab_date,
        "is_qualified": fake_pl.boolean(chance_of_getting_true=80)
    }

    if maybe_order:
        bag["order"] = maybe_order["_id"]

    blood_bags_data.append(bag)

CHUNK_SIZE = 1000
for i in range(0, len(blood_bags_data), CHUNK_SIZE):
    chunk = blood_bags_data[i: i + CHUNK_SIZE]
    blood_bags_collection.insert_many(chunk)

print(f"Inserted {len(blood_bags_data)} blood_bags.")

facility_to_bag_ids = {}
bags_cursor = blood_bags_collection.find({}, {"_id": 1, "facility_id": 1})
for doc in bags_cursor:
    f_id = doc["facility_id"]
    if f_id not in facility_to_bag_ids:
        facility_to_bag_ids[f_id] = []
    facility_to_bag_ids[f_id].append(doc["_id"])

for f_id, bag_ids in facility_to_bag_ids.items():
    num_available = random.randint(0, len(bag_ids))
    subset = random.sample(bag_ids, num_available)
    facilities_collection.update_one(
        {"_id": f_id},
        {"$set": {"available_blood_bags": subset}}
    )

print("Facilities updated with available blood bags.")

for doc in doctors_collection.find({}, {"_id": 1, "user_id": 1}):
    doctor_id = doc["_id"]
    user_id = doc["user_id"]
    db.users.update_one(
        {"_id": user_id},
        {"$push": {"profiles": {"role": "doctor", "doctor_id": doctor_id}}}
    )

for doc in donors_collection.find({}, {"_id": 1, "user_id": 1}):
    donor_id = doc["_id"]
    user_id = doc["user_id"]
    db.users.update_one(
        {"_id": user_id},
        {"$push": {"profiles": {"role": "donor", "donor_id": donor_id}}}
    )

for doc in moderators_collection.find({}, {"_id": 1, "user_id": 1}):
    mod_id = doc["_id"]
    user_id = doc["user_id"]
    db.users.update_one(
        {"_id": user_id},
        {"$push": {"profiles": {"role": "moderator", "moderator_id": mod_id}}}
    )

for doc in hospitals_collection.find({}, {"_id": 1, "user_id": 1}):
    hospital_id = doc["_id"]
    user_id = doc["user_id"]
    db.users.update_one(
        {"_id": user_id},
        {"$push": {"profiles": {"role": "hospital", "hospital_id": hospital_id}}}
    )

print("Users updated with role profiles.")

print("\nSeeding completed successfully!")
