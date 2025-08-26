-- ============================================================================= 
-- COMPLETE DATABASE SCHEMA FOR PORTFOLIO BACKEND
-- =============================================================================
-- This file contains all table definitions, indexes, and initial data
-- required for the portfolio backend system with audio caching and management.

-- Drop existing tables (be careful in production!)
DROP TABLE IF EXISTS contact_submissions CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS custom_audio CASCADE;
DROP TABLE IF EXISTS audio_cache CASCADE;
DROP TABLE IF EXISTS chat_history CASCADE;
DROP TABLE IF EXISTS notes CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- =============================================================================
-- USERS TABLE
-- =============================================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- Create indexes for users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- =============================================================================
-- NOTES TABLE
-- =============================================================================
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags JSON DEFAULT '[]',
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    view_count INTEGER DEFAULT 0
);

-- Create indexes for notes
CREATE INDEX idx_notes_published ON notes(is_published);
CREATE INDEX idx_notes_category ON notes(category);
CREATE INDEX idx_notes_created_at ON notes(created_at DESC);

-- =============================================================================
-- CHAT HISTORY TABLE
-- =============================================================================
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) DEFAULT 'Anonymous',
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    ai_provider VARCHAR(50) DEFAULT 'groq',
    response_time INTEGER, -- Response time in milliseconds
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_id VARCHAR(255) -- Optional session tracking
);

-- Create indexes for chat_history
CREATE INDEX idx_chat_history_username ON chat_history(username);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at DESC);
CREATE INDEX idx_chat_history_session ON chat_history(session_id);

-- =============================================================================
-- AUDIO CACHE TABLE
-- =============================================================================
CREATE TABLE audio_cache (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    text_hash VARCHAR(32) NOT NULL UNIQUE, -- MD5 hash for quick lookup
    voice_id VARCHAR(100) DEFAULT 'default',
    voice_settings JSON DEFAULT '{}',
    audio_url TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    duration FLOAT, -- Duration in seconds
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source VARCHAR(20) DEFAULT 'generated' CHECK (source IN ('generated', 'uploaded'))
);

-- Create indexes for audio_cache
CREATE UNIQUE INDEX idx_audio_cache_text_hash ON audio_cache(text_hash);
CREATE INDEX idx_audio_cache_voice_id ON audio_cache(voice_id);
CREATE INDEX idx_audio_cache_last_used ON audio_cache(last_used DESC);
CREATE INDEX idx_audio_cache_created_at ON audio_cache(created_at DESC);
CREATE INDEX idx_audio_cache_source ON audio_cache(source);

-- =============================================================================
-- CUSTOM AUDIO TABLE
-- =============================================================================
CREATE TABLE custom_audio (
    id SERIAL PRIMARY KEY,
    note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    audio_url TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    duration FLOAT, -- Duration in seconds
    uploaded_by INTEGER REFERENCES users(id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    text_content TEXT -- Optional text content this audio represents
);

-- Create indexes for custom_audio
CREATE INDEX idx_custom_audio_note_id ON custom_audio(note_id);
CREATE INDEX idx_custom_audio_is_active ON custom_audio(is_active);
CREATE INDEX idx_custom_audio_uploaded_by ON custom_audio(uploaded_by);
CREATE INDEX idx_custom_audio_uploaded_at ON custom_audio(uploaded_at DESC);

-- =============================================================================
-- REVIEWS TABLE
-- =============================================================================
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    project VARCHAR(255), -- Optional project reference
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_approved BOOLEAN DEFAULT false,
    admin_notes TEXT -- Internal notes for admins
);

-- Create indexes for reviews
CREATE INDEX idx_reviews_is_approved ON reviews(is_approved);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_submitted_at ON reviews(submitted_at DESC);

-- =============================================================================
-- CONTACT SUBMISSIONS TABLE
-- =============================================================================
CREATE TABLE contact_submissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    message TEXT NOT NULL,
    phone VARCHAR(50),
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'in_progress', 'resolved', 'spam')),
    admin_notes TEXT,
    responded_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for contact_submissions
CREATE INDEX idx_contact_status ON contact_submissions(status);
CREATE INDEX idx_contact_submitted_at ON contact_submissions(submitted_at DESC);
CREATE INDEX idx_contact_email ON contact_submissions(email);

-- =============================================================================
-- SAMPLE DATA
-- =============================================================================

-- Insert default admin user (password: 'admin123' - change this!)
INSERT INTO users (username, email, password_hash, role) VALUES 
('admin', 'admin@robinson-portfolio.com', '$2a$12$LKmVgR7PZ1qQK1RZz1vBMe9JvjqGcXMfXJXhZBR7rJz1xhzF3nOr6', 'admin');

-- Insert sample notes
INSERT INTO notes (title, content, category, tags, is_published) VALUES 
('Welcome to My Portfolio', 'This is an introduction to my work and skills. I specialize in full-stack development with modern technologies.', 'introduction', '["welcome", "intro", "portfolio"]', true),
('About My Skills', 'I have experience in JavaScript, Python, React, Vue.js, Node.js, and database design. I enjoy creating interactive and user-friendly applications.', 'skills', '["javascript", "python", "react", "vue"]', true),
('Project Showcase', 'Here you can find examples of my recent projects, including web applications, APIs, and innovative solutions.', 'projects', '["projects", "showcase", "portfolio"]', true),
('Contact Information', 'Feel free to reach out to me for collaboration opportunities or any questions about my work.', 'contact', '["contact", "collaboration"]', true);

