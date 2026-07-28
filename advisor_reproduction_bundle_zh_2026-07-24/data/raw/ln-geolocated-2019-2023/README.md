# Lightning topology source record

## Source

- Dataset: Danila Valko and Jorge Marx Gómez, *Geolocated Lightning Network
  topology snapshots: a dataset covering 2019–2023*.
- Dataset DOI: <https://doi.org/10.7910/DVN/2OAVO6>
- Data descriptor DOI: <https://doi.org/10.1038/s41597-025-06413-7>
- Upstream raw gossip archive: Christian Decker,
  <https://doi.org/10.5281/zenodo.4088530>.
- Access date: 2026-07-22 (Asia/Hong_Kong).

The data descriptor reports 336 reconstructed GML snapshots derived from
public gossip archives.  Gossip views are best-effort and partially observed;
they do not expose private channel balances or payment flows.

## Files acquired in this workspace

| File | Dataverse file ID | Bytes | Upstream MD5 | Local SHA-256 |
|---|---:|---:|---|---|
| `shapes.geo.tab` | 12510545 | 26,135 | `b352d9c82527f8257127d7c453615760` | `e537dc94274f87a5b1833307e3ea8329eb909f7111a41abbd4dd67eceb91abce` |
| `scripts.zip` | 12510548 | 8,250 | `e8bbd45f923df2205e25d43907ae0ac3` | `e918dce74117a6f08d443b1fac27d6d4d2752638928bcb4552df475f8d35f044` |
| `snapshots.geo.zip` | 12510549 | 562,027,011 | `e6edd6fd7acae460abd0f70f71c9dbec` | `f380b71796edd86019ddc0b7822938559bfd40a2f650b21ccb66f14ef10e9320` |

`scripts/` is the mechanically extracted content of `scripts.zip`; the ZIP is
the hash authority.  The metadata table has 336 rows.  Three predeclared
candidate snapshots are:

| Date | Nodes | Channels | Mean degree | Diameter | File |
|---|---:|---:|---:|---:|---|
| 2020-10-14 | 5,963 | 29,940 | 10.0419252054 | 8 | `20201014.gml.geo` |
| 2022-05-31 | 15,947 | 79,552 | 9.9770489747 | 9 | `20220531.gml.geo` |
| 2023-07-16 | 15,100 | 64,212 | 8.5049006623 | 9 | `20230716.gml.geo` |

## Selected snapshots

The full ZIP matches the upstream MD5 exactly.  Only the three predeclared GML
files were mechanically extracted into `selected_snapshots/`:

| File | Bytes | SHA-256 |
|---|---:|---|
| `20201014.gml.geo` | 12,333,118 | `900dbdce07298a65bafcc793bb18efbcd4bd43875a412c4195213dda41bce802` |
| `20220531.gml.geo` | 37,893,056 | `1aee99d82a6f60791f17e4176d76d3cfa20cd5931397f46d627a89b6e646e7a4` |
| `20230716.gml.geo` | 32,928,305 | `ee1b054a6ba2cb0ea3184f9f68f5cca7d8e70d17ff2d9e44e5e8871be8a8b855` |

NetworkX reads them as simple undirected `Graph` objects.  Their node and edge
counts exactly match `shapes.geo.tab`.  Observed edge fields are `scid`,
`destination`, `timestamp`, `features`, `fee_base_msat`,
`fee_proportional_millionths`, `htlc_minimim_msat`, `htlc_maximum_msat`, and
`cltv_expiry_delta`.

GML stores `htlc_maximum_msat` values that exceed its native integer range as
decimal strings: 8,121, 27,590, and 26,587 edges respectively in the three
selected snapshots.  The local adapter accepts only positive decimal strings
and normalizes them to Python integers; arbitrary strings remain invalid.

The older raw `gossip-20201014.gsp.bz2` is 763,645,040 bytes and is not needed
for the first mapping implementation.

The 4,388-byte Zenodo release archive retained under
`../lnresearch-topology-20201014/` contains the MIT-licensed project README
and source record, not the 763 MB gossip payload.  It must not be described as
the topology snapshot itself.

## Use boundary

These sources provide public topology and routing-policy metadata only.  The
paper must call experiments based on them **real-topology / synthetic-demand**
experiments.  They cannot be represented as observed Lightning payment flows,
balances, failures, rebalancing events, or channel-closing causes.
