import os

import psycopg2
import psycopg2.extras


class DBClient:

    def __init__(self):
        self.__conn_string = f"host={os.getenv('DB_HOST')} dbname={os.getenv('DB_DATABASE')} " \
                             f"user={os.getenv('DB_USER')} password={os.getenv('DB_PASSWORD')}"

    def __get_conn(self):
        return psycopg2.connect(self.__conn_string)

    def __run_select_query(self, query: str):
        with self.__get_conn() as conn:
            cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            cursor.execute(query)
            return cursor.fetchall()

    def __run_batch_insert_query(self, query: str, data: list):
        with self.__get_conn() as conn:
            cursor = conn.cursor()
            psycopg2.extras.execute_batch(cursor, query, data)
            conn.commit()

    def list_guilds(self):
        query = "SELECT * FROM guilds"
        response = self.__run_select_query(query)
        return [guild_row for guild_row in response]

    def list_encounters(self):
        query = "SELECT * FROM encounters"
        response = self.__run_select_query(query)
        return [encounter_row for encounter_row in response]

    def list_specs(self):
        query = "SELECT * FROM specs"
        response = self.__run_select_query(query)
        return [spec_row for spec_row in response]

    def list_characters(self):
        query = "SELECT * FROM characters"
        response = self.__run_select_query(query)
        return [char_row for char_row in response]

    def list_report_ids(self):
        query = "SELECT id FROM reports"
        response = self.__run_select_query(query)
        return [report_row["id"] for report_row in response]

    def list_parse_ids(self):
        query = "SELECT id FROM parses"
        response = self.__run_select_query(query)
        return [parse_row["id"] for parse_row in response]

    def insert_reports(self, reports):
        query = """
        INSERT INTO reports(id, guild, title, "date", realm, region, faction)
        VALUES (%(id)s, %(guild)s, %(title)s, %(date)s, %(realm)s, %(region)s, %(faction)s)
        """
        self.__run_batch_insert_query(query, reports)

    def insert_parses(self, parses):
        query = """
        INSERT INTO parses(id, character_id, name, "class", spec, guild, realm, region, faction, zone, zone_id,
                           encounter, encounter_id, duration, percentile, metric, value, ilvl, "date")
        VALUES (%(id)s, %(character_id)s, %(name)s, %(class)s, %(spec)s, %(guild)s, %(realm)s, %(region)s,
                %(faction)s, %(zone)s, %(zone_id)s, %(encounter)s, %(encounter_id)s, %(duration)s, %(percentile)s,
                %(metric)s, %(value)s, %(ilvl)s, %(date)s)
        """
        self.__run_batch_insert_query(query, parses)

    def insert_characters(self, characters):
        query = """
        INSERT INTO characters(id, name, guild, realm, region, faction, "class", is_blacklisted)
        VALUES (%(id)s, %(name)s, %(guild)s, %(realm)s, %(region)s, %(faction)s, %(class)s, %(is_blacklisted)s)
        """
        self.__run_batch_insert_query(query, characters)
