DROP TABLE IF EXISTS articles;
CREATE TABLE articles(
   id              SERIAL PRIMARY KEY
  ,title           TEXT
  ,body            TEXT NOT NULL
  ,year            DATE NOT NULL
  ,paper           TEXT NOT NULL
  ,tokens          TSVECTOR
  ,paper_id           TEXT NOT NULL
);
