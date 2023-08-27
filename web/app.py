import json
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template
from flask_frozen import Freezer

from db import PGClient
from config import CLASS_ICON_MAP, PARSE_COLOR_MAP, FIGHT_ID_MAP, CLASS_ID_MAP
from log import get_logger


app = Flask(__name__)
app.config['FREEZER_DESTINATION'] = '../docs'
freezer = Freezer(app, with_no_argument_rules=False)
db = PGClient()

def fetch_top_dps():
    get_logger().info("Fetching top DPS rankings...")
    top_dps = {
        f["code"]: {"label": f["label"], "rows": list()}
        for f in FIGHT_ID_MAP.values()
    }
    for encounter_id, fight_conf in FIGHT_ID_MAP.items():
        get_logger().info(f"Fetching top DPS rankings for fight: {encounter_id}")
        encounter_code = fight_conf["code"]
        top_dps_for_encounter = db.list_top_dps_by_encounter(encounter_id)
        top_dps_for_encounter = sorted(top_dps_for_encounter, key=lambda d: d['dps'], reverse=True)
        characters_computed = set()
        for dps_row in top_dps_for_encounter:
            if dps_row["character_id"] in characters_computed:
                continue

            dps_row["dps"] = float(dps_row["dps"])
            dps_row["class_spec"] = f"{dps_row['class']} - {dps_row['spec']}"
            dps_row["server_region"] = f"{dps_row['realm'].capitalize()}-{dps_row['region'].upper()}"
            dps_row["class_icon"] = CLASS_ICON_MAP[dps_row["class_spec"]]
            m, s = divmod(int(dps_row["duration"]), 60)
            dps_row["duration_formated"] = "{:02d}:{:02d}".format(m, s)
            top_dps[encounter_code]["rows"].append(dps_row)
            characters_computed.add(dps_row["character_id"])

            if len(characters_computed) == 20:
                break

    return top_dps

def fetch_top_parses():
    get_logger().info("Fetching top parses...")
    top_parses = {
        c["code"]: {"label": c["label"], "rows": list()}
        for c in CLASS_ID_MAP.values()
    }

    all = list()
    for class_name, class_conf in CLASS_ID_MAP.items():
        if class_name == "All":
            continue

        get_logger().info(f"Fetching top parses for class: {class_name}")
        top_parse_for_class = db.list_top_parses_by_class(class_name)
        top_parse_for_class = sorted(top_parse_for_class, key=lambda d: d['avg_parse'], reverse=True)
        characters_computed = set()
        for parse_row in top_parse_for_class:
            if parse_row["character_id"] in characters_computed:
                continue

            parse_row["avg_parse"] = float(parse_row["avg_parse"])
            parse_row["class_spec"] = f"{parse_row['class']} - {parse_row['spec']}"
            parse_row["server_region"] = f"{parse_row['realm'].capitalize()}-{parse_row['region'].upper()}"
            parse_row["class_icon"] = CLASS_ICON_MAP[parse_row["class_spec"]]
            top_parses[class_conf["code"]]["rows"].append(parse_row)
            for rule, color in PARSE_COLOR_MAP.items():
                if parse_row["avg_parse"] >= rule:
                    parse_row["parse_color"] = color
                    break
            all.append(parse_row)
            characters_computed.add(parse_row["character_id"])

            if len(characters_computed) == 20:
                break

    all = sorted(all, key=lambda d: d['avg_parse'], reverse=True)
    characters_computed = set()
    for parse_row in all:
        if parse_row["character_id"] in characters_computed:
            continue

        parse_row["avg_parse"] = float(parse_row["avg_parse"])
        parse_row["class_spec"] = f"{parse_row['class']} - {parse_row['spec']}"
        parse_row["server_region"] = f"{parse_row['realm'].capitalize()}-{parse_row['region'].upper()}"
        parse_row["class_icon"] = CLASS_ICON_MAP[parse_row["class_spec"]]
        for rule, color in PARSE_COLOR_MAP.items():
            if parse_row["avg_parse"] >= rule:
                parse_row["parse_color"] = color
                break
        top_parses["allc"]["rows"].append(parse_row)
        characters_computed.add(parse_row["character_id"])

        if len(characters_computed) == 20:
            break

    return top_parses


def fetch_fake_top_dps():
    with open(Path(__file__).parent / "sample_data/top_dps.json") as f:
        data = json.load(f)
    return data

def fetch_fake_top_parses():
    with open(Path(__file__).parent / "sample_data/top_parse.json") as f:
        data = json.load(f)
    return data

@freezer.register_generator
def index():
    yield {}

@app.route('/')
def index():
    if len(sys.argv) > 2 and sys.argv[2] == 'fake':
        top_dps = fetch_fake_top_dps()
        top_parses = fetch_fake_top_parses()
    else:
        db = PGClient()
        top_dps = fetch_top_dps()
        top_parses = fetch_top_parses()
    get_logger().info("Rendering website...")
    return render_template(
        'index.html',
        last_update=datetime.now().strftime("%d/%m/%Y %H:%M"),
        fights=list(top_dps.keys()),
        top_dps=top_dps,
        classes=list(top_parses.keys()),
        top_parses=top_parses
    )

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        freezer.freeze()
    else:
        app.run(debug=True)
