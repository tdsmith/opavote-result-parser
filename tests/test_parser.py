from opavote_result_parser.parse import Ballot, parse
from pathlib import Path

testroot = Path(__file__).parent


def test_parser():
    parsed = parse(testroot / "looney_tunes.html")
    assert len(parsed) == 21
