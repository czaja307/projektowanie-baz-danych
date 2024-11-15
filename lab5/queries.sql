-- liczba dawcow kazdej grupy krwi
SELECT
	(blood_info).blood_type::text || (blood_info).blood_rh::text AS blood_group,
	COUNT(*) as donor_count
FROM donors
GROUP BY (blood_info).blood_type, (blood_info).blood_rh
ORDER BY donor_count ASC;


-- zlicza dostepne torebki pogrupowane grupa krwi
SELECT
	(donors.blood_info).blood_type::text || (donors.blood_info).blood_rh::text AS blood_group,
	COUNT(blood_bags.id) as avaiable_bags
FROM blood_bags
JOIN donations ON blood_bags.fk_donation_id = donations.id
JOIN donors ON donations.fk_donor_id = donors.id
LEFT JOIN blood_bags_orders ON blood_bags.id = blood_bags_orders.fk_blood_bag_id
JOIN lab_results ON blood_bags.fk_lab_results_id = lab_results.id
WHERE blood_bags_orders.fk_blood_bag_id IS NULL
	AND lab_results.is_qualified = TRUE
GROUP BY (donors.blood_info).blood_type, (donors.blood_info).blood_rh
ORDER BY avaiable_bags ASC;

-- zlicza donorow i ich donacje
SELECT
	donors.id, users.first_name, users.last_name,
	COUNT(donations.id) AS donation_count
FROM donations
JOIN donors ON donations.fk_donor_id = donors.id
JOIN users ON donors.fk_user_id = users.id
GROUP BY donors.id, users.first_name, users.last_name
ORDER BY donation_count DESC

-- zlicza zdyskwalifikowane procentowo
SELECT
	COUNT(*) * 100.0 / (SELECT COUNT(*) FROM examinations) AS disqualified_precentage
FROM examinations
WHERE is_qualified = FALSE;

-- lista donorow ktorzy moga znowu oddac krew
SELECT
	donors.id, users.first_name, users.last_name,
	MAX (donations.date) AS last_donation_date
FROM donations
JOIN donors ON donations.fk_donor_id = donors.id
JOIN users ON donors.fk_user_id = users.id
GROUP BY donors.id, users.first_name, users.last_name
HAVING MAX(donations.date) <= CURRENT_DATE - INTERVAL '1 months'
ORDER BY last_donation_date ASC;