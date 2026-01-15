// Verify Incipient Romance
MATCH (s:Character {name:'Spencer'})-[r:RELATED_TO {type:'Incipient_Romance'}]-(c:Character {name:'Caroline'})
RETURN r.type, r.source AS romance_source;

// Verify Tivoli
MATCH (p:Project {id:'tivoli_retrofit'}) RETURN p.name, p.status;
