MATCH (h:Character {name:'Henry'}), (l:Character {name:'Luc'})
RETURN h.name AS henry_name, h.status AS henry_status, l.name AS luc_name, l.accent AS luc_accent
