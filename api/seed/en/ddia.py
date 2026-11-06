"""English version of the data systems theme (same cards, same order as the French one).

Chapter numbering: 1st edition of "Designing Data-Intensive Applications".
"""

from api.course_models import CardTranslation, ThemeTranslation

BOOK = "Martin Kleppmann, Designing Data-Intensive Applications (O'Reilly)"


def _ch(number: int, title: str) -> str:
    """Source label of a chapter (no link)."""
    return f"DDIA (1st ed.), ch. {number}: {title}"


THEME = ThemeTranslation(
    slug="ddia",
    titre="Data systems",
    source_label=BOOK,
    cards=[
        CardTranslation(
            titre="Reliability, scalability, maintainability",
            accroche=(
                "Three qualities structure any data system: it keeps working despite "
                "failures, it handles the load, it stays evolvable."
            ),
            points=[
                "Reliability: a fault (a component that deviates) is not a failure (the "
                "service stops); we design to tolerate faults.",
                "Scalability: describe the load with parameters (requests per second, "
                "read/write ratio) then measure performance.",
                "For latency, look at percentiles (p95, p99), not the average: the worst "
                "requests are often those of the best customers.",
                "Classic example: a social network feed, where precomputing the feed at "
                "write time (fan-out) is expensive for accounts with many followers.",
                "Maintainability: simplicity, operability and evolvability for the teams "
                "who will live with the system.",
            ],
            source_label=_ch(1, "Reliable, Scalable, and Maintainable Applications"),
        ),
        CardTranslation(
            titre="Data models",
            accroche=(
                "The choice of model (relational, document, graph) determines what is "
                "easy or painful to express."
            ),
            points=[
                "Relational: joins, strict schema on write, good for many relationships "
                "between entities.",
                "Document: self-contained data (a profile and its sub-items), flexible "
                "schema on read, good locality; less suited to many-to-many relationships.",
                "Graph: when everything is a relationship (social networks, "
                "recommendations) and traversals have variable depth.",
                "Models are converging: relational databases store JSON, document "
                "databases do joins.",
            ],
            source_label=_ch(2, "Data Models and Query Languages"),
        ),
        CardTranslation(
            titre="Storage: B-tree versus LSM-tree",
            accroche=(
                "Two main families of storage engines, with different trade-offs between "
                "reads and writes."
            ),
            points=[
                "B-tree: fixed-size pages updated in place, with a log (WAL) for "
                "recovery; predictable reads, very common in OLTP.",
                "LSM-tree: write to memory then flush to immutable sorted files merged in "
                "the background (compaction); fast sequential writes.",
                "Trade-off: LSM writes faster but costs compaction and may have less "
                "stable read latency; the B-tree reads well.",
                "OLTP versus OLAP: analytics read many rows over few columns, hence "
                "compressed column stores.",
            ],
            source_label=_ch(3, "Storage and Retrieval"),
            diagram_labels=["Write", "Memtable (memory)", "Sorted files (SSTable)", "Compaction"],
            edge_labels=["flush"],
        ),
        CardTranslation(
            titre="Encoding and schema evolution",
            accroche=(
                "In an evolving system, old and new code coexist: data formats must "
                "stay compatible."
            ),
            points=[
                "Backward compatibility: new code reads old data; forward compatibility: "
                "old code reads new data.",
                "Rolling upgrades force the two to coexist.",
                "JSON is readable but ambiguous and verbose; Protocol Buffers or Avro are "
                "compact and handle schema evolution.",
                "Practical rules: add optional fields, never reuse the identifier of a "
                "deleted field.",
            ],
            source_label=_ch(4, "Encoding and Evolution"),
        ),
        CardTranslation(
            titre="Replication",
            accroche=(
                "Replicating means keeping several copies of the data for availability, "
                "latency and read throughput."
            ),
            points=[
                "Leader-follower: all writes go through the leader, followers replicate; "
                "reads are spread across followers.",
                "Synchronous: wait for the copy, so durability but risk of blocking; "
                "asynchronous: fast but writes can be lost if the leader fails.",
                "Replication lag causes anomalies: reading your own write stops working, "
                "or reads seem to go back in time.",
                "Multi-leader: writes at several sites but conflicts to resolve.",
                "Leaderless (Dynamo style): quorums with w + r > n so reads and writes overlap.",
            ],
            source_label=_ch(5, "Replication"),
            diagram_labels=["Client", "Leader", "Follower 1", "Follower 2"],
            edge_labels=["writes", "log", "log"],
        ),
        CardTranslation(
            titre="Partitioning",
            accroche=(
                "When the data exceeds one machine, it is split into partitions spread "
                "across several nodes."
            ),
            points=[
                "By key range: good for range queries, but risk of a hot spot (for "
                "example all recent timestamps in the same place).",
                "By key hash: uniform distribution, but range queries are lost.",
                "Secondary indexes: local to each partition (simple write, read across "
                "all partitions) or global (targeted read, costlier write).",
                "Rebalancing: many fixed partitions rather than hashing modulo the number "
                "of nodes, which would move almost everything.",
                "Routing: the client, a proxy or a coordination service must know which "
                "partition holds the key.",
            ],
            source_label=_ch(6, "Partitioning"),
        ),
        CardTranslation(
            titre="Transactions and isolation",
            accroche=(
                "A transaction groups several operations into an all-or-nothing unit; "
                "isolation specifies what concurrent transactions see."
            ),
            points=[
                "ACID: atomicity (all or nothing), consistency (business rules "
                "respected), isolation, durability.",
                "Read committed: no reading of uncommitted data. Snapshot isolation: each "
                "transaction sees a consistent snapshot of the database.",
                "Anomalies to quote: lost update, write skew (two transactions read then "
                "write different items while violating a shared rule) and phantoms.",
                "Only serializability avoids them all: serial execution, two-phase "
                "locking or optimistic serializable snapshot isolation (SSI).",
            ],
            source_label=_ch(7, "Transactions"),
        ),
        CardTranslation(
            titre="The trouble with distributed systems",
            accroche=(
                "In a distributed system, one part can fail without the rest knowing: "
                "neither the network nor clocks can be trusted."
            ),
            points=[
                "The network loses, delays or duplicates messages; a timeout does not say "
                "whether the request was processed.",
                "Machine clocks drift: events from different machines cannot be ordered "
                "with timestamps.",
                "A pause (garbage collection, VM freeze) can make a node look dead, or "
                "make it believe it is still leader.",
                "Countermeasure: fencing tokens, which let the resource refuse a former "
                "lock holder.",
                "Reason in partial failures: some parts work, others do not.",
            ],
            source_label=_ch(8, "The Trouble with Distributed Systems"),
        ),
        CardTranslation(
            titre="Consistency and consensus",
            accroche=(
                "For several nodes to agree, strong consistency guarantees and consensus "
                "algorithms are used."
            ),
            points=[
                "Linearizability: the system behaves as if there were only one copy; "
                "costly in latency and availability.",
                "Causal consistency: order respected only between related events; weaker "
                "but more available.",
                "Consensus (Raft, Paxos, Zab) is used to elect a leader, lock, agree on a "
                "total order; it tolerates the failure of a minority of nodes.",
                "Two-phase atomic commit (2PC): a coordinator, blocking if it fails at the "
                "wrong time.",
                "CAP theorem, with nuance: during a partition, you must choose between "
                "consistency and availability.",
            ],
            source_label=_ch(9, "Consistency and Consensus"),
        ),
        CardTranslation(
            titre="Batch processing",
            accroche=(
                "Batch reads a large fixed input dataset and produces a derived output, "
                "without modifying the input."
            ),
            points=[
                "MapReduce: apply a function to each record (map), then group by key to "
                "aggregate (reduce).",
                "Dataflow engines (Spark, Flink) generalize this idea without writing to "
                "disk between steps.",
                "Immutable inputs and derived outputs: a job can be rerun after a bug "
                "without corrupting data.",
                "Use cases: building search indexes, models, reports; latency is counted "
                "in minutes or hours.",
            ],
            source_label=_ch(10, "Batch Processing"),
            diagram_labels=["Immutable input", "Map", "Group by key", "Reduce", "Derived output"],
        ),
        CardTranslation(
            titre="Stream processing",
            accroche=(
                "Streaming processes events as they arrive, with an ordered log as the backbone."
            ),
            points=[
                "Event log (Kafka): an ordered, partitioned, replayable sequence; "
                "consumers read at their own pace.",
                "Change data capture: turn the changes of a database into a stream, to "
                "feed a cache, an index, a warehouse.",
                "Event sourcing: the event log is the source of truth, the current state "
                "is a derived view of it.",
                "At-least-once delivery plus idempotence gives a practically exactly-once effect.",
                "Time windows and late events are the real difficulties.",
            ],
            source_label=_ch(11, "Stream Processing"),
        ),
    ],
)
