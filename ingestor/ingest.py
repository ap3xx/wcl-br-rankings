import json
from datetime import datetime, timedelta

from api import WCLApiClient
from cfg import IngestionConfig
from db import PGClient
from log import get_logger


class WCLBrazilIngestor:

    def __init__(self, cfg: IngestionConfig, api_client: WCLApiClient, db: PGClient):
        self.__cfg = cfg
        self.__api_client = api_client
        self.__db = db

    def __fetch_character_parses(self, character: dict):
        get_logger().debug(
            f"Fetching rankings for {character['name']} {character['realm']}-{character['region']}")
        character_rankings = list()
        try:
            for zone_id, zone in self.__cfg.zones.items():
                rankings = self.__api_client.get_character_rankings(
                    character["name"], character["realm"],  character["region"],
                    params={"metric": "dps", "zone": zone_id}
                )
                for ranking in rankings:
                    current_existing_parse = self.__cfg.processed_parses.get(ranking["encounterID"], dict()) \
                                                  .get(character["id"], dict()) \
                                                  .get(ranking["spec"], 999999999)

                    if round(current_existing_parse, 2) == round(ranking["percentile"], 2):
                        get_logger().debug("Character ranking already processed and did not change since last run...")
                        continue

                    if ranking["size"] != 25:
                        get_logger().debug(f"Not considering raid size {ranking['size']}")
                        continue

                    encounter = self.__cfg.encounters.get(ranking["encounterID"])
                    if not encounter or encounter["zone_name"] != zone["name"]:
                        get_logger().debug(f"Encounter {ranking['encounterName']} is invalid for zone {zone['name']}")
                        continue

                    if encounter["difficulty"] != ranking["difficulty"]:
                        get_logger().debug(f"Not considering difficulty {ranking['difficulty']} "
                                           f"for encounter {ranking['encounterName']}")
                        continue

                    if ranking["spec"] not in self.__cfg.classes_and_specs[ranking["class"]]:
                        get_logger().debug(f"Not condidering spec {ranking['spec']} for class {ranking['class']}")
                        continue

                    report = self.__fetch_report(ranking["reportID"], self.__cfg.guilds[character["guild"]])
                    fight_id = str(ranking["fightID"])
                    if not report or fight_id not in report["fights"]:
                        get_logger().debug("Report or fight not in guilds reports list! Skipping ranking...")
                        continue

                    character_rankings.append({
                        "character_id": character["id"],
                        "name": character["name"],
                        "class": character["class"],
                        "spec": ranking["spec"],
                        "realm": character["realm"],
                        "region": character["region"],
                        "guild": character["guild"],
                        "guild_id": self.__cfg.guilds[character["guild"]]["id"],
                        "faction": character["faction"],
                        "zone": zone["name"],
                        "zone_id": zone_id,
                        "encounter": ranking["encounterName"],
                        "encounter_id": ranking["encounterID"],
                        "duration":
                            self.__reports[character["guild"]][ranking["reportID"]]["fights"][fight_id]["duration"],
                        "percentile": ranking["percentile"],
                        "dps": ranking["total"],
                        "ilvl": ranking["ilvlKeyOrPatch"],
                        "report_id": ranking["reportID"],
                        "report_fight_id": ranking["fightID"],
                        "date": report["date"],
                    })


        except Exception as e:
            get_logger().error(f"Something happened: {str(e)}")

        get_logger().info(f"Found {len(character_rankings)} parses for "
                          f"character {character['name']} {character['realm']}-{character['region']}")
        return character_rankings

    def __fetch_new_characters_by_guild(self, guild_name: str, guild: dict):
        get_logger().info(f"Fetching characters from API for guild: {guild_name}")
        guild_characters = dict()

        for _, report in self.__reports[guild_name].items():
            for __, character in report["characters"].items():
                if character["id"] in self.__cfg.known_characters:
                    continue
                new_char_obj = {
                    "id": character["id"],
                    "name": character["name"],
                    "guild": report["guild"],
                    "realm": report["realm"],
                    "region": report["region"],
                    "faction": report["faction"],
                    "class": character["class"],
                    "is_blacklisted": False
                }
                guild_characters[new_char_obj["id"]] = new_char_obj

        get_logger().info(f"Found {len(guild_characters)} new characters for guild {guild_name}")
        return guild_characters

    def __fetch_report(self, report_id: str, guild: dict):
        if report_id in self.__reports[guild["name"]]:
            return self.__reports[guild["name"]][report_id]

        if report_id in self.__cfg.processed_reports and \
           self.__cfg.processed_reports[report_id]["fights"]:
            report = self.__cfg.processed_reports[report_id]
            self.__reports[guild["name"]][report_id] = report
            return report

        try:
            report_info = self.__api_client.get_report_info(report_id)
            characters = {
                c["name"]: c
                for c in report_info["exportedCharacters"]
            }
            for friendly in report_info["friendlies"]:
                if friendly["name"] in characters:
                    characters[friendly["name"]]["class"] = friendly["type"]

            report = {
                "id": report_id,
                "title": report_info["title"],
                "date": datetime.fromtimestamp(report_info["start"] / 1000),
                "guild": guild["name"],
                "realm": guild["realm"],
                "region": guild["region"],
                "faction": guild["faction"],
                "characters": characters,
                "fights": dict(),
            }
            for fight in report_info["fights"]:
                if fight.get("kill", False) and fight.get("size") == 25:
                    report["fights"][str(fight["id"])] = {
                        "duration": (fight["end_time"] - fight["start_time"]) / 1000
                    }

            get_logger().info(f"Fetched report {report_id} for guild {guild['name']}")
            self.__reports[guild["name"]][report_id] = report
            return report
        except Exception as e:
            get_logger().error(f"Something happened when fetching reports: {str(e)}")
            return None

    def __fetch_reports_by_guild(self, guild_name: str, guild: dict):
        start_date = (datetime.now() - timedelta(days=5)).timestamp() * 1000
        late_guild_reports = self.__api_client.get_guild_reports(
            guild_name, guild["realm"], guild["region"], params={"start": start_date}
        )
        for report_entry in late_guild_reports:
            if report_entry["id"] not in self.__cfg.processed_reports:
                self.__fetch_report(report_entry["id"], guild)

    def __load_reports(self):
        get_logger().info("Loading reports...")
        self.__reports = dict()
        for guild_name, guild in self.__cfg.guilds.items():
            self.__reports[guild_name] = dict()
            if guild["fetch_enabled"]:
                self.__fetch_reports_by_guild(guild_name, guild)

    def __load_characters(self):
        get_logger().info("Loading characters...")
        self.__characters = dict()
        self.__characters.update(self.__cfg.known_characters)
        for guild_name, guild in self.__cfg.guilds.items():
            if guild["fetch_enabled"]:
                guild_new_characters = self.__fetch_new_characters_by_guild(guild_name, guild)
                self.__characters.update(guild_new_characters)

    def __load_parses(self):
        get_logger().info("Loading characters parses...")
        self.__parses = list()
        for _, character in self.__characters.items():
            character_parses = self.__fetch_character_parses(character)
            if character_parses:
                self.__parses.extend(character_parses)

    def __save_reports(self):
        get_logger().info("Preparing to save reports...")
        self.new_reports = list()
        for _, reports in self.__reports.items():
            for report_id, report in reports.items():
                if report_id not in self.__cfg.processed_reports or \
                   not self.__cfg.processed_reports[report_id]["fights"]:
                    report["fights"] = json.dumps(report["fights"])
                    self.new_reports.append(report)
        get_logger().info(f"Saving {len(self.new_reports)} reports")
        self.__db.upsert_reports(self.new_reports)

    def __save_parses(self):
        get_logger().info(f"Saving {len(self.__parses)} parses...")
        self.__db.upsert_parses(self.__parses)

    def __save_characters(self):
        get_logger().info("Preparing to save characters...")
        self.new_characters = list()
        for character_id, character in self.__characters.items():
            if character_id not in self.__cfg.known_characters:
                self.new_characters.append(character)
        get_logger().info(f"Saving {len(self.new_characters)} characters...")
        self.__db.insert_characters(self.new_characters)

    def extract_and_transform(self):
        get_logger().info("Extracting and transforming data...")
        self.__load_reports()
        self.__load_characters()
        self.__load_parses()
        return self

    def load(self):
        get_logger().info("Loading data...")
        self.__save_reports()
        self.__save_parses()
        self.__save_characters()
        return self
