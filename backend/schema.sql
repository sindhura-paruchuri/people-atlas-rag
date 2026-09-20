CREATE TABLE IF NOT EXISTS people (id VARCHAR(64) PRIMARY KEY, name VARCHAR(200) NOT NULL, role VARCHAR(200) NOT NULL, location VARCHAR(200) NOT NULL, skills JSON NOT NULL, bio TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS queries (id CHAR(36) PRIMARY KEY, question TEXT NOT NULL, result_json JSON NOT NULL, created_at DATETIME NOT NULL);
CREATE TABLE IF NOT EXISTS feedback (query_id CHAR(36) PRIMARY KEY, rating SMALLINT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(query_id) REFERENCES queries(id), CHECK (rating IN (-1,1)));
INSERT IGNORE INTO people VALUES ('p001','Maya Chen','Senior ML Engineer','Austin, TX','["Python", "RAG", "Pinecone"]','Builds retrieval pipelines and evaluates grounded answers for enterprise knowledge systems.');
INSERT IGNORE INTO people VALUES ('p002','Arjun Rao','Data Engineer','Dallas, TX','["Python", "MySQL", "AWS"]','Designs reliable ingestion pipelines, SQL data models, and cloud data platforms.');
INSERT IGNORE INTO people VALUES ('p003','Sofia Martinez','Full Stack Engineer','Miami, FL','["React", "TypeScript", "Python"]','Creates accessible interfaces and FastAPI services for AI applications.');
INSERT IGNORE INTO people VALUES ('p004','Jordan Williams','AI Platform Engineer','Austin, TX','["Docker", "MCP", "Python"]','Runs containerized agent services and builds secure tools for language models.');
INSERT IGNORE INTO people VALUES ('p005','Priya Shah','Applied Scientist','Seattle, WA','["Evaluation", "RAG", "PyTorch"]','Develops retrieval benchmarks and measures answer quality with human feedback.');
INSERT IGNORE INTO people VALUES ('p006','Ethan Brooks','Backend Engineer','New York, NY','["MySQL", "FastAPI", "Docker"]','Builds database APIs, service authentication, and observable distributed systems.');
