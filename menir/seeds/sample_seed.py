#!/usr/bin/env python3
# menir/seeds/sample_seed.py
"""
Cria ~30+ nós: 6 pessoas, 3 cidades, 5 livros, 6 tópicos, 12 citações
Relacionamentos: LIVES_IN, WROTE, MENTORS, SAID, HAS_QUOTE, MENTIONS_TOPIC
Quotes com texto completo (50-100 palavras) para testes de embedding
"""
import os
from neo4j import GraphDatabase

# ==== DATA STRUCTURES ====

PEOPLE = [
    {
        "id": "person:luiz",
        "name": "Luiz",
        "role": "writer",
        "bio": "Luiz escreve, programa e monta grafos pessoais. Acredita que código e prosa podem conviver. Mentor informal de Débora."
    },
    {
        "id": "person:debora",
        "name": "Débora",
        "role": "author",
        "bio": "Débora transforma diários em literatura. Seu primeiro capítulo explora memória, culpa e identidade em tom confessional."
    },
    {
        "id": "person:caroline",
        "name": "Caroline",
        "role": "protagonist",
        "bio": "Caroline é a protagonista das narrativas de Débora. Mora entre Santos e São Paulo, lida com memórias fragmentadas."
    },
    {
        "id": "person:mentor_fantasma",
        "name": "Mentor Fantasma",
        "role": "mentor",
        "bio": "Figura recorrente nos cadernos de Luiz. Aparece em sonhos e anotações, oferece conselhos sobre escrita e sistemas."
    },
    {
        "id": "person:critico_anonimo",
        "name": "Crítico Anônimo",
        "role": "critic",
        "bio": "Voz crítica interna. Questiona a validade de tudo. Presente nos manuscritos como comentários à margem."
    },
    {
        "id": "person:editora_paciente",
        "name": "Editora Paciente",
        "role": "editor",
        "bio": "Editora que acompanha os projetos de Débora e Luiz. Acredita no potencial dos textos, mas cobra prazos e coerência."
    }
]

CITIES = [
    {"id": "city:santos", "name": "Santos"},
    {"id": "city:saopaulo", "name": "São Paulo"},
    {"id": "city:guaruja", "name": "Guarujá"}
]

BOOKS = [
    {
        "id": "book:debora_cap1",
        "title": "Livro da Débora – Capítulo Um",
        "genre": "autoficção"
    },
    {
        "id": "book:cadernos",
        "title": "Cadernos de Bordo",
        "genre": "anotações"
    },
    {
        "id": "book:ensaios_caroline",
        "title": "Ensaios de Caroline",
        "genre": "ensaio"
    },
    {
        "id": "book:manifesto_menir",
        "title": "Manifesto do Menir",
        "genre": "manifesto"
    },
    {
        "id": "book:atlas_pessoal",
        "title": "Atlas Pessoal",
        "genre": "cartografia"
    }
]

TOPICS = [
    {"id": "topic:memoria", "name": "memória"},
    {"id": "topic:culpa", "name": "culpa"},
    {"id": "topic:liberdade", "name": "liberdade"},
    {"id": "topic:escrita", "name": "escrita"},
    {"id": "topic:arquitetura", "name": "arquitetura"},
    {"id": "topic:cotidiano", "name": "cotidiano"}
]

