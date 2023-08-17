import sys
from collections import defaultdict
from csv import DictReader
from pathlib import Path

from flask import Flask, render_template
from flask_frozen import Freezer

from config import CLASS_ICON_MAP, PARSE_COLOR_MAP, FIGHT_ID_MAP, CLASS_ID_MAP


app = Flask(__name__)
app.config['FREEZER_DESTINATION'] = '../docs'
freezer = Freezer(app, with_no_argument_rules=False)


def fetch_top_dps():
    top_dps = {
        f["code"]: {"label": f["label"], "rows": list()}
        for f in FIGHT_ID_MAP.values()
    }
    with open(Path(__file__).parent / "sample_data/dps.csv") as f:
        csv_data = DictReader(f)
        for row in csv_data:
            row["dps"] = float(row["dps"])
            row["class_icon"] = CLASS_ICON_MAP[row["class_spec"]]
            top_dps[FIGHT_ID_MAP[row["fight"]]["code"]]["rows"].append(row)

    for fight in top_dps:
        all_dps = top_dps[fight]["rows"]
        top_20 = sorted(all_dps, key=lambda d: d['dps'], reverse=True)[:20]
        top_dps[fight]["rows"] = top_20

    return top_dps

def fetch_top_parses():
    top_parses = {
        c["code"]: {"label": c["label"], "rows": list()}
        for c in CLASS_ID_MAP.values()
    }
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
            top_parses[CLASS_ID_MAP[cls]["code"]]["rows"].append(row)
            top_parses[CLASS_ID_MAP["All"]["code"]]["rows"].append(row)

    for cls in top_parses:
        all_parses = top_parses[cls]["rows"]
        top_20 = sorted(all_parses, key=lambda d: d['avg_parse'], reverse=True)[:20]
        top_parses[cls]["rows"] = top_20

    return top_parses

@freezer.register_generator
def index():
    yield {}

@app.route('/')
def index():
    top_dps = fetch_top_dps()
    top_parses = fetch_top_parses()
    return render_template(
        'index.html',
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
