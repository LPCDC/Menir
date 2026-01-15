MATCH (n) WHERE n.project = 'Itaú' OR n.project_id = 'itau_15220012' RETURN count(n) AS node_count
