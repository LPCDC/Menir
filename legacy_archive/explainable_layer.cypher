// Explainable layers: return a subgraph path
MATCH (u:User {id:$uid})-[:ASKED]->(q:Query {id:$qid})
MATCH p=(q)-[*..4]-(answer:Answer)
RETURN p LIMIT 1;
