// 1. Ipsis Literis Task Query
MATCH (t:Task {id: "silent_archivist:ch1"}) RETURN t.blocking_level, t.blocking_label, t.status AS task_status;

// 2. Entity Check
MATCH (h:Character {name:'Henry'}), (l:Character {name:'Luc'}) 
RETURN h.name, h.status, l.name, l.accent;

// 3. Expected Signal (Path to Impedance)
MATCH (t:Task {id: "silent_archivist:ch1"})<-[:IMPACTS]-(i:Impedance) 
RETURN i.blocking_level, i.reason;

// 4. Project Stats (Heuristic: Connected to Caroline)
MATCH (c:Character {name:'Caroline'})-[*1..2]-(n)
RETURN count(distinct n) AS neighborhood_count;
