CREATE CONSTRAINT user_name_uniq IF NOT EXISTS FOR (u:User) REQUIRE u.name IS UNIQUE;
CREATE CONSTRAINT project_name_uniq IF NOT EXISTS FOR (p:Project) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT document_path_uniq IF NOT EXISTS FOR (d:Document) REQUIRE d.original_path IS UNIQUE;
