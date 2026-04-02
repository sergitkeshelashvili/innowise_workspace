-- 1) Create a table 'test_schedule' to store the parameters
CREATE TABLE test_schedule (
    id SERIAL PRIMARY KEY,
    param_1 DATE,
    param_2 TIMESTAMP,
    param_3 DATE
);


-- 2) Insert data into the table 'test_schedule'
INSERT INTO test_schedule (param_1, param_2, param_3)
VALUES
    ('2025-02-06', '2025-02-12 09:38:25.999982', '2025-01-28'),
    ('2025-02-14', '2025-02-14 16:17:14.095384', '2025-02-06'),
    ('2025-02-20', '2025-02-21 08:41:53.643244', '2025-02-14'),
    ('2025-02-25', '2025-03-11 15:52:28.575590', '2025-02-20'),
    ('2025-03-06', '2025-03-13 15:35:21.729785', '2025-02-25'),
    ('2025-03-13', '2025-03-13 16:32:27.178218', '2025-03-06'),
    ('2025-03-20', '2025-03-26 08:35:19.585812', '2025-03-13'),
    ('2025-03-27', '2025-03-28 07:23:03.611707', '2025-03-20'),
    ('2025-04-07', '2025-04-08 18:57:03.804270', '2025-03-27'),
    ('2025-04-10', '2025-04-15 11:19:51.275211', '2025-04-07'),
    ('2025-04-14', '2025-04-15 14:34:32.097939', '2025-04-10'),
    ('2025-04-24', '2025-04-24 14:41:48.705573', '2025-04-14'),
    ('2025-05-02', '2025-05-08 11:05:44.640510', '2025-04-24'),
    ('2025-05-15', '2025-05-21 10:00:08.361011', '2025-05-02'),
    ('2025-05-22', '2025-05-28 08:07:06.096731', '2025-05-15'),
    ('2025-05-29', '2025-05-30 10:01:45.906511', '2025-05-22'),
    ('2025-06-05', '2025-06-09 09:22:04.668390', '2025-05-29'),
    ('2025-06-19', '2025-07-03 08:27:40.115104', '2025-06-05'),
    ('2025-06-26', '2025-07-03 09:15:38.292950', '2025-06-19'),
    ('2025-07-03', '2025-07-07 10:53:30.915895', '2025-06-26');



-- 3) Create Procedure that handles the logic for each data set

CREATE OR REPLACE PROCEDURE test_2(
    p_date1 DATE,
    p_timestamp TIMESTAMP,
    p_date2 DATE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE NOTICE 'Executing for: %, %, %', p_date1, p_timestamp, p_date2;
END;
$$;


-- 4) Run Procedure: Automate the execution using a loop, pass every row into the procedure

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT param_1, param_2, param_3 FROM test_schedule ORDER BY id LOOP

        CALL test_2(r.param_1, r.param_2, r.param_3);

    END LOOP;
END $$;
