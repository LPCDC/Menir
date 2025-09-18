// Sample graph for Menir testing

// Create nodes
MERGE (a:Node {id:"A"})
MERGE (b:Node {id:"B"})
MERGE (c:Node {id:"C"})
MERGE (d:Node {id:"D"})

// Create relationships with energyCost property
MERGE (a)-[:REL {energyCost: 5}]->(b)
MERGE (b)-[:REL {energyCost: 2}]->(c)
MERGE (a)-[:REL {energyCost: 10}]->(c)
MERGE (c)-[:REL {energyCost: 1}]->(d)
MERGE (b)-[:REL {energyCost: 4}]->(d);

// Example query after loading:
// :param { src: "A", dst: "D" }
// MATCH p = (a:Node {id:$src})-[:REL*1..5]->(b:Node {id:$dst})
// WITH p, reduce(cost=0.0, r IN relationships(p) | cost + coalesce(r.energyCost, 1.0)) AS cost
// RETURN p AS bestPath, cost ORDER BY cost ASC LIMIT 1;
