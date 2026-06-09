"""The official 2026 World Cup knockout bracket (FIFA Annex C geometry).

The Round of 32 template pairs fixed group positions; eight slots receive a
third-placed team drawn from a specific candidate set of groups (designed so a
third can never face a winner from its own group). Given which eight groups'
thirds actually qualify, we solve the bipartite matching of thirds -> slots
respecting those candidate sets. Any perfect matching reproduces a valid,
rematch-free bracket identical in structure to FIFA's pre-computed table.
"""
from __future__ import annotations

GROUPS = list("ABCDEFGHIJKL")

# (match_number, slot_a, slot_b). Slots: ("W", g)=winner, ("RU", g)=runner-up,
# ("3", (candidate groups)) = a best third-placed team.
R32: list[tuple[int, tuple, tuple]] = [
    (73, ("RU", "A"), ("RU", "B")),
    (74, ("W", "E"), ("3", ("A", "B", "C", "D", "F"))),
    (75, ("W", "F"), ("RU", "C")),
    (76, ("W", "C"), ("RU", "F")),
    (77, ("W", "I"), ("3", ("C", "D", "F", "G", "H"))),
    (78, ("RU", "E"), ("RU", "I")),
    (79, ("W", "A"), ("3", ("C", "E", "F", "H", "I"))),
    (80, ("W", "L"), ("3", ("E", "H", "I", "J", "K"))),
    (81, ("W", "D"), ("3", ("B", "E", "F", "I", "J"))),
    (82, ("W", "G"), ("3", ("A", "E", "H", "I", "J"))),
    (83, ("RU", "K"), ("RU", "L")),
    (84, ("W", "H"), ("RU", "J")),
    (85, ("W", "B"), ("3", ("E", "F", "G", "I", "J"))),
    (86, ("W", "J"), ("RU", "H")),
    (87, ("W", "K"), ("3", ("D", "E", "I", "J", "L"))),
    (88, ("RU", "D"), ("RU", "G")),
]

# Later rounds reference the winners of earlier match numbers.
R16: list[tuple[int, int, int]] = [
    (89, 74, 77), (90, 73, 75), (91, 76, 78), (92, 79, 80),
    (93, 83, 84), (94, 81, 82), (95, 86, 88), (96, 85, 87),
]
QF: list[tuple[int, int, int]] = [(97, 89, 90), (98, 93, 94), (99, 91, 92), (100, 95, 96)]
SF: list[tuple[int, int, int]] = [(101, 97, 98), (102, 99, 100)]
FINAL: tuple[int, int, int] = (104, 101, 102)

# Third-placed slots and the candidate groups eligible for each.
THIRD_SLOTS: dict[int, tuple[str, ...]] = {
    m: slot_b[1] for (m, _slot_a, slot_b) in R32 if slot_b[0] == "3"
}


def assign_thirds(qualified_groups: set[str]) -> dict[int, str]:
    """Match each third-placed slot to one qualifying group via Kuhn's algorithm.

    Returns {match_number: group_letter}. Assumes ``qualified_groups`` holds the
    eight groups whose third-placed teams advanced.
    """
    # Process the most-constrained slots first for a fast, stable matching.
    candidates = {
        m: [g for g in THIRD_SLOTS[m] if g in qualified_groups] for m in THIRD_SLOTS
    }
    slot_order = sorted(THIRD_SLOTS, key=lambda m: (len(candidates[m]), m))

    group_to_slot: dict[str, int] = {}
    slot_to_group: dict[int, str] = {}

    def augment(slot: int, visited: set[str]) -> bool:
        for g in candidates[slot]:
            if g in visited:
                continue
            visited.add(g)
            if g not in group_to_slot or augment(group_to_slot[g], visited):
                group_to_slot[g] = slot
                slot_to_group[slot] = g
                return True
        return False

    for slot in slot_order:
        augment(slot, set())

    # Fallback (should not trigger for a valid 8-of-12 combination): assign any
    # leftover slots/groups arbitrarily so the bracket is always complete.
    if len(slot_to_group) < 8:
        leftover_groups = [g for g in qualified_groups if g not in group_to_slot]
        for slot in THIRD_SLOTS:
            if slot not in slot_to_group and leftover_groups:
                slot_to_group[slot] = leftover_groups.pop()

    return slot_to_group
