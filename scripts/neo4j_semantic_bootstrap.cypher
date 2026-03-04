// Vector index para Leads
CREATE VECTOR INDEX lead_intent_index IF NOT EXISTS
FOR (l:Lead) ON (l.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 768,
    `vector.similarity_function`: 'cosine'
  }
};

// Vector index para Eventos
CREATE VECTOR INDEX event_context_index IF NOT EXISTS
FOR (e:Event) ON (e.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 768,
    `vector.similarity_function`: 'cosine'
  }
};

// Vector index para Produtos
CREATE VECTOR INDEX product_index IF NOT EXISTS
FOR (p:Product) ON (p.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 768,
    `vector.similarity_function`: 'cosine'
  }
};
