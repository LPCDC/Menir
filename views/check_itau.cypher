MATCH (t:Task)
WHERE toLower(t.project_id) CONTAINS 'itau' OR toLower(t.id) CONTAINS 'itau'
OPTIONAL MATCH (t)<-[:IMPACTS]-(i:Impedance)
RETURN t.name, t.status, i.blocking_level AS impedance
ORDER BY impedance ASC
