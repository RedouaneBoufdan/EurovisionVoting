from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
LOG_DIR = BASE_DIR / "logs"

SONGS_FILE = DATA_DIR / "songs.csv"
VOTES_STREAM_FILE = RESULTS_DIR / "votes_stream.csv"
VOTES_STORAGE_FILE = RESULTS_DIR / "votes_storage.csv"
DATACENTER_RESULTS_FILE = RESULTS_DIR / "datacenter_results.csv"
GLOBAL_RESULTS_FILE = RESULTS_DIR / "global_results.csv"
WINNER_FILE = RESULTS_DIR / "winner.txt"
PIPELINE_METRICS_FILE = RESULTS_DIR / "pipeline_metrics.json"
PROVISIONING_PLAN_FILE = RESULTS_DIR / "provisioning_plan.json"
DEPLOYMENT_MANIFEST_FILE = RESULTS_DIR / "deployment_manifest.json"
SHUTDOWN_REPORT_FILE = RESULTS_DIR / "shutdown_report.json"

COUNTRY_CODES = {
    "Sweden": "SE", "France": "FR", "Italy": "IT", "Spain": "ES", "Germany": "DE",
    "Belgium": "BE", "Netherlands": "NL", "Norway": "NO", "Denmark": "DK", "Finland": "FI",
    "Portugal": "PT", "Greece": "GR", "Poland": "PL", "Ukraine": "UA", "United Kingdom": "GB",
    "Switzerland": "CH", "Austria": "AT", "Ireland": "IE", "Czechia": "CZ", "Estonia": "EE",
}

CODE_TO_COUNTRY = {code: country for country, code in COUNTRY_CODES.items()}

DIAL_PREFIX = {
    "SE": "+46", "FR": "+33", "IT": "+39", "ES": "+34", "DE": "+49", "BE": "+32",
    "NL": "+31", "NO": "+47", "DK": "+45", "FI": "+358", "PT": "+351", "GR": "+30",
    "PL": "+48", "UA": "+380", "GB": "+44", "CH": "+41", "AT": "+43", "IE": "+353",
    "CZ": "+420", "EE": "+372",
}

# Simulated datacenters. In a real project these would be VM hostnames/IP addresses.
DATACENTERS = {
    "dc-west": {"provider": "Proxmox", "region": "Belgium", "countries": ["BE", "FR", "NL", "GB", "IE"]},
    "dc-north": {"provider": "Proxmox", "region": "Nordics", "countries": ["SE", "NO", "DK", "FI", "EE"]},
    "dc-central": {"provider": "AWS", "region": "eu-central-1", "countries": ["DE", "AT", "CH", "PL", "CZ"]},
    "dc-south": {"provider": "AWS", "region": "eu-west-3", "countries": ["IT", "ES", "PT", "GR", "UA"]},
}

FRIEND_BIAS = {
    "BE": ["FR", "NL"], "FR": ["BE", "CH"], "NL": ["BE", "DE"],
    "DE": ["AT", "CH", "NL", "PL"], "AT": ["DE", "CH"], "CH": ["FR", "DE", "AT"],
    "SE": ["NO", "DK", "FI"], "NO": ["SE", "DK"], "DK": ["SE", "NO"], "FI": ["SE", "EE"],
    "ES": ["PT", "FR"], "PT": ["ES"], "IE": ["GB"], "GB": ["IE"],
    "PL": ["UA", "CZ", "DE"], "UA": ["PL"], "CZ": ["PL", "DE"], "EE": ["FI"],
}

def ensure_directories() -> None:
    for folder in (DATA_DIR, RESULTS_DIR, LOG_DIR):
        folder.mkdir(exist_ok=True)

def get_datacenter_for_country(country_code: str) -> str:
    for name, info in DATACENTERS.items():
        if country_code in info["countries"]:
            return name
    return "dc-central"
