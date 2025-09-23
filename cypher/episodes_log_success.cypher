// cypher/episodes_log_success.cypher
MERGE (e:Episode {commit:$commit_hash})
SET e.ts = datetime(),
    e.status = "success",
    e.project = $project,
    e.source = "git-hook"
RETURN e;
