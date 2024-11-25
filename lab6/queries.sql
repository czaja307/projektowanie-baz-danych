-- liczba dawcow kazdej grupy krwi
EXPLAIN SELECT (blood_info).blood_type::text || (blood_info).blood_rh::text AS blood_group,
       COUNT(*)                                                     as donor_count
FROM donors
GROUP BY (blood_info).blood_type, (blood_info).blood_rh
ORDER BY donor_count;


-- zlicza dostepne torebki pogrupowane grupa krwi
EXPLAIN SELECT (donors.blood_info).blood_type::text || (donors.blood_info).blood_rh::text AS blood_group,
       COUNT(blood_bags.id)                                                       as avaiable_bags
FROM blood_bags
         JOIN donations ON blood_bags.fk_donation_id = donations.id
         JOIN donors ON donations.fk_donor_id = donors.id
         LEFT JOIN blood_bags_orders ON blood_bags.id = blood_bags_orders.fk_blood_bag_id
         JOIN lab_results ON blood_bags.fk_lab_results_id = lab_results.id
WHERE blood_bags_orders.fk_blood_bag_id IS NULL
  AND lab_results.is_qualified = TRUE
GROUP BY (donors.blood_info).blood_type, (donors.blood_info).blood_rh
ORDER BY avaiable_bags;

-- zlicza donorow i ich donacje
EXPLAIN SELECT donors.id,
       users.first_name,
       users.last_name,
       COUNT(donations.id) AS donation_count
FROM donations
         JOIN donors ON donations.fk_donor_id = donors.id
         JOIN users ON donors.fk_user_id = users.id
GROUP BY donors.id, users.first_name, users.last_name
ORDER BY donation_count DESC;

-- zlicza zdyskwalifikowane procentowo
EXPLAIN SELECT COUNT(*) * 100.0 / (SELECT COUNT(*) FROM examinations) AS disqualified_precentage
FROM examinations
WHERE is_qualified = FALSE;

-- lista donorow ktorzy moga znowu oddac krew
EXPLAIN SELECT donors.id,
       users.first_name,
       users.last_name,
       MAX(donations.date) AS last_donation_date
FROM donations
         JOIN donors ON donations.fk_donor_id = donors.id
         JOIN users ON donors.fk_user_id = users.id
GROUP BY donors.id, users.first_name, users.last_name
HAVING MAX(donations.date) <= CURRENT_DATE - INTERVAL '1 months'
ORDER BY last_donation_date;

-- pobiera pilne zamówienia oczekujące wraz z nazwą szpitala
EXPLAIN SELECT orders.*,
       hospitals.name    AS hospital_name,
       hospitals.address AS hospital_address
FROM orders
         JOIN
     hospitals ON orders.fk_hospital_id = hospitals.id
WHERE orders.state = 'AWAITING'
  AND orders.is_urgent = TRUE;

-- Pobiera dawców, którzy oddali krew więcej niż 5 razy w ciągu ostatniego roku, z imieniem użytkownika
EXPLAIN SELECT users.first_name    AS first_name,
       users.last_name     AS last_name,
       donors.*,
       COUNT(donations.id) AS donation_count
FROM donors
         JOIN
     donations ON donors.id = donations.fk_donor_id
         JOIN
     users ON donors.fk_user_id = users.id
WHERE donations.date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY donors.id, users.first_name, users.last_name
HAVING COUNT(donations.id) > 5
ORDER BY donation_count DESC;

-- Oblicza średnią wagę i wzrost z tabeli badań
EXPLAIN SELECT AVG(weight) AS avg_weight,
       AVG(height) AS avg_height
FROM examinations;

-- Oblicza średnie wyniki badań dla wszystkich grup krwi
EXPLAIN SELECT (donors.blood_info).blood_type::text || (donors.blood_info).blood_rh::text AS blood_group,
       AVG(lab_results.hemoglobin_level)                                          AS avg_hemoglobin,
       AVG(lab_results.red_cells_count)                                           AS avg_red_cells_count,
       AVG(lab_results.white_cells_count)                                         AS avg_white_cells_count,
       AVG(lab_results.platelet_count)                                            AS avg_platelet_count,
       AVG(lab_results.hematocrit_level)                                          AS avg_hematocrit_level,
       AVG(lab_results.glucose_level)                                             AS avg_glucose_level
FROM lab_results
         JOIN
     blood_bags ON blood_bags.fk_lab_results_id = lab_results.id
         JOIN
     donations ON blood_bags.fk_donation_id = donations.id
         JOIN
     donors ON donations.fk_donor_id = donors.id
GROUP BY blood_group;

-- Pobiera listę lekarzy którzy przeprowadzali badania w 2024 roku i sortuje malejąco po ilości badań
CREATE INDEX idx_examinations_date_year ON examinations (date);
CREATE INDEX idx_users_full_name ON users (first_name, last_name);

