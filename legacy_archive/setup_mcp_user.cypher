// 1. Create Role with Read-Only Access
CREATE ROLE ai_reader_role IF NOT EXISTS;
GRANT ACCESS ON DATABASE neo4j TO ai_reader_role;
GRANT TRAVERSE ON GRAPH neo4j TO ai_reader_role;
GRANT READ {*} ON GRAPH neo4j TO ai_reader_role;
DENY WRITE ON GRAPH neo4j TO ai_reader_role;

// 2. Create User (Change 'StrongPassword!' to a real secure password)
// The user should replace 'StrongPassword!' before running.
CREATE USER ai_reader IF NOT EXISTS SET PASSWORD 'MenirReader2026!' CHANGE NOT REQUIRED;
GRANT ROLE ai_reader_role TO ai_reader;

// 3. Verify
SHOW USERS WHERE user = 'ai_reader';