QUOTES = [
    {
        "id": "quote:debora_memoria_1",
        "author_id": "person:debora",
        "book_id": "book:debora_cap1",
        "text": "Às vezes, lembrar dói menos do que fingir que nada aconteceu. As memórias voltam em fragmentos: o cheiro de café na cozinha, a luz da tarde entrando pela janela, a voz da minha mãe chamando meu nome. Cada pedaço traz consigo uma dor específica, mas também um alívio estranho. É como se, ao reconhecer a ferida, eu pudesse começar a curá-la.",
        "topics": ["topic:memoria", "topic:culpa"]
    },
    {
        "id": "quote:debora_culpa_1",
        "author_id": "person:debora",
        "book_id": "book:debora_cap1",
        "text": "A culpa é um bicho que mora no peito e não aceita desculpas. Ela cresce quando você tenta ignorá-la, se alimenta das suas justificativas. Eu tentei explicar para mim mesma que não era minha responsabilidade, que eu era só uma criança. Mas a culpa não entende lógica. Ela só entende presença, insistência, peso.",
        "topics": ["topic:culpa"]
    },
    {
        "id": "quote:luiz_escrita_1",
        "author_id": "person:luiz",
        "book_id": "book:cadernos",
        "text": "Escrever é como programar: você cria estruturas, define regras, espera que o sistema funcione. Mas, ao contrário do código, a prosa aceita contradições. Ela permite que duas verdades coexistam no mesmo parágrafo. Isso me fascina e me frustra ao mesmo tempo. Quero ordem, mas também quero que a bagunça faça sentido.",
        "topics": ["topic:escrita", "topic:arquitetura"]
    },
    {
        "id": "quote:caroline_santos_1",
        "author_id": "person:caroline",
        "book_id": "book:ensaios_caroline",
        "text": "Santos é uma cidade de passagem. As pessoas vêm, ficam um tempo, vão embora. Eu sempre quis ser diferente, criar raízes, mas a cidade parece dizer: 'Não adianta, você também vai partir.' Talvez seja por isso que eu nunca consigo me comprometer de verdade. Sei que, no fundo, estou só esperando o momento certo de ir embora.",
        "topics": ["topic:cotidiano", "topic:liberdade"]
    },
    {
        "id": "quote:mentor_sistema_1",
        "author_id": "person:mentor_fantasma",
        "book_id": "book:cadernos",
        "text": "Um sistema de memória precisa de redundância. Se você guardar tudo em um único lugar, vai perder quando esse lugar desaparecer. Espalhe suas lembranças: em textos, em grafos, em conversas. Assim, quando um nó falhar, os outros mantêm a rede viva. A memória não é um arquivo; é uma teia.",
        "topics": ["topic:memoria", "topic:arquitetura"]
    },
    {
        "id": "quote:critico_meta_1",
        "author_id": "person:critico_anonimo",
        "book_id": "book:manifesto_menir",
        "text": "Por que você insiste em escrever sobre escrita? Isso não é meta demais? No fundo, você está tentando criar um sistema que se explica sozinho, uma recursão infinita. Mas talvez seja exatamente isso que você precisa: um espelho que reflete outro espelho, criando profundidade onde antes havia apenas superfície.",
        "topics": ["topic:escrita"]
    },
    {
        "id": "quote:editora_prazo_1",
        "author_id": "person:editora_paciente",
        "book_id": "book:debora_cap1",
        "text": "Débora, eu entendo que o processo criativo tem o próprio ritmo. Mas, em algum momento, você precisa decidir: o livro está pronto ou não? A busca pela perfeição pode ser uma forma de procrastinação. Às vezes, é melhor publicar algo imperfeito e vivo do que guardar um manuscrito perfeito e morto na gaveta.",
        "topics": ["topic:escrita", "topic:liberdade"]
    },
    {
        "id": "quote:luiz_grafo_1",
        "author_id": "person:luiz",
        "book_id": "book:atlas_pessoal",
        "text": "Cada pessoa é um nó em um grafo maior. Você só consegue se entender quando mapeia as conexões: quem te influenciou, quem você influenciou, quais ideias circulam entre vocês. O Menir é uma tentativa de tornar esse grafo visível, de transformar relações implícitas em estruturas explícitas. Não é sobre armazenar dados; é sobre revelar padrões.",
        "topics": ["topic:arquitetura", "topic:memoria"]
    },
    {
        "id": "quote:debora_liberdade_1",
        "author_id": "person:debora",
        "book_id": "book:debora_cap1",
        "text": "A liberdade não é fazer o que você quer; é saber que você pode escolher. Durante anos, achei que estava presa às minhas memórias, condenada a repetir os mesmos padrões. Mas, ao escrever, percebi que posso reinterpretar o passado, dar novos significados às mesmas histórias. Isso é libertador: não mudar o que aconteceu, mas mudar o que isso significa.",
        "topics": ["topic:liberdade", "topic:memoria", "topic:escrita"]
    },
    {
        "id": "quote:caroline_saopaulo_1",
        "author_id": "person:caroline",
        "book_id": "book:ensaios_caroline",
        "text": "São Paulo é grande demais para caber na minha cabeça. Sempre que vou lá, me perco — não só fisicamente, mas também mentalmente. A cidade te força a ser múltipla, a ter várias versões de si mesma. Em Santos, sou a Caroline que todo mundo conhece. Em São Paulo, posso ser outra pessoa. Isso assusta e atrai ao mesmo tempo.",
        "topics": ["topic:cotidiano", "topic:liberdade"]
    },
    {
        "id": "quote:mentor_recursao_1",
        "author_id": "person:mentor_fantasma",
        "book_id": "book:manifesto_menir",
        "text": "A recursão é uma ferramenta poderosa, mas perigosa. Se você não definir uma condição de parada, o sistema entra em loop infinito e trava. O mesmo vale para a autorreflexão: você precisa saber quando parar de analisar e começar a viver. Caso contrário, fica preso em um ciclo de pensamento que nunca se resolve.",
        "topics": ["topic:arquitetura", "topic:escrita"]
    },
    {
        "id": "quote:critico_contradicao_1",
        "author_id": "person:critico_anonimo",
        "book_id": "book:cadernos",
        "text": "Você diz que quer clareza, mas seus textos são cheios de ambiguidades. Você diz que quer simplicidade, mas constrói sistemas complexos. Talvez o problema seja que você ainda não aceitou a contradição como parte do processo. Ou talvez eu esteja errado, e a contradição seja exatamente o que torna tudo isso interessante.",
        "topics": ["topic:escrita", "topic:culpa"]
    }
]

LIVES_IN = [
    ("person:luiz", "city:saopaulo"),
    ("person:debora", "city:santos"),
    ("person:caroline", "city:santos"),
    ("person:mentor_fantasma", "city:saopaulo"),
    ("person:critico_anonimo", "city:guaruja"),
    ("person:editora_paciente", "city:saopaulo")
]

