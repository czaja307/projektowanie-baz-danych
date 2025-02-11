-- backup
ALTER TABLE "orders" RENAME TO "orders_arch";

-- new tables
CREATE TABLE "realizations" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"date" DATE NOT NULL,
	"fk_transport_id" INTEGER NOT NULL,
	PRIMARY KEY("id")
);

CREATE TABLE "realization_orders" (
	"fk_realization_id" INTEGER NOT NULL,
	"fk_order_id" INTEGER NOT NULL,
	PRIMARY KEY("fk_realization_id", "fk_order_id"),
	CONSTRAINT "realization_fk" FOREIGN KEY ("fk_realization_id") REFERENCES "realizations" ("id") ON DELETE CASCADE,
	CONSTRAINT "order_fk" FOREIGN KEY ("fk_order_id") REFERENCES "orders_arch" ("id") ON DELETE CASCADE
);

CREATE TABLE "orders" (
	"id" INTEGER NOT NULL UNIQUE GENERATED BY DEFAULT AS IDENTITY,
	"date" DATE NOT NULL CONSTRAINT "chk_not_future_date" CHECK ("date" <= CURRENT_DATE),
	"state" ORDER_STATE NOT NULL DEFAULT 'AWAITING',
	"is_urgent" BOOLEAN NOT NULL,
	"fk_hospital_id" INTEGER NOT NULL,
	PRIMARY KEY("id"),
	CONSTRAINT "hospital_fk" FOREIGN KEY ("fk_hospital_id") REFERENCES "hospitals" ("id") ON DELETE CASCADE
);

-- alter existing
ALTER TABLE "blood_bags"
ADD COLUMN "fk_realization_id" INTEGER,
ADD CONSTRAINT "fk_realization_id" FOREIGN KEY ("realization_id") REFERENCES "realizations" ("id") ON DELETE SET NULL;

--move data
INSERT INTO "realizations" ("date", "fk_transport_id")
SELECT "date", "fk_transport_id"
FROM "orders_arch"
WHERE "fk_transport_id" IS NOT NULL;

INSERT INTO "orders" ("id", "date", "state", "is_urgent", "fk_hospital_id")
SELECT "id", "date", "state", "is_urgent", "fk_hospital_id"
FROM "orders_arch";

INSERT INTO "realization_orders" ("fk_realization_id", "fk_order_id")
SELECT r."id", o."id"
FROM "realizations" AS r
JOIN "orders_arch" AS o
ON r."date" = o."date" AND r."fk_transport_id" = o."fk_transport_id";

-- drop constraints tables
ALTER TABLE "blood_bags_orders" DROP CONSTRAINT IF EXISTS "blood_bags_orders_fk_order_id_fkey";
ALTER TABLE "realization_orders" DROP CONSTRAINT IF EXISTS "order_fk";

-- drop unused tables
DROP TABLE IF EXISTS "blood_bags_orders";
DROP TABLE IF EXISTS "orders_arch";