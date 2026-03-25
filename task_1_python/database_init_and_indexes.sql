DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS rooms;

CREATE TABLE rooms (
    id INT PRIMARY KEY,
    name TEXT
);

CREATE TABLE students (
    id INT PRIMARY KEY,
    name TEXT,
    birthday TIMESTAMP,
    sex TEXT,
    room_id INT REFERENCES rooms(id)
);


CREATE INDEX idx_students_room_id ON students (room_id);
CREATE INDEX idx_students_sex ON students (sex);
CREATE INDEX idx_students_birthday ON students (birthday);