WROTE = [
    ("person:debora", "book:debora_cap1"),
    ("person:luiz", "book:cadernos"),
    ("person:caroline", "book:ensaios_caroline"),
    ("person:luiz", "book:manifesto_menir"),
    ("person:luiz", "book:atlas_pessoal")
]

MENTORS = [
    ("person:luiz", "person:debora"),
    ("person:mentor_fantasma", "person:luiz"),
    ("person:editora_paciente", "person:debora"),
    ("person:critico_anonimo", "person:luiz")
]


# ==== SEED FUNCTION ====

def seed_graph(driver):
    """
    Popula o grafo Neo4j com pessoas, cidades, livros, tópicos, citações
    e relacionamentos entre eles.
    """

    def _create_nodes(tx):
        # Pessoas
        for p in PEOPLE:
            tx.run(
                """
                MERGE (p:Person {id: $id})
                SET p.name = $name,
                    p.role = $role,
                    p.bio = $bio
                """,
                id=p["id"],
                name=p["name"],
                role=p["role"],
                bio=p["bio"]
            )

        # Cidades
        for c in CITIES:
            tx.run(
                """
                MERGE (c:City {id: $id})
                SET c.name = $name
                """,
                id=c["id"],
                name=c["name"]
            )

        # Livros
        for b in BOOKS:
            tx.run(
                """
                MERGE (b:Book {id: $id})
                SET b.title = $title,
                    b.genre = $genre
                """,
                id=b["id"],
                title=b["title"],
                genre=b["genre"]
            )

        # Tópicos
        for t in TOPICS:
            tx.run(
                """
                MERGE (t:Topic {id: $id})
                SET t.name = $name
                """,
                id=t["id"],
                name=t["name"]
            )

        # Citações
        for q in QUOTES:
            tx.run(
                """
                MERGE (q:Quote {id: $id})
                SET q.text = $text
                """,
                id=q["id"],
                text=q["text"]
            )

    def _create_relationships(tx):
        # LIVES_IN
        for person_id, city_id in LIVES_IN:
            tx.run(
                """
                MATCH (p:Person {id: $person_id})
                MATCH (c:City {id: $city_id})
                MERGE (p)-[:LIVES_IN]->(c)
                """,
                person_id=person_id,
                city_id=city_id
            )

        # WROTE
        for person_id, book_id in WROTE:
            tx.run(
                """
                MATCH (p:Person {id: $person_id})
                MATCH (b:Book {id: $book_id})
                MERGE (p)-[:WROTE]->(b)
                """,
                person_id=person_id,
                book_id=book_id
            )

        # MENTORS
        for mentor_id, mentee_id in MENTORS:
            tx.run(
                """
                MATCH (mentor:Person {id: $mentor_id})
                MATCH (mentee:Person {id: $mentee_id})
                MERGE (mentor)-[:MENTORS]->(mentee)
                """,
                mentor_id=mentor_id,
                mentee_id=mentee_id
            )

        # SAID (Person -> Quote)
        for q in QUOTES:
            tx.run(
                """
                MATCH (p:Person {id: $author_id})
                MATCH (q:Quote {id: $quote_id})
                MERGE (p)-[:SAID]->(q)
                """,
                author_id=q["author_id"],
                quote_id=q["id"]
            )

        # HAS_QUOTE (Book -> Quote)
        for q in QUOTES:
            tx.run(
                """
                MATCH (b:Book {id: $book_id})
                MATCH (q:Quote {id: $quote_id})
                MERGE (b)-[:HAS_QUOTE]->(q)
                """,
                book_id=q["book_id"],
                quote_id=q["id"]
            )

        # MENTIONS_TOPIC (Quote -> Topic)
        for q in QUOTES:
            for topic_id in q["topics"]:
                tx.run(
                    """
                    MATCH (q:Quote {id: $quote_id})
                    MATCH (t:Topic {id: $topic_id})
                    MERGE (q)-[:MENTIONS_TOPIC]->(t)
                    """,
                    quote_id=q["id"],
                    topic_id=topic_id
                )

    with driver.session() as session:
        session.execute_write(_create_nodes)
        session.execute_write(_create_relationships)


def print_counts(driver):
    """Imprime contagens de nós e relacionamentos para verificação."""
    with driver.session() as session:
        counts = {}
        for label in ["Person", "City", "Book", "Topic", "Quote"]:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) AS cnt")
            counts[label] = result.single()["cnt"]

        print("\n📊 Contagens:")
        print(f"   Pessoas: {counts['Person']}")
        print(f"   Cidades: {counts['City']}")
        print(f"   Livros: {counts['Book']}")
        print(f"   Tópicos: {counts['Topic']}")
        print(f"   Citações: {counts['Quote']}")


# ==== MAIN ====

def main():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "menir123")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        seed_graph(driver)
        print("✅ Seed: comprehensive graph created.")
        print_counts(driver)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
