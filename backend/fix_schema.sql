-- Fix Supabase schema - Add missing array columns
ALTER TABLE templates ADD COLUMN IF NOT EXISTS categories text[] DEFAULT '{}';
ALTER TABLE templates ADD COLUMN IF NOT EXISTS tools text[] DEFAULT '{}';

-- Update existing templates with sample data to test
UPDATE templates SET 
    categories = '{"marketing", "produtividade"}',
    tools = '{"make", "gmail"}'
WHERE slug = 'automacao-email-marketing';

UPDATE templates SET 
    categories = '{"vendas", "atendimento"}',
    tools = '{"openai", "slack"}'
WHERE slug = 'chatbot-vendas-ia';

-- Create RPC function for distinct platforms (for facets)
CREATE OR REPLACE FUNCTION get_distinct_platforms()
RETURNS TABLE(platform text) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT t.platform
    FROM templates t
    WHERE t.status = 'published'
    ORDER BY t.platform;
END;
$$ LANGUAGE plpgsql;