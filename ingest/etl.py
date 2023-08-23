import csv
import json
import os
from datetime import datetime, timedelta
from time import sleep

from api import WCLApiClient
from cfg import Config
from db import PGClient
from log import get_logger


class ETL:

    def __init__(
        self, cfg: Config, api_client: WCLApiClient, db_client: PGClient, historical_run: bool,
        sleep_time: int = 300, sleep_delta: int = 100
    ):
        self.__cfg = cfg
        self.__api_client = api_client
        self.__db_client = db_client
        self.__historical_run = historical_run
        self.__sleep_time = sleep_time
        self.__sleep_delta = sleep_delta

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
            get_logger().error(f"Something when fetching rankings for: {character['name']}")
            get_logger().error(f"Error: {str(e)}")

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

            get_logger().debug(f"Fetched report {report_id} for guild {guild['name']}")
            self.__reports[guild["name"]][report_id] = report
            return report
        except Exception as e:
            get_logger().error(f"Something happened when fetching report {report_id}")
            get_logger().error(f"Error: {str(e)}")
            return None

    def __fetch_reports_by_guild(self, guild_name: str, guild: dict):
        DELTA = 14 if self.__historical_run else 5
        get_logger().info(f"Fetching reports for: {guild['name']}. Delta: {DELTA} days")
        start_date = (datetime.now() - timedelta(days=DELTA)).timestamp() * 1000
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
                try:
                    self.__fetch_reports_by_guild(guild_name, guild)
                    get_logger().info(f"{len(self.__reports[guild_name])} new reports for {guild['name']} !")
                except Exception as e:
                    get_logger().error(f"Could not fetch reports for guild {guild_name}")
                    get_logger().error(f"Error: {str(e)}")

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
        for index, character in enumerate(self.__characters.values()):
            character_parses =  self.__fetch_character_parses(character)
            if character_parses:
                self.__parses.extend(character_parses)
            if (index + 1) % self.__sleep_delta == 0:
                get_logger().info(f"Fetched {index + 1} character parses. Waiting {int(self.__sleep_time / 60)} minutes...")
                sleep(self.__sleep_time)

    def __prepare_data(self):
        get_logger().info("Preparing reports...")
        self.__reports_to_save = list()
        for _, reports in self.__reports.items():
            for report_id, report in reports.items():
                if report_id not in self.__cfg.processed_reports or \
                   not self.__cfg.processed_reports[report_id]["fights"]:
                    report["fights"] = json.dumps(report["fights"])
                    self.__reports_to_save.append(report)

        get_logger().info("Preparing characters...")
        self.__characters_to_save = list()
        for character_id, character in self.__characters.items():
            if character_id not in self.__cfg.known_characters:
                self.__characters_to_save.append(character)


    def __backup_data(self):
        backup_path = os.getenv("BACKUP_PATH", "/opt/backup")
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        get_logger().info("Backuping data...")
        if self.__parses:
            get_logger().info("Backuping parses...")
            with open(f"{backup_path}/{timestamp}_parses.csv", "w") as fout:
                field_names = list(self.__parses[0].keys())
                writer = csv.DictWriter(fout, fieldnames=field_names)
                writer.writerows(self.__parses)
        if self.__reports_to_save:
            get_logger().info("Backuping reports...")
            with open(f"{backup_path}/{timestamp}_reports.csv", "w") as fout:
                field_names = list(self.__reports_to_save[0].keys())
                writer = csv.DictWriter(fout, fieldnames=field_names)
                writer.writerows(self.__reports_to_save)
        if self.__characters_to_save:
            get_logger().info("Backuping characters...")
            with open(f"{backup_path}/{timestamp}_characters.csv", "w") as fout:
                field_names = list(self.__characters_to_save[0].keys())
                writer = csv.DictWriter(fout, fieldnames=field_names)
                writer.writerows(self.__characters_to_save)


    def __save_reports(self):
        get_logger().info(f"Saving {len(self.__reports_to_save)} reports")
        self.__db_client.upsert_reports(self.__reports_to_save)

    def __save_parses(self):
        get_logger().info(f"Saving {len(self.__parses)} parses...")
        self.__db_client.upsert_parses(self.__parses)

    def __save_characters(self):
        get_logger().info(f"Saving {len(self.__characters_to_save)} characters...")
        self.__db_client.insert_characters(self.__characters_to_save)

    def extract_and_transform(self):
        get_logger().info("Extracting and transforming data...")
        self.__load_reports()
        self.__load_characters()
        self.__load_parses()
        return self

    def load(self):
        get_logger().info("Loading data...")
        self.__prepare_data()
        self.__backup_data()
        self.__save_reports()
        self.__save_parses()
        self.__save_characters()
        return self
