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

    def list_top_dps_by_encounter(self, encounter_id):
        query = f"""
        SELECT
            "character_id", "name", guild, realm, region, faction, "class", spec, encounter_id, dps, duration
        FROM data_parses
        WHERE encounter_id = {encounter_id}
        """
        response = self.__run_select_query(query)
        return [parse_row for parse_row in response]

    def list_top_parses_by_class(self, player_class):
        query = f"""
        SELECT
            character_id, "name", guild, realm, region, faction, "class", spec, SUM(percentile)/4 AS avg_parse
        FROM data_parses
        WHERE "class" = '{player_class}'
        GROUP BY
            character_id, "name", guild, realm, region, faction, "class", spec
        """
        response = self.__run_select_query(query)
        return [parse_row for parse_row in response]
