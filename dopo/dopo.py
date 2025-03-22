"""

"""
import bw2data as bd
from pathlib import Path

from .activity_filter import generate_sets_from_filters, _get_mapping
from .methods import MethodFinder
from .lca import sector_lca_scores

MAPPING_DIR = Path(__file__).resolve().parent / "mapping"

def load_sectors():
    """ Search for .yaml files in dopo/mapping. Return a list of sector names without the extension. """
    return [f.stem.replace(".yaml", "") for f in MAPPING_DIR.glob("*.yaml")]

SECTORS = load_sectors()

class Dopo:
    def __init__(self):
        self._dopo = None
        self.methods = MethodFinder()
        self.databases = None
        self.activities = {}
        self.results = None
        self.sectors = None

    def __str__(self):
        return f"Dopo: {self._dopo}"

    def add_sectors(self, sectors: list = None):
        sectors = sectors or SECTORS

        if not all([s in SECTORS for s in sectors]):
            raise ValueError("Invalid sector name." f"Valid sectors are: {SECTORS}")

        self.sectors = sectors
        self.find_activities()

    def find_activities(self):
        if self.databases is None:
            print("No databases found.")
            return

        if self.sectors is None:
            print("No sectors found.")
            return

        if len(self.databases) > 0:
            for db in self.databases:
                for sector in self.sectors:
                    if sector in self.activities:
                        self.activities[sector].update(
                            generate_sets_from_filters(
                                _get_mapping(Path(MAPPING_DIR) / f"{sector}.yaml"),
                                bd.Database(db),
                            )[sector]
                        )
                    else:
                        self.activities[sector] = generate_sets_from_filters(
                            _get_mapping(Path(MAPPING_DIR) / f"{sector}.yaml"),
                            bd.Database(db),
                        )[sector]

        else:
            print("No databases found.")

    def analyze(self, cutoff=0.01):
        if self.activities:
            self.results = sector_lca_scores(
                self.activities,
                self.methods.methods,
                cutoff=cutoff,
            )
