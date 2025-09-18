// Blockchain auditing: generate SHA-256 hash for decision payload
WITH $decisionPayload AS payload
RETURN apoc.util.sha256([payload]) AS hash;

// Example of storing the hash
MERGE (d:Decision {id: apoc.create.uuid()})
SET d.hash = apoc.util.sha256([payload]), d.timestamp = timestamp();
