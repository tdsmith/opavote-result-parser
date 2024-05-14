import re
from collections.abc import Mapping
from os import PathLike
from typing import IO

import attr
from bs4 import BeautifulSoup


@attr.frozen(kw_only=True)
class Ballot:
    sequence: int
    token: str | None = None
    weight: int | None = None
    # Mapping of candidate name -> integer rank
    # Unranked candidates are absent
    ranks: Mapping[str, int]


VOTER_RE = re.compile(r"Voter: ([A-Z]+)")
WEIGHT_RE = re.compile(r"Weight: (\d+)")
COUNTER_RE = re.compile(r"\((\d+)/(\d+)\)")


def parse(path_or_file: IO[str] | PathLike | str) -> list[Ballot]:
    """Parse a page of an election HTML result.

    Ballots look like:

    <div class="ballot-page">
    <h1>Looney Tunes</h1>
    <div class="ballot">
    <div class="candidate">Voter: ZAYIESWE</div>
    <div class="candidate">Weight: 70</div>
    <div class="candidate"><div class="rank"></div> Bugs Bunny</div>
    <div class="candidate"><div class="rank"></div> Daffy Duck</div>
    <div class="candidate"><div class="rank">3</div> Porky Pig</div>
    <div class="candidate"><div class="rank"></div> Tweety Bird</div>
    <div class="candidate"><div class="rank"></div> Sylvester the Cat</div>
    <div class="candidate"><div class="rank"></div> Yosemite Sam</div>
    <div class="candidate"><div class="rank"></div> Tasmanian Devil</div>
    <div class="candidate"><div class="rank">2</div> Elmer Fudd</div>
    <div class="candidate"><div class="rank"></div> Road Runner</div>
    <div class="candidate"><div class="rank">1</div> Wile E. Coyote</div>
    </div>
    <div class="logo">OpaVote (www.opavote.com)</div>
    <div class="counter">(20/21)</div>
    </div>
    """

    if isinstance(path_or_file, (PathLike, str)):
        path_or_file = open(path_or_file, "rt")
    soup = BeautifulSoup(path_or_file, "html.parser")
    pages = soup.find_all("div", class_="ballot-page")
    ballots = []
    for page in pages:
        found = {}
        text = page.get_text()
        if m := VOTER_RE.search(text):
            found["token"] = m[1]
        if m := WEIGHT_RE.search(text):
            found["weight"] = int(m[1])
        ranks = {}
        candidates = page.css.select(".candidate:has(.rank)")
        for candidate in candidates:
            rank = candidate.find(class_="rank").string
            if not rank:
                continue
            candidate = list(candidate.stripped_strings)[-1]
            ranks[candidate] = int(rank)

        counter_div = page.find(class_="counter")
        m = COUNTER_RE.match(counter_div.string)
        assert m
        sequence = int(m[1])

        ballot = Ballot(sequence=sequence, ranks=ranks, **found)
        ballots.append(ballot)
    return ballots
