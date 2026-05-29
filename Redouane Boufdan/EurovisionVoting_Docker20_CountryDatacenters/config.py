from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
LOG_DIR = BASE_DIR / "logs"
STATIC_DIR = BASE_DIR / "static"

SONGS_FILE = DATA_DIR / "songs.csv"
DISTRIBUTED_VOTES_FILE = RESULTS_DIR / "distributed_votes.csv"
DISTRIBUTED_STATUS_FILE = RESULTS_DIR / "distributed_status.json"
DISTRIBUTED_GLOBAL_FILE = RESULTS_DIR / "distributed_global_results.csv"
DISTRIBUTED_DATACENTER_FILE = RESULTS_DIR / "distributed_datacenter_results.csv"

COUNTRY_CODES = {
    "Sweden": "SE", "France": "FR", "Italy": "IT", "Spain": "ES", "Germany": "DE", "Belgium": "BE", "Netherlands": "NL", "Norway": "NO", "Denmark": "DK", "Finland": "FI", "Portugal": "PT", "Greece": "GR", "Poland": "PL", "Ukraine": "UA", "United Kingdom": "GB", "Switzerland": "CH", "Austria": "AT", "Ireland": "IE", "Czechia": "CZ", "Estonia": "EE"
}

CODE_TO_COUNTRY = {code: country for country, code in COUNTRY_CODES.items()}

DIAL_PREFIX = {
    "SE": "+46",     "FR": "+33",     "IT": "+39",     "ES": "+34",     "DE": "+49",     "BE": "+32",     "NL": "+31",     "NO": "+47",     "DK": "+45",     "FI": "+358",     "PT": "+351",     "GR": "+30",     "PL": "+48",     "UA": "+380",     "GB": "+44",     "CH": "+41",     "AT": "+43",     "IE": "+353",     "CZ": "+420",     "EE": "+372"
}

