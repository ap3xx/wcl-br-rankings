

import yaml

from db import PGClient
from log import get_logger

class IngestionConfig:

    def __init__(self):
        get_logger().info("Initializing configurations...")
        self.__db = PGClient()
        self.__load_encounters_conf()
        self.__load_specs_conf()
        self.__load_guilds_database()
        self.__load_characters_database()
        self.__load_processed_reports()
        self.__load_processed_parses()
        get_logger().info("Configurations loaded!")

    def __load_encounters_conf(self):
        get_logger().debug("Loading zones conf...")
        self.__encounters_conf = self.__db.list_encounters()
        self.zones = dict()
        self.encounters = dict()
        for e in self.__encounters_conf:
            if e["zone_id"] not in self.zones:
                self.zones[e["zone_id"]] = {"id": e["zone_id"], "name": e["zone_name"]}
            self.encounters[e["id"]] = e

    def __load_specs_conf(self):
        get_logger().debug("Loading classes conf...")
        self.__specs_conf = self.__db.list_specs()
        self.classes = dict()
        for s in self.__specs_conf:
            if s["class"] not in self.classes:
                self.classes[s["class"]] = dict(specs=dict(dps=list(), tank=list(), healer=list()))
            self.classes[s["class"]]["specs"][s["role"]].append(s["name"])

    def __load_guilds_database(self):
        get_logger().debug("Loading guilds conf...")
        self.__guilds_conf = self.__db.list_guilds()
        self.guilds = {
            g["name"]: g
            for g in self.__guilds_conf
        }

    def __load_characters_database(self):
        get_logger().debug("Loading characters database...")
        self.__characters_conf = self.__db.list_characters()
        self.known_characters = {
            c["id"]: c
            for c in self.__characters_conf
        }

    def __load_processed_reports(self):
        get_logger().debug("Loading already processed reports...")
        self.processed_reports_ids = self.__db.list_report_ids()

    def __load_processed_parses(self):
        get_logger().debug("Loading already processed parses...")
        self.processed_parses_ids = self.__db.list_parse_ids()

