// ============================================================
// Queries de Auditoria - Livro Débora (Menir Graph)
// ============================================================
// Copie e cole estas queries no Neo4j Browser para análise

// 1. Contagem de nós por label
CALL db.labels() YIELD label
CALL {
  WITH label
  MATCH (n)
  WHERE label IN labels(n)
  RETURN count(n) AS count
}
RETURN label, count
ORDER BY count DESC;

// 2. Contagem de relações por tipo
MATCH ()-[r]->()
RETURN type(r) AS relType, count(r) AS relCount
ORDER BY relCount DESC;

// 3. Todos os personagens e quantas cenas aparecem
MATCH (c:Character)-[:APPEARS_IN]->(s:Scene)
WITH c.name AS character, count(DISTINCT s) AS scenesCount
RETURN character, scenesCount
ORDER BY scenesCount DESC;

// 4. Para cada cena: quantas vezes aparece cada personagem
MATCH (s:Scene)<-[:APPEARS_IN]-(c:Character)
RETURN s.id AS sceneId, s.title AS sceneTitle, collect(c.name) AS charactersInScene
ORDER BY s.sceneIndex;

// 5. Todos os eventos de uma cena específica (ex: scene_04)
MATCH (s:Scene {id: "scene_04"})<-[:OCCURS_IN]-(e:Event)
RETURN e.eventIndex AS idx, e.eventType AS type, e.summary AS summary
ORDER BY idx;

// 6. Relações diretas entre personagens (Character ↔ Character), se houver
MATCH (p1:Character)-[r]-(p2:Character)
RETURN p1.name AS from, type(r) AS relation, p2.name AS to
ORDER BY from, to;

// 7. Rede de conexões entre personagens via cenas compartilhadas (grau 2)
// mostra pares de personagens que aparecem na mesma cena
MATCH (p1:Character)-[:APPEARS_IN]->(s:Scene)<-[:APPEARS_IN]-(p2:Character)
WHERE p1.id < p2.id
RETURN p1.name AS char1, p2.name AS char2, collect(s.id) AS sharedScenes, count(s) AS countScenes
ORDER BY countScenes DESC;

// 8. Listar caminhos completos de eventos por cena — para checar ordem narrativa
MATCH (s:Scene)<-[:HAS_SCENE]-(cv:ChapterVersion {id:"cap1_better_v1.0"})
MATCH path = (s)<-[:OCCURS_IN]-(e:Event)
RETURN s.title AS sceneTitle, e.eventIndex AS eventIndex, e.summary AS eventSummary
ORDER BY s.sceneIndex, e.eventIndex;

// 9. Verificar personagens "órfãos" — personagens sem cenas associadas
MATCH (c:Character)
WHERE NOT (c)-[:APPEARS_IN]->(:Scene)
RETURN c.name AS orphanCharacter;

// 10. Exportar subgrafo de uma personagem específica — todas cenas, eventos e relações  
// (ex: para Caroline Howell)
MATCH path = (c:Character {name:"Caroline Howell"})-[:APPEARS_IN|ACTS_IN*0..3]-(x)
RETURN path
LIMIT 100;

// ============================================================
// QUERIES ADICIONAIS - ANÁLISE NARRATIVA
// ============================================================

// 11. Sequência completa de eventos do capítulo (timeline narrativa)
MATCH path = (e:Event)-[:NEXT_EVENT*0..]->(next:Event)
WHERE NOT ()-[:NEXT_EVENT]->(e)
WITH nodes(path) AS eventChain
UNWIND eventChain AS evt
RETURN evt.eventId AS eventId, evt.eventIndex AS idx, evt.summary AS summary, evt.eventType AS type
ORDER BY evt.eventId;

// 12. Mapa de lugares e suas cenas
MATCH (p:Place)<-[:SET_IN]-(s:Scene)
RETURN p.name AS place, p.type AS placeType, collect(s.title) AS scenes, count(s) AS sceneCount
ORDER BY sceneCount DESC;

// 13. Personagens principais (aparecem em mais de 2 cenas)
MATCH (c:Character)-[:APPEARS_IN]->(s:Scene)
WITH c, count(DISTINCT s) AS appearances
WHERE appearances > 2
RETURN c.name AS mainCharacter, appearances
ORDER BY appearances DESC;

// 14. Eventos por tipo (ACTION, DIALOGUE, REVELATION, etc.)
MATCH (e:Event)
RETURN e.eventType AS eventType, count(e) AS count
ORDER BY count DESC;

