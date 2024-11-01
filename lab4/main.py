import psycopg2
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker for generating random names and other data
fake = Faker(['pl-PL'])
Faker.seed(12)

# Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname="blood",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)
cur = conn.cursor()


def remove_polish_signs(name):
    # Translation table for Polish letters to their Latin equivalents
    polish_chars = str.maketrans(
        "ąćęłńóśźżü",
        "acelnoszzu"
    )

    return name.translate(polish_chars)


def random_email(firstname, lastname):
    # Remove Polish signs and convert to lowercase
    firstname = remove_polish_signs(firstname.lower().replace(" ", ""))
    lastname = remove_polish_signs(lastname.lower().replace(" ", ""))

    # List of common email domains
    domains = ["example.com", "mail.com", "webmail.com", "testmail.com", "demo.com"]

    # Generate random parts of the email
    options = [
        f"{firstname[0]}{lastname}",  # First initial + last name
        f"{firstname}{lastname[0]}",  # First name + last initial
        f"{firstname}{random.choice(['.', '_'])}{lastname}",  # Full first name + separator + last name
        f"{firstname[:3]}{lastname[:3]}",  # First 3 letters of first and last name
        f"{lastname}{firstname[0]}",  # Last name + first initial
    ]

    options = [f"{option}{random.randint(1, 9999)}" for option in options]

    # Choose a random option and domain
    email_local = random.choice(options)
    domain = random.choice(domains)

    # Combine local part and domain
    return f"{email_local}@{domain}"


def random_login(firstname, lastname):
    # List of common separators for usernames
    separators = ["", ".", "_", "-"]
    firstname = remove_polish_signs(firstname.lower().replace(" ", ""))
    lastname = remove_polish_signs(lastname.lower().replace(" ", ""))

    # Generate possible login patterns
    options = [
        f"{firstname[0]}{lastname}",  # First initial + last name
        f"{firstname}{lastname[0]}",  # First name + last initial
        f"{firstname}{random.choice(separators)}{lastname}",  # Full first + separator + last
        f"{firstname[:3]}{lastname[:3]}",  # First 3 letters of each
        f"{lastname}{firstname[0]}",  # Last name + first initial
    ]

    options = [f"{option}{random.randint(1, 9999)}" for option in options]

    # Select a random login format
    return random.choice(options)


