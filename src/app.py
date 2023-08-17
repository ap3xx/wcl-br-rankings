import sys
from collections import defaultdict
from csv import DictReader
from pathlib import Path

from flask import Flask, render_template
from flask_frozen import Freezer

from config import CLASS_ICON_MAP, PARSE_COLOR_MAP


app = Flask(__name__)
app.config['FREEZER_DESTINATION'] = '../docs'
freezer = Freezer(app, with_no_argument_rules=False)


def fetch_dps_player_data():
    fights_dps = defaultdict(list)
    with open(Path(__file__).parent / "sample_data/dps.csv") as f:
        csv_data = DictReader(f)
        for row in csv_data:
            row["dps"] = float(row["dps"])
            row["class_icon"] = CLASS_ICON_MAP[row["class_spec"]]
            fights_dps[row["fight"]].append(row)

    for fight in fights_dps:
        all_dps = fights_dps[fight]
        top_20 = sorted(all_dps, key=lambda d: d['dps'], reverse=True)[:20]
        fights_dps[fight] = top_20

    return fights_dps

def fetch_parse_player_data():
    class_parses = defaultdict(list)
    with open(Path(__file__).parent / "sample_data/parse.csv") as f:
        csv_data = DictReader(f)
        for row in csv_data:
            cls = row["class_spec"].split(" - ")[0]
            row["avg_parse"] = float(row["avg_parse"])
            row["class_icon"] = CLASS_ICON_MAP[row["class_spec"]]
            row["parse_color"] = "grey"
            for rule, color in PARSE_COLOR_MAP.items():
                if row["avg_parse"] >= rule:
                    row["parse_color"] = color
                    break
            class_parses[cls].append(row)
            class_parses["All"].append(row)

    for cls in class_parses:
        all_parses = class_parses[cls]
        top_20 = sorted(all_parses, key=lambda d: d['avg_parse'], reverse=True)[:20]
        class_parses[cls] = top_20

    return class_parses

@freezer.register_generator
def index():
    yield {}

@app.route('/')
def index():
    bosses_dps = fetch_dps_player_data()
    class_parses = fetch_parse_player_data()
    return render_template(
        'index.html',
        top_20_bofn=bosses_dps["629"],
        top_20_lord=bosses_dps["633"],
        top_20_twin=bosses_dps["641"],
        top_20_anub=bosses_dps["645"],
        top_20_allc=class_parses["All"],
        top_20_dkni=class_parses["Death Knight"],
        top_20_dudu=class_parses["Druid"],
        top_20_hunt=class_parses["Hunter"],
        top_20_mage=class_parses["Mage"],
        top_20_pala=class_parses["Paladin"],
        top_20_prst=class_parses["Priest"],
        top_20_roge=class_parses["Rogue"],
        top_20_sham=class_parses["Shaman"],
        top_20_lock=class_parses["Warlock"],
        top_20_warr=class_parses["Warrior"]
    )

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        freezer.freeze()
    else:
        app.run(debug=True)
