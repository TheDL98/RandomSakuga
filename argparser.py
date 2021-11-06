import argparse
from pathlib import Path


description = "Python script that posts random sakuga to Facebook"
parser = argparse.ArgumentParser(prog="RandomSakuga", description=description)

parser.add_argument(
    "-c",
    "--config",
    type=Path,
    help="Path to configuration file",
    default="RS_settings.json",
)
args = parser.parse_args()
