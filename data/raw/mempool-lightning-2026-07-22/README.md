# mempool.space Lightning projection captured on 2026-07-22

## Retrieval record

- Retrieval time: `2026-07-22 15:20:31 +08:00` (`Asia/Hong_Kong`).
- API statistics timestamp: `2026-07-22T00:00:00.000Z`.
- Network statistics endpoint: <https://mempool.space/api/v1/lightning/statistics/latest>.
- Geolocated-channel endpoint: <https://mempool.space/api/v1/lightning/channels-geo>.
- Upstream implementation: <https://github.com/mempool/mempool> at commit
  `e9d6cf8c042f946be53e372bb36530cd7b7851a4`.

| File | Bytes | SHA-256 |
|---|---:|---|
| `channels-geo.json` | 2,047,601 | `fbddddc486a8bb644520c373fd9588dc3811a6414c77185f0b2e8740e338637b` |
| `statistics-latest.json` | 719 | `14800a80c2ffd43c210ae1a89e7d1335a37e64dd95df54ce26e5dcf5b7a53ee9` |
| `mempool-source/channels.api.ts` | 26,625 | `5bcc7ad4183cf24606ee2bf5d5b52e2fca836a887af33d2e730190816366913c` |
| `mempool-source/channels.routes.ts` | 5,490 | `84d16225baf368c5863b5eee2abfc3ed88143faee5fd6235c70df968f7a3b3ae` |

The statistics response reports 17,270 nodes and 39,077 channels for the
2026-07-22 observation. These totals describe the mempool.space observer's
full indexed graph and are **not** the shape of `channels-geo.json`.

## Exact API projection

The captured upstream source fixes the endpoint semantics. Without a node-key
parameter, `channels-geo` selects rows satisfying all of the following:

1. `channels.status = 1` (active in the observer database);
2. both endpoint nodes have non-null latitude and longitude;
3. `channels.capacity > 1000000` sat;
4. rows are grouped by the ordered endpoint columns;
5. groups are ordered by channel capacity descending;
6. at most 10,000 rows are returned.

Each response row is an eight-element array:

`[node1_pubkey, node1_alias, node1_longitude, node1_latitude, node2_pubkey, node2_alias, node2_longitude, node2_latitude]`.

No channel identifier, individual capacity, payment flow, directional balance,
or success/failure observation is present in this response.

## Local structural audit

- JSON records: 10,000; malformed records: 0.
- Unique undirected endpoint pairs: 9,999.
- Exact reversed-pair duplicates after undirected canonicalization: 1.
- Nodes: 1,277; simple undirected edges: 9,999; self-loops: 0.
- Connected components: 3.
- Largest component: 1,273 nodes and 9,997 edges; diameter 6.

The one reversed pair is collapsed deterministically and counted; no other
parallel-channel claim can be made from this endpoint because it groups by
endpoint columns and omits channel identifiers.

## Claim boundary

This capture is a **current, filtered, high-capacity geolocated topology
projection from one public observer**. It is useful only as an external
time-sensitivity check. It is not a complete 2026 Lightning graph and must not
be described as real payment traffic, balances, failure times, or an unbiased
sample of channels.
