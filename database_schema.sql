-- LexiGo Database Schema

-- Words table
CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,
    word VARCHAR(100) NOT NULL,
    polish_translation VARCHAR(100) NOT NULL,
    example_sentence_1 TEXT NOT NULL,
    example_sentence_2 TEXT NOT NULL,
    example_sentence_3 TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User notes table (user-specific notes for each word)
CREATE TABLE IF NOT EXISTS user_notes (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    word_id INTEGER NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    notes TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_email, word_id)
);

-- Indexes for better performance
CREATE INDEX idx_user_notes_email ON user_notes(user_email);
CREATE INDEX idx_user_notes_word_id ON user_notes(word_id);

-- Sample data
INSERT INTO words (word, polish_translation, example_sentence_1, example_sentence_2, example_sentence_3) VALUES
('serendipity', 'szczęśliwy traf', 'Finding that book was pure serendipity.', 'Their meeting was a moment of serendipity.', 'Serendipity played a role in their discovery.'),
('ephemeral', 'ulotny, przemijający', 'The beauty of cherry blossoms is ephemeral.', 'Fame can be ephemeral in the modern world.', 'Those ephemeral moments are precious.'),
('resilience', 'odporność, sprężystość', 'She showed great resilience after the setback.', 'The team''s resilience helped them win.', 'Building resilience takes time and practice.'),
('eloquent', 'elokwentny, wymowny', 'His speech was eloquent and moving.', 'She gave an eloquent defense of her position.', 'The painting was an eloquent expression of grief.'),
('ambiguous', 'niejednoznaczny, dwuznaczny', 'The message was deliberately ambiguous.', 'His answer remained ambiguous.', 'The contract contained ambiguous terms.');
