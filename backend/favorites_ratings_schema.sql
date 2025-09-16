-- Add favorites and ratings functionality to FlowLib

-- Create favorites table
CREATE TABLE IF NOT EXISTS favorites (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL, -- For now, we'll use session/email as user identifier
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, template_id)
);

-- Create ratings table  
CREATE TABLE IF NOT EXISTS ratings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL, -- For now, we'll use session/email as user identifier  
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, template_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_template_id ON favorites(template_id);
CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_template_id ON ratings(template_id);

-- Create function to update template rating_avg when ratings change
CREATE OR REPLACE FUNCTION update_template_rating_avg()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the rating_avg for the affected template
    UPDATE templates 
    SET rating_avg = (
        SELECT ROUND(AVG(rating)::numeric, 1)
        FROM ratings 
        WHERE template_id = COALESCE(NEW.template_id, OLD.template_id)
    )
    WHERE id = COALESCE(NEW.template_id, OLD.template_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Create triggers to auto-update rating_avg
DROP TRIGGER IF EXISTS trigger_update_rating_avg_insert ON ratings;
DROP TRIGGER IF EXISTS trigger_update_rating_avg_update ON ratings;  
DROP TRIGGER IF EXISTS trigger_update_rating_avg_delete ON ratings;

CREATE TRIGGER trigger_update_rating_avg_insert
    AFTER INSERT ON ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_template_rating_avg();

CREATE TRIGGER trigger_update_rating_avg_update
    AFTER UPDATE ON ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_template_rating_avg();

CREATE TRIGGER trigger_update_rating_avg_delete
    AFTER DELETE ON ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_template_rating_avg();