# Extended distributed version: 1 Docker datacenter service per Eurovision country/song.
# For the demo you can start only 3-5 selected datacenters, but the platform can operate all 20.
DATACENTERS = {
    "dc-sweden": {
        "display_name": "Sweden Datacenter",
        "country": "Sweden",
        "country_code": "SE",
        "provider": "Nordic Docker VM",
        "region": "Stockholm / Sweden",
        "container": "eurovision20-dc-sweden",
        "description": "Handles Sweden incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-france": {
        "display_name": "France Datacenter",
        "country": "France",
        "country_code": "FR",
        "provider": "Western Europe Docker VM",
        "region": "Paris / France",
        "container": "eurovision20-dc-france",
        "description": "Handles France incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-italy": {
        "display_name": "Italy Datacenter",
        "country": "Italy",
        "country_code": "IT",
        "provider": "Southern Europe Docker VM",
        "region": "Milan / Italy",
        "container": "eurovision20-dc-italy",
        "description": "Handles Italy incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-spain": {
        "display_name": "Spain Datacenter",
        "country": "Spain",
        "country_code": "ES",
        "provider": "Southern Europe Docker VM",
        "region": "Madrid / Spain",
        "container": "eurovision20-dc-spain",
        "description": "Handles Spain incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-germany": {
        "display_name": "Germany Datacenter",
        "country": "Germany",
        "country_code": "DE",
        "provider": "Central Europe Docker VM",
        "region": "Frankfurt / Germany",
        "container": "eurovision20-dc-germany",
        "description": "Handles Germany incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-belgium": {
        "display_name": "Belgium Datacenter",
        "country": "Belgium",
        "country_code": "BE",
        "provider": "Western Europe Docker VM",
        "region": "Brussels / Belgium",
        "container": "eurovision20-dc-belgium",
        "description": "Handles Belgium incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-netherlands": {
        "display_name": "Netherlands Datacenter",
        "country": "Netherlands",
        "country_code": "NL",
        "provider": "Western Europe Docker VM",
        "region": "Amsterdam / Netherlands",
        "container": "eurovision20-dc-netherlands",
        "description": "Handles Netherlands incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-norway": {
        "display_name": "Norway Datacenter",
        "country": "Norway",
        "country_code": "NO",
        "provider": "Nordic Docker VM",
        "region": "Oslo / Norway",
        "container": "eurovision20-dc-norway",
        "description": "Handles Norway incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-denmark": {
        "display_name": "Denmark Datacenter",
        "country": "Denmark",
        "country_code": "DK",
        "provider": "Nordic Docker VM",
        "region": "Copenhagen / Denmark",
        "container": "eurovision20-dc-denmark",
        "description": "Handles Denmark incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-finland": {
        "display_name": "Finland Datacenter",
        "country": "Finland",
        "country_code": "FI",
        "provider": "Nordic Docker VM",
        "region": "Helsinki / Finland",
        "container": "eurovision20-dc-finland",
        "description": "Handles Finland incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-portugal": {
        "display_name": "Portugal Datacenter",
        "country": "Portugal",
        "country_code": "PT",
        "provider": "Southern Europe Docker VM",
        "region": "Lisbon / Portugal",
        "container": "eurovision20-dc-portugal",
        "description": "Handles Portugal incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-greece": {
        "display_name": "Greece Datacenter",
        "country": "Greece",
        "country_code": "GR",
        "provider": "Southern Europe Docker VM",
        "region": "Athens / Greece",
        "container": "eurovision20-dc-greece",
        "description": "Handles Greece incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-poland": {
        "display_name": "Poland Datacenter",
        "country": "Poland",
        "country_code": "PL",
        "provider": "Central Europe Docker VM",
        "region": "Warsaw / Poland",
        "container": "eurovision20-dc-poland",
        "description": "Handles Poland incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-ukraine": {
        "display_name": "Ukraine Datacenter",
        "country": "Ukraine",
        "country_code": "UA",
        "provider": "Eastern Europe Docker VM",
        "region": "Kyiv / Ukraine",
        "container": "eurovision20-dc-ukraine",
        "description": "Handles Ukraine incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-united-kingdom": {
        "display_name": "United Kingdom Datacenter",
        "country": "United Kingdom",
        "country_code": "GB",
        "provider": "Western Europe Docker VM",
        "region": "London / United Kingdom",
        "container": "eurovision20-dc-united-kingdom",
        "description": "Handles United Kingdom incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-switzerland": {
        "display_name": "Switzerland Datacenter",
        "country": "Switzerland",
        "country_code": "CH",
        "provider": "Central Europe Docker VM",
        "region": "Zurich / Switzerland",
        "container": "eurovision20-dc-switzerland",
        "description": "Handles Switzerland incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-austria": {
        "display_name": "Austria Datacenter",
        "country": "Austria",
        "country_code": "AT",
        "provider": "Central Europe Docker VM",
        "region": "Vienna / Austria",
        "container": "eurovision20-dc-austria",
        "description": "Handles Austria incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-ireland": {
        "display_name": "Ireland Datacenter",
        "country": "Ireland",
        "country_code": "IE",
        "provider": "Western Europe Docker VM",
        "region": "Dublin / Ireland",
        "container": "eurovision20-dc-ireland",
        "description": "Handles Ireland incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-czechia": {
        "display_name": "Czechia Datacenter",
        "country": "Czechia",
        "country_code": "CZ",
        "provider": "Central Europe Docker VM",
        "region": "Prague / Czechia",
        "container": "eurovision20-dc-czechia",
        "description": "Handles Czechia incoming votes and sends vote batches to the central aggregator.",
    },
    "dc-estonia": {
        "display_name": "Estonia Datacenter",
        "country": "Estonia",
        "country_code": "EE",
        "provider": "Northern Europe Docker VM",
        "region": "Tallinn / Estonia",
        "container": "eurovision20-dc-estonia",
        "description": "Handles Estonia incoming votes and sends vote batches to the central aggregator.",
    },
}

FRIEND_BIAS = {
    "BE": ['FR', 'NL', 'DE'],     "FR": ['BE', 'CH', 'IT', 'ES'],     "DE": ['AT', 'CH', 'NL', 'PL', 'BE'],     "SE": ['NO', 'DK', 'FI', 'EE'],     "NO": ['SE', 'DK', 'FI'],     "DK": ['SE', 'NO', 'DE'],     "FI": ['SE', 'NO', 'EE'],     "EE": ['FI', 'SE'],     "IT": ['FR', 'CH', 'ES', 'GR'],     "ES": ['PT', 'FR', 'IT'],     "PT": ['ES', 'FR'],     "GR": ['CY', 'IT', 'UA'],     "NL": ['BE', 'DE', 'GB'],     "GB": ['IE', 'FR', 'NL'],     "IE": ['GB'],     "PL": ['UA', 'DE', 'CZ'],     "UA": ['PL', 'EE', 'CZ'],     "CZ": ['PL', 'DE', 'AT'],     "AT": ['DE', 'CH', 'CZ'],     "CH": ['DE', 'FR', 'IT', 'AT']
}


def ensure_directories() -> None:
    for folder in (DATA_DIR, RESULTS_DIR, LOG_DIR, STATIC_DIR):
        folder.mkdir(exist_ok=True)
