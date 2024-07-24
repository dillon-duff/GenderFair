import sqlite3
import os
from typing import Union
from config import Config
import pandas as pd

class IRS990Extractor:
    def __init__(self):
        self.db_path = 'irs990_index.db'
        self.initialize_database()

    def initialize_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS irs990_index (
                ein INTEGER,
                year INTEGER,
                object_id TEXT,
                file_path TEXT,
                PRIMARY KEY (ein, year)
            )
        ''')
        conn.commit()
        conn.close()

    def populate_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for year in range(Config.START_YEAR, Config.END_YEAR + 1):
            index_file = f"{Config.INDEX_FOLDER}/index_{year}.csv"
            if os.path.exists(index_file):
                df = pd.read_csv(index_file)
                for _, row in df.iterrows():
                    ein = int(str(row['EIN']).replace("-", ""))
                    object_id = row['OBJECT_ID']
                    year_folder = f"{Config.ARCHIVE_FOLDER}/{year}"
                    for subdir in os.listdir(year_folder):
                        subdir_path = os.path.join(year_folder, subdir)
                        if os.path.isdir(subdir_path):
                            xml_filename = f"{object_id}_public.xml"
                            xml_file_path = os.path.join(subdir_path, xml_filename)
                            if os.path.exists(xml_file_path):
                                cursor.execute('''
                                    INSERT OR REPLACE INTO irs990_index (ein, year, object_id, file_path)
                                    VALUES (?, ?, ?, ?)
                                ''', (ein, year, object_id, xml_file_path))
                                break
        
        conn.commit()
        conn.close()

    def find_and_extract_990(self, ein: str) -> Union[str, int]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        ein = int(str(ein).replace("-", ""))
        cursor.execute('''
            SELECT file_path FROM irs990_index
            WHERE ein = ?
            ORDER BY year DESC
            LIMIT 1
        ''', (ein,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            file_path = result[0]
            with open(file_path, 'r') as file:
                return file.read()
        return -1
