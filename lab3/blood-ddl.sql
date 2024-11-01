CREATE TYPE "order_state" AS ENUM (
	'COMPLETED',
	'AWAITING',
	'CANCELED'
);

CREATE TYPE "blood_type" AS ENUM (
	'0',
	'A',
	'B',
	'AB'
);

CREATE TYPE "blood_rh" AS ENUM (
	'+',
	'-'
);

CREATE TYPE "sex" AS ENUM (
	'M',
	'F'
);

CREATE TYPE "certificate_level" AS ENUM (
	'I',
	'II',
	'III'
);

CREATE TYPE blood_info AS (
	blood_type BLOOD_TYPE,
	blood_rh BLOOD_RH
);

CREATE TABLE "doctors" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"fk_user_id" INTEGER NOT NULL,
	PRIMARY KEY("id")
);


CREATE TABLE "nurses" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"first_name" TEXT NOT NULL,
	"last_name" TEXT NOT NULL,
	"phone_number" TEXT CONSTRAINT "chk_phone_number_format" CHECK ("phone_number" ~ '^\+?\d{9,15}$'),
	PRIMARY KEY("id")
);


CREATE TABLE "moderators" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"fk_user_id" INTEGER NOT NULL,
	PRIMARY KEY("id")
);


CREATE TABLE "users" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"first_name" TEXT,
	"last_name" TEXT,
	"login" TEXT NOT NULL UNIQUE,
	"email" TEXT NOT NULL UNIQUE CONSTRAINT "chk_email_format" CHECK ("email" ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'),
	"password" TEXT NOT NULL CONSTRAINT "chk_password" CHECK ("password" ~* '^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W]).{6,20}$'),
	"phone_number" TEXT NOT NULL UNIQUE CONSTRAINT "chk_phone_number_format" CHECK ("phone_number" ~ '^\+?\d{9,15}$'),
	PRIMARY KEY("id")
);


CREATE TABLE "hospitals" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"name" TEXT NOT NULL,
	"address" TEXT NOT NULL,
	"fk_user_id" INTEGER NOT NULL,
	PRIMARY KEY("id")
);


CREATE TABLE "donors" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"pesel" TEXT NOT NULL CONSTRAINT "chk_pesel" CHECK ("pesel" ~ '^\d{11}$'),
	"birth_date" DATE NOT NULL CONSTRAINT "chk_donor_age" CHECK (age("birth_date") >= INTERVAL '18 years'),
	"sex" SEX NOT NULL,
	"blood_info" BLOOD_INFO NOT NULL,
	"fk_user_id" INTEGER NOT NULL,
	PRIMARY KEY("id")
);


CREATE TABLE "orders" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"date" DATE NOT NULL CONSTRAINT "chk_not_future_date" CHECK ("date" <= CURRENT_DATE),
	"state" ORDER_STATE NOT NULL DEFAULT 'AWAITING',
	"is_urgent" BOOLEAN NOT NULL,
	"fk_transport_id" INTEGER,
	"fk_hospital_id" INTEGER NOT NULL,
	PRIMARY KEY("id")
);


CREATE TABLE "transports" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"fk_driver_id" INTEGER NOT NULL,
	PRIMARY KEY("id")
);


CREATE TABLE "drivers" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"first_name" TEXT NOT NULL,
	"last_name" TEXT NOT NULL,
	PRIMARY KEY("id")
);


CREATE TABLE "examinations" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"date" DATE NOT NULL CONSTRAINT "chk_not_future_date" CHECK ("date" <= CURRENT_DATE),
	"weight" DECIMAL NOT NULL CONSTRAINT "chk_positive_weight" CHECK ("weight" > 0),
	"height" INTEGER NOT NULL CONSTRAINT "chk_positive_height" CHECK ("height" > 0),
	"diastolic_blood_pressure" INTEGER NOT NULL CONSTRAINT "chk_positive_dpressure" CHECK ("diastolic_blood_pressure" > 0),
	"systolic_blood_pressure" INTEGER NOT NULL CONSTRAINT "chk_positive_spressure" CHECK ("systolic_blood_pressure" > 0),
	"is_qualified" BOOLEAN NOT NULL,
	"form_number" TEXT NOT NULL UNIQUE,
	"fk_donor_id" INTEGER NOT NULL,
	"fk_doctor_id" INTEGER NOT NULL,
	PRIMARY KEY("id")
);


CREATE TABLE "donations" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"date" DATE NOT NULL CONSTRAINT "chk_not_future_date" CHECK ("date" <= CURRENT_DATE),
	"fk_donor_id" INTEGER NOT NULL,
	"fk_nurse_id" INTEGER NOT NULL,
	PRIMARY KEY("id")
);


CREATE TABLE "blood_bags" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"volume" INTEGER NOT NULL CONSTRAINT "chk_blood_bag_volume" CHECK ("volume" BETWEEN 0 AND 600),
	"fk_donation_id" INTEGER NOT NULL,
	"fk_lab_results_id" INTEGER,
	"fk_facility_id" INTEGER,
	PRIMARY KEY("id")
);


