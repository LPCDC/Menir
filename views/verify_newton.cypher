MATCH (u:User {name:'Luiz'})-[r1]->(p:Persona {name:'Newton Pipoca'})-[r2]->(c:Character {name:'Caroline'})
RETURN u.name, type(r1), p.name, type(r2), r2.as as role, c.name
