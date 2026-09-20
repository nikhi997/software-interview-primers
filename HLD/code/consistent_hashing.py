"""
Consistent hashing — the demo referenced in HLD Chapter 4.

Run it and watch how FEW keys move when you add a node. That "few keys move"
property is the entire reason consistent hashing exists: with naive
`hash(key) mod N`, changing N reshuffles almost every key.

    python3 consistent_hashing.py
"""

import hashlib
from bisect import bisect, insort


def _hash(value: str) -> int:
    """Hash a string to a point on the ring (an integer 0 .. 2^32-1)."""
    return int(hashlib.md5(value.encode()).hexdigest(), 16) % (2 ** 32)


class ConsistentHashRing:
    """
    A ring of nodes. Each physical node is placed at many positions on the
    ring (virtual nodes) so load stays balanced. A key belongs to the first
    node found clockwise from the key's position.
    """

    def __init__(self, virtual_nodes: int = 100):
        self.virtual_nodes = virtual_nodes
        self._ring: dict[int, str] = {}      # ring position -> physical node
        self._sorted_positions: list[int] = []

    def add_node(self, node: str) -> None:
        for i in range(self.virtual_nodes):
            pos = _hash(f"{node}#{i}")
            self._ring[pos] = node
            insort(self._sorted_positions, pos)

    def remove_node(self, node: str) -> None:
        for i in range(self.virtual_nodes):
            pos = _hash(f"{node}#{i}")
            del self._ring[pos]
            self._sorted_positions.remove(pos)

    def get_node(self, key: str) -> str:
        """Find the node responsible for a key: first node clockwise."""
        if not self._ring:
            raise ValueError("ring is empty")
        pos = _hash(key)
        idx = bisect(self._sorted_positions, pos)
        if idx == len(self._sorted_positions):  # wrapped past the end -> first
            idx = 0
        return self._ring[self._sorted_positions[idx]]


def _naive_mod(key: str, num_nodes: int) -> int:
    """The naive scheme for comparison: hash(key) mod N."""
    return _hash(key) % num_nodes


def demo() -> None:
    keys = [f"key-{i}" for i in range(10_000)]

    # --- Consistent hashing: add a node, count how many keys move ---
    ring = ConsistentHashRing(virtual_nodes=100)
    for node in ["A", "B", "C"]:
        ring.add_node(node)

    before = {k: ring.get_node(k) for k in keys}
    ring.add_node("D")  # grow the cluster
    after = {k: ring.get_node(k) for k in keys}

    moved = sum(1 for k in keys if before[k] != after[k])
    print("CONSISTENT HASHING")
    print(f"  added node D to a 3-node ring ({len(keys)} keys)")
    print(f"  keys that moved: {moved} ({moved / len(keys):.1%})")
    print(f"  (expect roughly 1/4 = 25% — only D's share moves)\n")

    # --- Naive mod N: same change, count how many keys move ---
    before_mod = {k: _naive_mod(k, 3) for k in keys}
    after_mod = {k: _naive_mod(k, 4) for k in keys}
    moved_mod = sum(1 for k in keys if before_mod[k] != after_mod[k])
    print("NAIVE hash(key) mod N")
    print(f"  changed N from 3 to 4 ({len(keys)} keys)")
    print(f"  keys that moved: {moved_mod} ({moved_mod / len(keys):.1%})")
    print(f"  (expect ~75% — almost everything reshuffles. This is the bomb.)")


if __name__ == "__main__":
    demo()
