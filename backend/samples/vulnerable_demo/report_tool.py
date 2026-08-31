"""
DEMO SCENARIO — deliberately vulnerable sample module.

This file exists ONLY to demonstrate the SENTINEL-AI pipeline. It is
never executed by the platform — it is analyzed statically, exactly
like an uploaded project would be.
"""

import os
import pickle
import subprocess


def convert_report_to_pdf(filename: str) -> None:
    # Vulnerable: shell interpolation of a filename that may originate
    # from a user-supplied report name.
    os.system("libreoffice --convert-to pdf " + filename)


def run_export_job(export_cmd: str) -> None:
    subprocess.call(export_cmd, shell=True)


def load_cached_report(path: str):
    with open(path, "rb") as fh:
        # Vulnerable: deserializing a cached report blob with pickle.
        return pickle.load(fh)
