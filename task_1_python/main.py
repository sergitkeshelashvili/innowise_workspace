#!/usr/bin/env python3
import argparse
import json
import psycopg2
import xml.etree.ElementTree as ET
import sys
import decimal
from datetime import datetime
from psycopg2.extras import execute_batch


### Database Connection
class Database:
  

    def __init__(self, dbname, user, password, host="localhost", port=5432):
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            self.conn.autocommit = True
        except Exception as e:
            print(f"Connection Error: {e}")
            sys.exit(1)

    def get_cursor(self):
        return self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()


### Database Schema: Initializes the database tables and indexes for optimization
def create_schema(db):

    with db.get_cursor() as cursor:
        cursor.execute("""
                       DROP TABLE IF EXISTS students CASCADE;
                       DROP TABLE IF EXISTS rooms CASCADE;

                       CREATE TABLE rooms
                       (
                           id   INT PRIMARY KEY,
                           name TEXT NOT NULL
                       );

                       CREATE TABLE students
                       (
                           id       INT PRIMARY KEY,
                           name     TEXT      NOT NULL,
                           birthday TIMESTAMP NOT NULL,
                           sex      CHAR(1)   NOT NULL,
                           room_id  INT REFERENCES rooms (id) ON DELETE CASCADE
                       );

                       -- Query Optimization: B-Tree Indexes
                       CREATE INDEX idx_students_room_id ON students (room_id);
                       CREATE INDEX idx_students_sex ON students (sex);
                       CREATE INDEX idx_students_birthday ON students (birthday);
                       """)


### Data Loader: Parsing and loading JSON data into the database/postgresql
class DataLoader:
    

    def __init__(self, db):
        self.db = db

    def load_rooms(self, path):
        with open(path, "r", encoding="utf-8") as f:
            rooms = json.load(f)
        data = [(r["id"], r["name"]) for r in rooms]
        with self.db.get_cursor() as cursor:
            execute_batch(cursor,
                          "INSERT INTO rooms (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
                          data)

    def load_students(self, path):
        with open(path, "r", encoding="utf-8") as f:
            students = json.load(f)
        data = [
            (s["id"], s["name"], datetime.fromisoformat(s["birthday"]), s["sex"], s["room"])
            for s in students
        ]
        with self.db.get_cursor() as cursor:
            execute_batch(cursor,
                          "INSERT INTO students (id, name, birthday, sex, room_id) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                          data)


### Query Service: analytical queries
class QueryService:

    def __init__(self, db):
        self.db = db

    def _execute(self, query):
        with self.db.get_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def get_all_results(self):
        return {
            "rooms_with_student_count": self._execute("""
                                                      SELECT r.name, COUNT(s.id)
                                                      FROM rooms r
                                                               LEFT JOIN students s ON r.id = s.room_id
                                                      GROUP BY r.id, r.name"""),

            "top_5_rooms_smallest_avg_age": self._execute("""
                                                          SELECT r.name, AVG(EXTRACT(YEAR FROM AGE(s.birthday))) as avg_age
                                                          FROM rooms r
                                                                   JOIN students s ON r.id = s.room_id
                                                          GROUP BY r.id, r.name
                                                          ORDER BY avg_age ASC LIMIT 5"""),

            "top_5_rooms_largest_age_difference": self._execute("""
                                                                SELECT r.name,
                                                                       MAX(EXTRACT(YEAR FROM AGE(s.birthday))) -
                                                                       MIN(EXTRACT(YEAR FROM AGE(s.birthday))) as diff
                                                                FROM rooms r
                                                                         JOIN students s ON r.id = s.room_id
                                                                GROUP BY r.id, r.name
                                                                ORDER BY diff DESC LIMIT 5"""),

            "mixed_sex_rooms": self._execute("""
                                             SELECT r.name
                                             FROM rooms r
                                                      JOIN students s ON r.id = s.room_id
                                             GROUP BY r.id, r.name
                                             HAVING COUNT(DISTINCT s.sex) > 1""")
        }


### Data Exporter: Exports query results into JSON 
class Exporter:

    @staticmethod
    def _serialize(val):
        if isinstance(val, (decimal.Decimal, datetime)):
            return str(val)
        return val

    @staticmethod
    def to_json(data, path="output.json"):
        clean_data = {k: [[Exporter._serialize(c) for c in row] for row in v] for k, v in data.items()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=4)

    @staticmethod
    def to_xml(data, path="output.xml"):
        root = ET.Element("results")
        for key, rows in data.items():
            section = ET.SubElement(root, key)
            for row in rows:
                item = ET.SubElement(section, "item")
                for i, val in enumerate(row):
                    ET.SubElement(item, f"column_{i}").text = str(val)
        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)


### Main Logic
def main():
    parser = argparse.ArgumentParser(description="University Data ETL Tool")
    parser.add_argument("--students", required=True, help="Path to students.json")
    parser.add_argument("--rooms", required=True, help="Path to rooms.json")
    parser.add_argument("--format", choices=["json", "xml"], default="json", help="Output format")
    parser.add_argument("--dbname", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5432)

    args = parser.parse_args()
    db = Database(args.dbname, args.user, args.password, args.host, args.port)

    try:
        print("Starting Schema Initialization...")
        create_schema(db)

        loader = DataLoader(db)
        print("Loading Data into Database...")
        loader.load_rooms(args.rooms)
        loader.load_students(args.students)

        print("Executing Analytics...")
        service = QueryService(db)
        results = service.get_all_results()

        print(f"Exporting results to {args.format}...")
        if args.format == "json":
            Exporter.to_json(results)
        else:
            Exporter.to_xml(results)

        print("Process completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
