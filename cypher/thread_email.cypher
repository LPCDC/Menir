MERGE (m:Documento {id:$id})
SET m.doc_type='email', m.message_id=$msgid, m.in_reply_to=$irt, m.references=$refs
WITH m
MATCH (parent:Documento {message_id: m.in_reply_to})
MERGE (m)-[:REPLY_TO]->(parent);
