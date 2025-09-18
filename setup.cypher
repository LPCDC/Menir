// Setup constraints and sample import
CREATE CONSTRAINT node_id IF NOT EXISTS FOR (n:Node) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT tx_hash IF NOT EXISTS FOR (t:Transaction) REQUIRE t.hash IS UNIQUE;

// Example of importing nodes from a published CSV
LOAD CSV WITH HEADERS FROM 'https://<user>.github.io/<repo>/nodes.csv' AS row
MERGE (n:Node {id: row.`id:ID`}) SET n += apoc.convert.fromJsonMap(row.props);

// Example of importing relationships from CSV
LOAD CSV WITH HEADERS FROM 'https://<user>.github.io/<repo>/rels.csv' AS row
MATCH (a:Node {id: row.`:START_ID`}) MATCH (b:Node {id: row.`:END_ID`})
MERGE (a)-[:REL {type: row.type}]->(b);
