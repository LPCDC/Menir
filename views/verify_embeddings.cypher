MATCH (n:Document) WHERE n.project='Itaú' AND n.embedding IS NOT NULL RETURN count(n) AS embedded_count, size(n.embedding) AS dim, n.embedding_model AS model