def insert_users(n):
    for _ in range(n):
        first_name = fake.first_name()
        last_name = fake.last_name()
        login = random_login(first_name, last_name)

        email = random_email(first_name, last_name)
        password = fake.password(length=10, special_chars=True, upper_case=True)
        if "_" in password:
            password = password.replace("_", "!")
        phone_number = ''.join([str(random.randint(0, 9)) for _ in range(9)])

        cur.execute("""
            INSERT INTO "users" (first_name, last_name, login, email, password, phone_number)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, login, email, password, phone_number))


def insert_doctors(n):
    cur.execute('SELECT id FROM "users" ORDER BY random() LIMIT %s', (n,))
    user_ids = cur.fetchall()
    for user_id in user_ids:
        cur.execute("""
            INSERT INTO "doctors" (fk_user_id)
            VALUES (%s)
        """, (user_id[0],))


def insert_nurses(n):
    for _ in range(n):
        first_name = fake.first_name()
        last_name = fake.last_name()
        phone_number = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        cur.execute("""
            INSERT INTO "nurses" (first_name, last_name, phone_number)
            VALUES (%s, %s, %s)
        """, (first_name, last_name, phone_number))


def insert_moderators(n):
    cur.execute('SELECT id FROM "users" ORDER BY random() LIMIT %s', (n,))
    user_ids = cur.fetchall()
    for user_id in user_ids:
        cur.execute("""
            INSERT INTO "moderators" (fk_user_id)
            VALUES (%s)
        """, (user_id[0],))


def insert_hospitals(n):
    cur.execute('SELECT id FROM "users" ORDER BY random() LIMIT %s', (n,))
    user_ids = cur.fetchall()
    for user_id in user_ids:
        name = fake.company()
        address = fake.address()
        cur.execute("""
            INSERT INTO "hospitals" (name, address, fk_user_id)
            VALUES (%s, %s, %s)
        """, (name, address, user_id[0]))


def insert_donors(n):
    cur.execute('SELECT id FROM "users" ORDER BY random() LIMIT %s', (n,))
    user_ids = cur.fetchall()
    blood_types = ['0', 'A', 'B', 'AB']
    blood_rhs = ['+', '-']
    sexes = ['M', 'F']
    for user_id in user_ids:
        pesel = ''.join([str(random.randint(0, 9)) for _ in range(11)])
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=60)
        sex = random.choice(sexes)
        blood_type = random.choice(blood_types)
        blood_rh = random.choice(blood_rhs)
        cur.execute("""
            INSERT INTO "donors" (pesel, birth_date, sex, blood_info, fk_user_id)
            VALUES (%s, %s, %s, ROW(%s, %s)::blood_info, %s)
        """, (pesel, birth_date, sex, blood_type, blood_rh, user_id[0]))


def insert_drivers(n):
    for _ in range(n):
        first_name = fake.first_name()
        last_name = fake.last_name()
        cur.execute("""
            INSERT INTO "drivers" (first_name, last_name)
            VALUES (%s, %s)
        """, (first_name, last_name))


def insert_transports(n):
    cur.execute('SELECT id FROM "drivers" ORDER BY random() LIMIT %s', (n,))
    driver_ids = cur.fetchall()
    for driver_id in driver_ids:
        cur.execute("""
            INSERT INTO "transports" (fk_driver_id)
            VALUES (%s)
        """, (driver_id[0],))


def insert_orders(n):
    # Fetch hospitals and transports from the database
    cur.execute('SELECT id FROM "hospitals"')
    hospital_ids = [h[0] for h in cur.fetchall()]
    cur.execute('SELECT id FROM "transports"')
    transport_ids = [t[0] for t in cur.fetchall()]

    states = ['COMPLETED', 'AWAITING', 'CANCELED']
    num_hospitals = len(hospital_ids)
    num_transports = len(transport_ids)

    for i in range(n):
        order_date = datetime.now() - timedelta(days=random.randint(1, 3000))
        state = random.choice(states)
        is_urgent = random.choice([True, False])

        # Use modulo to loop over available hospital and transport IDs if not enough in database
        hospital_id = hospital_ids[i % num_hospitals]
        transport_id = transport_ids[i % num_transports] if num_transports > 0 else None

        cur.execute("""
            INSERT INTO "orders" (date, state, is_urgent, fk_transport_id, fk_hospital_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (order_date, state, is_urgent, transport_id, hospital_id))


def insert_donations_and_examinations(n):
    cur.execute('SELECT id FROM "donors" ORDER BY random() LIMIT %s', (n,))
    donor_ids = cur.fetchall()

    cur.execute('SELECT id FROM "doctors" ORDER BY random()')
    doctor_ids = [doc[0] for doc in cur.fetchall()]

    cur.execute('SELECT id FROM "facilities" ORDER BY random()')
    facility_ids = [fac[0] for fac in cur.fetchall()]

    cur.execute('SELECT id FROM "nurses" ORDER BY random()')
    nurse_ids = [nurse[0] for nurse in cur.fetchall()]

    for donor_id in donor_ids:
        # Generate a random donation date
        donation_date = datetime.now() - timedelta(days=random.randint(1, 30))  # Donation date
        nurse_id = random.choice(nurse_ids)
        # Insert donation
        cur.execute("""
            INSERT INTO "donations" (date, fk_donor_id, fk_nurse_id)
            VALUES (%s, %s, %s) RETURNING id
        """, (donation_date, donor_id[0], nurse_id))
        donation_id = cur.fetchone()[0]

        # Insert examination with fk_doctor_id
        weight = round(random.uniform(50.0, 100.0), 2)  # Random weight between 50kg and 100kg
        height = random.randint(150, 200)  # Random height between 150cm and 200cm
        diastolic_blood_pressure = random.randint(60, 90)
        systolic_blood_pressure = random.randint(90, 140)
        is_qualified = random.choice([True, True, True, True, True, True, True, True, False])

        doctor_id = random.choice(doctor_ids)  # Select random doctor ID

        form_number = random.randint(500000000, 600000000)
        cur.execute("""
            INSERT INTO "examinations" (date, weight, height, diastolic_blood_pressure, systolic_blood_pressure, is_qualified, form_number, fk_donor_id, fk_doctor_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            donation_date, weight, height, diastolic_blood_pressure, systolic_blood_pressure, is_qualified, form_number,
            donor_id[0],
            doctor_id))

        red_cells_count = round(random.uniform(4.0, 6.0), 2)
        white_cells_count = round(random.uniform(4.0, 11.0), 2)
        platelet_count = round(random.uniform(150, 450), 2)
        hemoglobin_level = round(random.uniform(12.0, 18.0), 2)
        hematocrit_level = round(random.uniform(36.0, 52.0), 2)
        glucose_level = round(random.uniform(70, 140), 2)
        is_qualified = random.choice([True, True, True, True, True, True, True, True, False])
        lab_result_date = donation_date + timedelta(days=random.randint(1, 7))
        if lab_result_date > datetime.now():
            lab_result_date = datetime.now()

        # Insert lab result associated with the examination
        cur.execute("""
            INSERT INTO "lab_results" (date, red_cells_count, white_cells_count, platelet_count,
                                       hemoglobin_level, hematocrit_level, glucose_level, is_qualified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (lab_result_date, red_cells_count, white_cells_count, platelet_count,
              hemoglobin_level, hematocrit_level, glucose_level, is_qualified))

        lab_result_id = cur.fetchone()[0]

        # Insert blood bag with fk_donation_id, fk_lab_results_id, and fk_facility_id
        volume = random.choice([450, 500, 550])  # Common blood bag volumes in ml
        facility_id = random.choice(facility_ids)  # Select a random facility

        cur.execute("""
            INSERT INTO "blood_bags" (volume, fk_donation_id, fk_lab_results_id, fk_facility_id)
            VALUES (%s, %s, %s, %s)
        """, (volume, donation_id, lab_result_id, facility_id))


def insert_facilities(n):
    for _ in range(n):
        # Generate random facility name, address, and phone number
        number_of_facility = random.randint(100, 999)
        name = f"Placówka Donacji {number_of_facility}"
        address = f"{random.randint(1, 999)} {random.choice(['Kwiatowa', 'Złota', 'Generalna', 'Wyszyńskiego'])}"
        phone_number = ''.join([str(random.randint(0, 9)) for _ in range(9)])  # Generate a 9-digit phone number
        email = f"placowka{number_of_facility}@krew.pl"
        # Insert into the database
        cur.execute("""
            INSERT INTO "facilities" (name, address, email, phone_number)
            VALUES (%s, %s, %s, %s)
        """, (name, address, email, phone_number))


# Call functions to populate tables
insert_users(5000)
insert_doctors(20)
insert_nurses(30)
insert_moderators(10)
insert_hospitals(10)
insert_donors(2000)
insert_drivers(15)
insert_transports(10000)
insert_orders(20)
insert_facilities(5)
for i in range(100):
    insert_donations_and_examinations(50)

# Commit and close connection
conn.commit()
cur.close()
conn.close()
print("Database populated with random data.")
