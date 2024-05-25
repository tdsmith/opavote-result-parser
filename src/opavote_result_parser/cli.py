from pathlib import Path
from typing import Optional

import pandas as pd
import typer

from opavote_result_parser.parse import parse
from opavote_result_parser.transform import ballots_to_dataframe


def main(
    ballots_html: Path,
    merge: Optional[Path] = None,
    output: typer.FileTextWrite = "-",  # type: ignore
):
    ballots = parse(ballots_html)
    df = ballots_to_dataframe(ballots)

    if merge:
        to_merge = pd.read_csv(merge)
        df = df.merge(to_merge, how="left", left_on="Token", right_on="Code")

    # Ballot ranks are stored as floats because some of them
    # are missing and therefore represented as NaNs.
    # Cocerce them back to integer representations with the
    # float_format option.
    df.to_csv(output, index=False, float_format="%d")


def entrypoint():
    typer.run(main)


if __name__ == "__main__":
    entrypoint()
