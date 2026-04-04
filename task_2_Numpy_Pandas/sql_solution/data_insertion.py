import psycopg2
from psycopg2.extras import execute_values
import csv


class BOMDatabaseHandler:
    def __init__(self, dbname, user, password, host="localhost", port=5432):
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            print("Database connection established.")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            self.conn = None

    def insert_csv_data(self, file_path):
        if not self.conn:
            return

        query = """
                INSERT INTO bom_data (year, month, produced_material, produced_material_production_type, \
                                      produced_material_release_type, produced_material_quantity, \
                                      component_material, component_material_production_type, \
                                      component_material_release_type, component_material_quantity, plant_id) \
                VALUES %s \
                """

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)

                data_to_insert = []
                for row in reader:
                    
                    processed_row = [
                        int(row[0]),
                        int(row[1]),
                        row[2],
                        row[3] if row[3] else None,  
                        row[4],
                        float(row[5].replace(',', '')),
                        row[6],
                        row[7] if row[7] else None,
                        row[8],
                        float(row[9].replace(',', '')),
                        row[10]
                    ]
                    data_to_insert.append(processed_row)

            with self.conn.cursor() as cur:
                execute_values(cur, query, data_to_insert)
                self.conn.commit()
                print(f"Successfully inserted {len(data_to_insert)} rows.")

        except Exception as e:
            self.conn.rollback()
            print(f"Error during insertion: {e}")

    def close(self):
        if self.conn:
            self.conn.close()


file_loc = "/mnt/c/Users/sergi/OneDrive/Desktop/innowise_workspace/task_2_Numpy_Pandas/pandas_BOM(Bill_of_Materials)/task_2_data.csv"

db = BOMDatabaseHandler(
    dbname="postgres",
    user="postgres",
    password="xxxxxx"
)

db.insert_csv_data(file_loc)
db.close()
