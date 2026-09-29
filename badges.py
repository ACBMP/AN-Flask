"""Rendering of the medal/badge markup shown next to player names."""

# Score awarded per badge rank on the achievements leaderboard.
BADGE_SCORES = {
    "1st": 5,
    "2nd": 4,
    "3rd": 3,
    "Trophy": 5,
    "Custom": 2,
    "Rookie": 2,
    "All-Star": 1,
}

# HTML entity for each rank's medal. "Custom" carries its own in the document.
BADGE_MEDALS = {
    "1st": "&#129351",
    "2nd": "&#129352",
    "3rd": "&#129353",
    "Trophy": "&#127942",
    "Rookie": "&#128304",
    "Special": "&#127941",
    "All-Star": "&#11088",
}

# The maximum number of badges displayed on a page.
BADGE_LIMIT = 5


def badge_score(badges):
    """Total achievement score for a player's badges."""
    return sum(BADGE_SCORES.get(b["rank"], 0) for b in badges)


def transform_badge_to_html(badge, badges=""):
    """Prepend one badge's markup to ``badges``."""
    rank = badge.get("rank")
    if rank == "Custom":
        medal = badge["medal"]["HTML"]
    elif rank in BADGE_MEDALS:
        medal = BADGE_MEDALS[rank]
    else:
        raise ValueError(
            "Unknown rank! Options are: 1st, 2nd, 3rd, Trophy, Rookie, Special, "
            "All-Star, and Custom."
        )

    if rank in ("Trophy", "Special", "All-Star", "Custom"):
        title = badge.get("name")
    elif rank == "Rookie":
        title = f"Season {badge.get('season')} Rookie of the Season"
    else:
        title = f"Season {badge.get('season')} {badge.get('mode')} {rank} Place"
    return f'<span title="{title}">{medal}</span>' + badges


def filter_badges(badges, mode):
    """Pick the badges most relevant to ``mode``, padding up to BADGE_LIMIT
    with the rest so the row stays full."""
    relevant = []
    other = []

    for b in badges:
        # Some badges have no mode of their own - eg rookie of the season.
        if b["mode"] == "all":
            relevant.append(b)
        elif mode.endswith(("AA Running", "AA Defending")):
            # AA cares about both directions - no priority between them for now.
            # Each game ("AA ...", "ACR AA ...") has its own badges.
            game = mode.rsplit("AA ", 1)[0]
            if b["mode"] in (game + "AA Running", game + "AA Defending"):
                relevant.append(b)
            else:
                other.insert(0, b)
        elif b["mode"] == mode:
            relevant.append(b)
        else:
            other.insert(0, b)

    # "other" is in reverse encounter order, and padding is prepended one at a
    # time, so the badges nearest the relevant ones are the earliest encountered.
    padding = other[: max(0, BADGE_LIMIT - len(relevant))]
    return padding[::-1] + relevant


def transform_badges(badges, mode=None):
    """Render badges to HTML. ``mode`` is optional so user profiles, which show
    every badge, can reuse this."""
    if mode:
        badges = filter_badges(badges, mode)
    badges_str = ""
    for badge in badges:
        badges_str = transform_badge_to_html(badge, badges_str)
    return badges_str


def full_badge_names(badges):
    """Badge markup with each medal's title spelled out beside it, one per line."""
    if not badges:
        return ""
    # transform_badges prepends each badge, so the rendered order is reversed.
    rendered = [transform_badge_to_html(b) for b in reversed(badges)]
    lines = []
    for span in rendered:
        name = span[span.find('"') + 1 : span.find(">") - 1]
        lines.append(f"{span} {name}<br>")
    return "".join(lines)
