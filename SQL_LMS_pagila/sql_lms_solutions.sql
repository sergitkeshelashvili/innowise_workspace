-- Output the number of movies in each category, sorted descending

SELECT cat.name, COUNT(*) AS movie_counted
FROM film f
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category cat ON fc.category_id = cat.category_id
GROUP BY cat.name
ORDER BY movie_counted DESC;

-- Output the 10 actors whose movies rented the most, sorted in descending order

SELECT a.actor_id,
       a.first_name,
       a.last_name,
       COUNT(r.rental_id) AS rentals_counted
FROM actor a
JOIN film_actor fa ON a.actor_id = fa.actor_id
JOIN inventory i ON fa.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY rentals_counted DESC
LIMIT 10;

-- Output the category of movies on which the most money was spent

SELECT cat.name,
       SUM(p.amount) AS total_revenue
FROM payment p
JOIN rental r ON p.rental_id = r.rental_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film_category fc ON i.film_id = fc.film_id
JOIN category cat ON fc.category_id = cat.category_id
GROUP BY cat.name
ORDER BY total_revenue DESC
LIMIT 1;

-- Print the names of movies that are not in the inventory.
-- Write a query without using the IN operator.

SELECT f.title
FROM film f
LEFT JOIN inventory i ON f.film_id = i.film_id
WHERE i.inventory_id IS NULL;

-- Output the top 3 actors who have appeared the most in movies in the “Children” category.
-- If several actors have the same number of movies, output all of them.

WITH actors_counted AS (
    SELECT a.actor_id,
           a.first_name,
           a.last_name,
           COUNT(*) AS movie_count
    FROM actor a
    JOIN film_actor fa ON a.actor_id = fa.actor_id
    JOIN film_category fc ON fa.film_id = fc.film_id
    JOIN category cat ON fc.category_id = cat.category_id
    WHERE cat.name = 'Children'
    GROUP BY a.actor_id, a.first_name, a.last_name
),
ranked AS (
    SELECT *,
           DENSE_RANK() OVER (ORDER BY movie_count DESC) AS rnk
    FROM actors_counted
)
SELECT *
FROM ranked
WHERE rnk <= 3;


-- Output cities with the number of active and inactive customers (active - customer.active = 1).
-- Sort by the number of inactive customers in descending order.

SELECT ci.city,
       SUM(CASE WHEN c.active = 1 THEN 1 ELSE 0 END) AS active_customers,
       SUM(CASE WHEN c.active = 0 THEN 1 ELSE 0 END) AS inactive_customers
FROM customer c
JOIN address a ON c.address_id = a.address_id
JOIN city ci ON a.city_id = ci.city_id
GROUP BY ci.city
ORDER BY inactive_customers DESC;

-- Output the category of movies that have the highest number of total rental hours in the city (customer.address_id in this city)
-- and that start with the letter “a”. Do the same for cities that have a “-” in them. Write everything in one query.

WITH total_rental_hours AS (
    SELECT ci.city,
           c.name AS category,
           SUM(EXTRACT(EPOCH FROM (r.return_date - r.rental_date)) / 3600) AS total_hours
    FROM rental r
    JOIN customer cu ON r.customer_id = cu.customer_id
    JOIN address a ON cu.address_id = a.address_id
    JOIN city ci ON a.city_id = ci.city_id
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film_category fc ON i.film_id = fc.film_id
    JOIN category c ON fc.category_id = c.category_id
    WHERE ci.city ILIKE 'a%' OR ci.city LIKE '%-%'
    GROUP BY ci.city, c.name
),
ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY city ORDER BY total_hours DESC) AS rn
    FROM total_rental_hours
)
SELECT city, category, total_hours
FROM ranked
WHERE rn = 1;
