import os

import requests

WCL_API_KEY = os.getenv("WCL_API_KEY")

class WCLApiClient:

    __API_BASE_URL = "https://classic.warcraftlogs.com/v1"

    def __request_api(self, endpoint: str, params: dict = None):
        if not params:
            params = dict()
        params["api_key"] = WCL_API_KEY
        res = requests.get(f"{self.__API_BASE_URL}/{endpoint}", params=params)
        if res.status_code > 299:
            raise Exception(f"Something happened: {res.content}")
        return res.json()


    def get_character_rankings(self, character, realm, region, params=None):
        endpoint = f"rankings/character/{character}/{realm}/{region}"
        return self.__request_api(endpoint, params=params)


    def get_guild_reports(self, name, realm, region, params=None):
        endpoint = f"reports/guild/{name}/{realm}/{region}"
        return self.__request_api(endpoint, params)


    def get_report_info(self, code, params=None):
        endpoint = f"report/fights/{code}"
        return self.__request_api(endpoint, params)