// 15. Grafo completo de uma cena (personagens, eventos, lugar)
MATCH (s:Scene {id: "scene_01"})
OPTIONAL MATCH (s)<-[:APPEARS_IN]-(c:Character)
OPTIONAL MATCH (s)<-[:OCCURS_IN]-(e:Event)
OPTIONAL MATCH (s)-[:SET_IN]->(p:Place)
RETURN s.title AS scene,
       collect(DISTINCT c.name) AS characters,
       collect(DISTINCT e.summary) AS events,
       p.name AS place;

// 16. Verificar integridade: ChapterVersion com hash
MATCH (v:ChapterVersion)
RETURN v.id AS versionId, v.versionTag AS tag, v.hash AS fileHash, v.databaseOrigin AS origin, v.updatedAt AS lastUpdate;

// 17. Estrutura hierárquica completa (Work → Chapter → ChapterVersion → Scenes)
MATCH path = (w:Work)-[:HAS_CHAPTER]->(c:Chapter)<-[:VERSION_OF]-(v:ChapterVersion)-[:HAS_SCENE]->(s:Scene)
RETURN w.title AS work, c.number AS chapter, v.versionTag AS version, count(s) AS totalScenes;

// 18. Sequência de cenas com NEXT_SCENE
MATCH path = (s:Scene)-[:NEXT_SCENE*0..]->(next:Scene)
WHERE NOT ()-[:NEXT_SCENE]->(s)
WITH nodes(path) AS sceneChain
UNWIND sceneChain AS scene
RETURN scene.sceneIndex AS idx, scene.id AS sceneId, scene.title AS title
ORDER BY idx;

// 19. Personagens por role (protagonist, friend, family, staff)
MATCH (c:Character)
RETURN c.role AS role, collect(c.name) AS characters, count(c) AS count
ORDER BY count DESC;

// 20. Análise de co-ocorrência: quantas vezes cada par de personagens aparece junto
MATCH (c1:Character)-[:APPEARS_IN]->(s:Scene)<-[:APPEARS_IN]-(c2:Character)
WHERE c1.id < c2.id
WITH c1.name AS char1, c2.name AS char2, count(DISTINCT s) AS coOccurrences
WHERE coOccurrences > 1
RETURN char1, char2, coOccurrences
ORDER BY coOccurrences DESC;

// ============================================================
// QUERIES DE VALIDAÇÃO - TESTES DE INTEGRIDADE
// ============================================================

// 21. Verificar cenas sem eventos
MATCH (s:Scene)
WHERE NOT (s)<-[:OCCURS_IN]-(:Event)
RETURN s.id AS sceneWithoutEvents, s.title AS title;

// 22. Verificar eventos sem cena
MATCH (e:Event)
WHERE NOT (e)-[:OCCURS_IN]->(:Scene)
RETURN e.eventId AS orphanEvent, e.summary AS summary;

// 23. Verificar cenas sem personagens
MATCH (s:Scene)
WHERE NOT (s)<-[:APPEARS_IN]-(:Character)
RETURN s.id AS sceneWithoutCharacters, s.title AS title;

// 24. Verificar cenas sem lugar
MATCH (s:Scene)
WHERE NOT (s)-[:SET_IN]->(:Place)
RETURN s.id AS sceneWithoutPlace, s.title AS title;

// 25. Contador geral de todos os tipos de nós
MATCH (n)
RETURN labels(n)[0] AS nodeType, count(n) AS total
ORDER BY total DESC;

// ============================================================
// EXPORTAÇÃO / BACKUP
// ============================================================

// 26. Exportar estrutura completa para JSON (use APOC se disponível)
// CALL apoc.export.json.all("livro_debora_backup.json", {useTypes:true})

// 27. Snapshot do estado atual
MATCH (w:Work {id: "better_in_manhattan"})
OPTIONAL MATCH (w)-[:HAS_CHAPTER]->(c:Chapter)
OPTIONAL MATCH (c)<-[:VERSION_OF]-(v:ChapterVersion)
OPTIONAL MATCH (v)-[:HAS_SCENE]->(s:Scene)
OPTIONAL MATCH (s)<-[:OCCURS_IN]-(e:Event)
OPTIONAL MATCH (s)<-[:APPEARS_IN]-(char:Character)
OPTIONAL MATCH (s)-[:SET_IN]->(p:Place)
RETURN 
  w.title AS work,
  count(DISTINCT c) AS chapters,
  count(DISTINCT v) AS versions,
  count(DISTINCT s) AS scenes,
  count(DISTINCT e) AS events,
  count(DISTINCT char) AS characters,
  count(DISTINCT p) AS places;