CREATE TABLE "lab_results" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"date" DATE NOT NULL CONSTRAINT "chk_not_future_date" CHECK ("date" <= CURRENT_DATE),
	"red_cells_count" DECIMAL NOT NULL CONSTRAINT "chk_red_cells_count" CHECK ("red_cells_count" >= 0),
	"white_cells_count" DECIMAL NOT NULL CONSTRAINT "chk_white_cells_count" CHECK ("white_cells_count" >= 0),
	"platelet_count" DECIMAL NOT NULL CONSTRAINT "chk_platelet_count" CHECK ("platelet_count" >= 0),
	"hemoglobin_level" DECIMAL NOT NULL CONSTRAINT "chk_hemoglobin_level" CHECK ("hemoglobin_level" >= 0),
	"hematocrit_level" DECIMAL NOT NULL CONSTRAINT "chk_hematocrit_level" CHECK ("hematocrit_level" >= 0),
	"glucose_level" DECIMAL NOT NULL CONSTRAINT "chk_glucose_level" CHECK ("glucose_level" >= 0),
	"is_qualified" BOOLEAN NOT NULL,
	PRIMARY KEY("id")
);


CREATE TABLE "facilities" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"name" TEXT NOT NULL,
	"address" TEXT NOT NULL,
	"email" TEXT NOT NULL UNIQUE CONSTRAINT "chk_email_format" CHECK ("email" ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'),
	"phone_number" TEXT NOT NULL UNIQUE CONSTRAINT "chk_phone_number_format" CHECK ("phone_number" ~ '^\+?\d{9,15}$'),
	PRIMARY KEY("id")
);


CREATE TABLE "doctors_facilities" (
	"fk_doctor_id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"fk_facility_id" INTEGER NOT NULL,
	PRIMARY KEY("fk_doctor_id", "fk_facility_id")
);


CREATE TABLE "nurses_facilities" (
	"fk_nurse_id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"fk_facility_id" INTEGER NOT NULL,
	PRIMARY KEY("fk_nurse_id", "fk_facility_id")
);


CREATE TABLE "certificates" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"level" CERTIFICATE_LEVEL NOT NULL,
	"acquisition_date" DATE NOT NULL,
	"fk_donor_id" INTEGER NOT NULL,
	PRIMARY KEY("id")
);
ALTER TABLE "certificates" ADD CONSTRAINT "unique_donor_level" UNIQUE ("fk_donor_id", "level");

CREATE TABLE "blood_bags_orders" (
	"fk_blood_bag_id" INTEGER NOT NULL,
	"fk_order_id" INTEGER NOT NULL,
	PRIMARY KEY("fk_blood_bag_id", "fk_order_id")
);

ALTER TABLE "transports"
ADD FOREIGN KEY("fk_driver_id") REFERENCES "drivers"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "orders"
ADD FOREIGN KEY("fk_transport_id") REFERENCES "transports"("id")
ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "orders"
ADD FOREIGN KEY("fk_hospital_id") REFERENCES "hospitals"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "doctors_facilities"
ADD FOREIGN KEY("fk_doctor_id") REFERENCES "doctors"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "doctors_facilities"
ADD FOREIGN KEY("fk_facility_id") REFERENCES "facilities"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "nurses_facilities"
ADD FOREIGN KEY("fk_nurse_id") REFERENCES "nurses"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "nurses_facilities"
ADD FOREIGN KEY("fk_facility_id") REFERENCES "facilities"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "donations"
ADD FOREIGN KEY("fk_donor_id") REFERENCES "donors"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "certificates"
ADD FOREIGN KEY("fk_donor_id") REFERENCES "donors"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "blood_bags"
ADD FOREIGN KEY("fk_donation_id") REFERENCES "donations"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "blood_bags"
ADD FOREIGN KEY("fk_lab_results_id") REFERENCES "lab_results"("id")
ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE "donations"
ADD FOREIGN KEY("fk_nurse_id") REFERENCES "nurses"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "blood_bags"
ADD FOREIGN KEY("fk_facility_id") REFERENCES "facilities"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "examinations"
ADD FOREIGN KEY("fk_donor_id") REFERENCES "donors"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "examinations"
ADD FOREIGN KEY("fk_doctor_id") REFERENCES "doctors"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "doctors"
ADD FOREIGN KEY("fk_user_id") REFERENCES "users"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "moderators"
ADD FOREIGN KEY("fk_user_id") REFERENCES "users"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "hospitals"
ADD FOREIGN KEY("fk_user_id") REFERENCES "users"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "donors"
ADD FOREIGN KEY("fk_user_id") REFERENCES "users"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "blood_bags_orders"
ADD FOREIGN KEY("fk_blood_bag_id") REFERENCES "blood_bags"("id")
ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE "blood_bags_orders"
ADD FOREIGN KEY("fk_order_id") REFERENCES "orders"("id")
ON UPDATE CASCADE ON DELETE CASCADE;