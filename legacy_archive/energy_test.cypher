// Define parameters for routing
:param { src: "A", dst: "D" }

// Run energy-aware routing (fallback without GDS)
MATCH p = (a:Node {id:$src})-[:REL*1..5]->(b:Node {id:$dst})
WITH p,
     reduce(cost=0.0, r IN relationships(p) | cost + coalesce(r.energyCost, 1.0)) AS cost
RETURN p AS bestPath, cost
ORDER BY cost ASC
LIMIT 1;

// Expected result with sample_graph:
// Best path: A -> B -> C -> D (cost 8)
