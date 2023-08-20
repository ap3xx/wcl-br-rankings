import os

import psycopg2
import psycopg2.extras


class PGClient:

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

    def list_encounters(self):
        query = "SELECT * FROM cfg_encounters"
        response = self.__run_select_query(query)
        return [encounter_row for encounter_row in response]

    def list_specs(self):
        query = "SELECT * FROM cfg_specs"
        response = self.__run_select_query(query)
        return [spec_row for spec_row in response]

    def list_guilds(self, guild_name):
        query = "SELECT * FROM cfg_guilds"
        if guild_name:
            query += f" WHERE name = '{guild_name}'"
        response = self.__run_select_query(query)
        return [guild_row for guild_row in response]

    def list_characters(self, guild_name):
        query = "SELECT * FROM data_characters"
        if guild_name:
            query += f" WHERE guild = '{guild_name}'"
        response = self.__run_select_query(query)
        return [char_row for char_row in response]

    def list_reports(self, guild_name):
        query = "SELECT * FROM data_reports"
        if guild_name:
            query += f" WHERE guild = '{guild_name}'"
        response = self.__run_select_query(query)
        return [report_row for report_row in response]

    def list_processed_parses(self, guild_name):
        query = "SELECT encounter_id, character_id, spec, percentile FROM data_parses"
        if guild_name:
            query += f" WHERE guild = '{guild_name}'"
        response = self.__run_select_query(query)
        return [parse_row for parse_row in response]

    def upsert_reports(self, reports):
        query = """
        INSERT INTO data_reports(id, guild, title, "date", realm, region, faction, fights)
        VALUES (%(id)s, %(guild)s, %(title)s, %(date)s, %(realm)s, %(region)s, %(faction)s, %(fights)s)
        ON CONFLICT (id)
        DO UPDATE
        SET fights = EXCLUDED.fights
        """
        self.__run_batch_insert_query(query, reports)

    def upsert_parses(self, parses):
        query = """
        INSERT INTO data_parses(
            character_id, name, "class", spec, guild, realm, region, faction, zone, zone_id,
            encounter, encounter_id, duration, percentile, dps, ilvl, "date")
        VALUES (%(character_id)s, %(name)s, %(class)s, %(spec)s, %(guild)s, %(realm)s, %(region)s,
                %(faction)s, %(zone)s, %(zone_id)s, %(encounter)s, %(encounter_id)s, %(duration)s, %(percentile)s,
                %(dps)s, %(ilvl)s, %(date)s)
        ON CONFLICT (character_id, encounter_id, spec)
        DO UPDATE
        SET duration = EXCLUDED.duration, percentile = EXCLUDED.percentile, dps = EXCLUDED.dps,
            ilvl = EXCLUDED.ilvl, "date" = EXCLUDED."date"
        """
        self.__run_batch_insert_query(query, parses)

    def insert_characters(self, characters):
        query = """
        INSERT INTO data_characters(id, name, guild, realm, region, faction, "class", is_blacklisted)
        VALUES (%(id)s, %(name)s, %(guild)s, %(realm)s, %(region)s, %(faction)s, %(class)s, %(is_blacklisted)s)
        """
        self.__run_batch_insert_query(query, characters)
