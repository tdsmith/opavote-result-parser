from opavote_result_parser.parse import Ballot
import pandas as pd
from typing import Iterable


def ballots_to_dataframe(ballots: Iterable[Ballot]) -> pd.DataFrame:
    rows = []
    candidates = set()
    for ballot in ballots:
        row = {
            "Sequence": ballot.sequence,
            "Token": ballot.token,
            "Weight": ballot.weight,
        }
        candidates |= ballot.ranks.keys()
        row.update(ballot.ranks)
        rows.append(row)
    columns = ["Sequence", "Token", "Weight", *sorted(candidates)]
    return pd.DataFrame.from_records(rows, columns=columns)