-- Insert sample reviews
INSERT INTO reviews (name, email, rating, comment, project, is_approved) VALUES 
('John Smith', 'john@example.com', 5, 'Amazing work on the web application! Very professional and responsive design.', 'E-commerce Platform', true),
('Sarah Johnson', 'sarah@example.com', 5, 'Robinson delivered exactly what we needed. Great communication throughout the project.', 'Portfolio Website', true),
('Mike Chen', 'mike@example.com', 4, 'Solid technical skills and clean code. Would recommend for any development project.', 'API Development', true);

-- =============================================================================
-- FUNCTIONS AND TRIGGERS
-- =============================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add trigger to notes table
CREATE TRIGGER update_notes_updated_at BEFORE UPDATE ON notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add trigger to users table  
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- PERFORMANCE OPTIMIZATIONS
-- =============================================================================

-- Create composite indexes for common query patterns
CREATE INDEX idx_audio_cache_voice_settings ON audio_cache USING GIN (voice_settings);
CREATE INDEX idx_custom_audio_note_active ON custom_audio(note_id, is_active);
CREATE INDEX idx_notes_category_published ON notes(category, is_published);

-- =============================================================================
-- SECURITY POLICIES (Row Level Security)
-- =============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE custom_audio ENABLE ROW LEVEL SECURITY;

-- Policy for users - users can only see their own data
CREATE POLICY user_self_access ON users
    FOR ALL TO authenticated_user
    USING (id = current_setting('app.current_user_id')::INTEGER);

-- Policy for admin access to all user data
CREATE POLICY admin_full_access ON users
    FOR ALL TO admin_role
    USING (true);

-- =============================================================================
-- MAINTENANCE FUNCTIONS
-- =============================================================================

-- Function to clean up old cache entries
CREATE OR REPLACE FUNCTION cleanup_old_cache(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM audio_cache 
    WHERE last_used < NOW() - INTERVAL '1 day' * days_old;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get cache statistics
CREATE OR REPLACE FUNCTION get_cache_stats()
RETURNS TABLE (
    total_entries BIGINT,
    total_size_bytes BIGINT,
    avg_file_size NUMERIC,
    oldest_entry TIMESTAMP WITH TIME ZONE,
    newest_entry TIMESTAMP WITH TIME ZONE,
    most_used_voice VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_entries,
        SUM(file_size) as total_size_bytes,
        AVG(file_size) as avg_file_size,
        MIN(created_at) as oldest_entry,
        MAX(created_at) as newest_entry,
        (SELECT voice_id FROM audio_cache GROUP BY voice_id ORDER BY COUNT(*) DESC LIMIT 1) as most_used_voice
    FROM audio_cache;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- BACKUP AND MONITORING
-- =============================================================================

-- Create a view for monitoring active custom audio
CREATE VIEW active_custom_audio_summary AS
SELECT 
    ca.note_id,
    n.title as note_title,
    ca.title as audio_title,
    ca.file_size,
    ca.duration,
    ca.uploaded_at,
    u.username as uploaded_by
FROM custom_audio ca
JOIN notes n ON ca.note_id = n.id
LEFT JOIN users u ON ca.uploaded_by = u.id
WHERE ca.is_active = true
ORDER BY ca.uploaded_at DESC;

-- Create a view for cache usage statistics
CREATE VIEW cache_usage_stats AS
SELECT 
    DATE_TRUNC('day', last_used) as usage_date,
    COUNT(*) as files_accessed,
    SUM(file_size) as total_bytes_served,
    COUNT(DISTINCT voice_id) as unique_voices_used
FROM audio_cache 
WHERE last_used > NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', last_used)
ORDER BY usage_date DESC;

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

-- Create application roles
CREATE ROLE portfolio_app;
CREATE ROLE portfolio_admin;

-- Grant basic permissions to application role
GRANT SELECT, INSERT, UPDATE ON notes TO portfolio_app;
GRANT SELECT, INSERT ON reviews TO portfolio_app;
GRANT SELECT, INSERT ON contact_submissions TO portfolio_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON audio_cache TO portfolio_app;
GRANT SELECT, INSERT ON custom_audio TO portfolio_app;

-- Grant full permissions to admin role
GRANT ALL ON ALL TABLES IN SCHEMA public TO portfolio_admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO portfolio_admin;

-- =============================================================================
-- FINAL SETUP VERIFICATION
-- =============================================================================

-- Verify all tables were created successfully
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE';
    
    IF table_count >= 6 THEN
        RAISE NOTICE '✅ Database schema created successfully! % tables found.', table_count;
    ELSE
        RAISE EXCEPTION '❌ Database schema creation failed! Only % tables found.', table_count;
    END IF;
END $$;

-- Display summary
SELECT 
    schemaname,
    tablename,
    tableowner,
    tablespace
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- =============================================================================
-- USAGE EXAMPLES
-- =============================================================================

/*
-- Example queries for testing:

-- Check cache for specific text
SELECT * FROM audio_cache WHERE text_hash = MD5('hello world-default-{}');

-- Get all active custom audio for a note
SELECT * FROM custom_audio WHERE note_id = 1 AND is_active = true;

-- Get cache statistics
SELECT * FROM get_cache_stats();

-- Clean up old cache entries (older than 30 days)
SELECT cleanup_old_cache(30);

-- Get recent contact submissions
SELECT * FROM contact_submissions ORDER BY submitted_at DESC LIMIT 10;

-- Get approved reviews
SELECT name, rating, comment FROM reviews WHERE is_approved = true;
*/

COMMIT;