EXPLAIN SELECT doctors.id,
       users.first_name,
       users.last_name,
       COUNT(examinations.id) AS examination_count
FROM doctors
         JOIN
     users ON doctors.fk_user_id = users.id
         JOIN
     examinations ON doctors.id = examinations.fk_doctor_id
WHERE EXTRACT(YEAR FROM examinations.date) = 2024
GROUP BY doctors.id, users.first_name, users.last_name
ORDER BY examination_count DESC;

-- Statystyki dla placówek - liczba donacji, ilość zakwalifikowanych donacji i liczba dostępnych worków z krwią
EXPLAIN SELECT facilities.id                       AS facility_id,
       facilities.name                     AS facility_name,
       COUNT(donations.id)                 AS total_donations,
       (SELECT COUNT(*)
        FROM blood_bags bb
                 JOIN lab_results lr ON bb.fk_lab_results_id = lr.id
        WHERE bb.fk_facility_id = facilities.id
          AND lr.is_qualified IS TRUE)     AS qualified_donations,
       (SELECT COUNT(*)
        FROM blood_bags bb
                 JOIN lab_results lr ON bb.fk_lab_results_id = lr.id
                 LEFT JOIN blood_bags_orders bbo ON bb.id = bbo.fk_blood_bag_id
        WHERE bb.fk_facility_id = facilities.id
          AND lr.is_qualified IS TRUE
          AND bbo.fk_blood_bag_id IS NULL) AS available_blood_bags
FROM "facilities"
         LEFT JOIN "blood_bags" ON blood_bags.fk_facility_id = facilities.id
         LEFT JOIN "donations" ON blood_bags.fk_donation_id = donations.id
         LEFT JOIN "lab_results" ON blood_bags.fk_lab_results_id = lab_results.id
GROUP BY facilities.id, facilities.name
ORDER BY available_blood_bags DESC;


-- Średni czas potrzebny na kwalifikację torebki krwi w placówce
EXPLAIN SELECT facilities.id                          AS facility_id,
       facilities.name                        AS facility_name,
       AVG(lab_results.date - donations.date) AS avg_qualification_time
FROM lab_results
         JOIN
     blood_bags ON lab_results.id = blood_bags.fk_lab_results_id
         JOIN
     donations ON blood_bags.fk_donation_id = donations.id
         JOIN
     facilities ON blood_bags.fk_facility_id = facilities.id
GROUP BY facilities.id, facilities.name
ORDER BY avg_qualification_time;

-- Donorzy z certyfikatem i ilością oddanej krwi
EXPLAIN SELECT donors.id,
       users.first_name,
       users.last_name,
       certificates.level,
       certificates.acquisition_date,
       COALESCE(SUM(blood_bags.volume), 0) AS donated_blood_ml
FROM donors
         JOIN users ON donors.fk_user_id = users.id
         JOIN certificates ON certificates.fk_donor_id = donors.id
         LEFT JOIN donations ON donations.fk_donor_id = donors.id
         LEFT JOIN blood_bags ON blood_bags.fk_donation_id = donations.id
GROUP BY donors.id, users.first_name, users.last_name, certificates.level, certificates.acquisition_date
ORDER BY certificates.level;


-- Średnia ilość donacji na dawcę
EXPLAIN SELECT AVG(donation_count) AS avg_donations_per_donor
FROM (SELECT COUNT(donations.id) AS donation_count
      FROM donors
               LEFT JOIN donations ON donations.fk_donor_id = donors.id
      GROUP BY donors.id) AS donor_donations;

-- Ilość zamówień zrobionych przez kazdy szpital
EXPLAIN SELECT hospitals.id,
       hospitals.name,
       COUNT(orders.id) AS order_count
FROM hospitals
         JOIN orders ON orders.fk_hospital_id = hospitals.id
GROUP BY hospitals.id, hospitals.name
ORDER BY order_count DESC;

--TEST
CREATE INDEX idx_donors_blood_info ON donors (((blood_info).blood_type), ((blood_info).blood_rh));

SELECT donors.id,
       users.first_name,
       users.last_name,
       (donors.blood_info).blood_type AS blood_type,
       (donors.blood_info).blood_rh AS blood_rh,
       MAX(donations.date) AS last_donation_date
FROM donors
         JOIN users ON donors.fk_user_id = users.id
         JOIN donations ON donors.id = donations.fk_donor_id
WHERE (donors.blood_info).blood_type = 'A'
  AND (donors.blood_info).blood_rh = '+'
  AND donations.date > '2023-01-01'
GROUP BY donors.id, users.first_name, users.last_name, (donors.blood_info).blood_type, (donors.blood_info).blood_rh
ORDER BY users.last_name, users.first_name;
