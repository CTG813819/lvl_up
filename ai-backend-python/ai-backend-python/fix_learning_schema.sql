-- Fix Learning Schema Mismatch
-- =============================
-- This SQL script fixes the database schema mismatch between the old and new Learning table schemas.
-- Run this script directly on your PostgreSQL database.

-- Step 1: Add learning_data column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'learning' 
        AND column_name = 'learning_data'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE learning ADD COLUMN learning_data JSONB;
        RAISE NOTICE 'Added learning_data column to learning table';
    ELSE
        RAISE NOTICE 'learning_data column already exists in learning table';
    END IF;
END $$;

-- Step 2: Migrate existing data to learning_data
DO $$
DECLARE
    record RECORD;
    learning_data JSONB;
BEGIN
    -- Check if we have old schema data to migrate
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'learning' 
        AND column_name = 'pattern'
        AND table_schema = 'public'
    ) THEN
        -- Migrate existing records
        FOR record IN 
            SELECT id, ai_type, learning_type, pattern, context, feedback, 
                   confidence, applied_count, success_rate, status, created_at, updated_at
            FROM learning
            WHERE learning_data IS NULL
        LOOP
            -- Create learning_data JSON from old columns
            learning_data := jsonb_build_object(
                'pattern', record.pattern,
                'context', record.context,
                'feedback', record.feedback,
                'confidence', COALESCE(record.confidence, 0.5),
                'applied_count', COALESCE(record.applied_count, 0),
                'success_rate', COALESCE(record.success_rate, 0.0),
                'migrated_from_old_schema', true,
                'migration_timestamp', now()::text
            );
            
            -- Update the record with learning_data
            UPDATE learning 
            SET learning_data = learning_data
            WHERE id = record.id;
        END LOOP;
        
        RAISE NOTICE 'Migrated existing data to learning_data column';
    ELSE
        RAISE NOTICE 'No old schema data found to migrate';
    END IF;
END $$;

-- Step 3: Make old columns nullable (since data is now in learning_data)
DO $$ 
BEGIN
    -- Make pattern column nullable if it exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'learning' 
        AND column_name = 'pattern'
        AND table_schema = 'public'
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE learning ALTER COLUMN pattern DROP NOT NULL;
        RAISE NOTICE 'Made pattern column nullable';
    END IF;
    
    -- Make context column nullable if it exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'learning' 
        AND column_name = 'context'
        AND table_schema = 'public'
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE learning ALTER COLUMN context DROP NOT NULL;
        RAISE NOTICE 'Made context column nullable';
    END IF;
END $$;

-- Step 4: Create index on learning_data if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'learning' 
        AND indexname = 'idx_learning_learning_data'
    ) THEN
        CREATE INDEX idx_learning_learning_data ON learning USING GIN (learning_data);
        RAISE NOTICE 'Created GIN index on learning_data column';
    ELSE
        RAISE NOTICE 'Index on learning_data column already exists';
    END IF;
END $$;

-- Step 5: Verify the migration
DO $$
DECLARE
    test_data JSONB;
    test_id UUID;
BEGIN
    -- Test inserting a record with the new schema
    test_data := jsonb_build_object(
        'pattern', 'test_pattern',
        'context', 'test_context',
        'feedback', 'test_feedback',
        'confidence', 0.8,
        'applied_count', 1,
        'success_rate', 1.0
    );
    
    INSERT INTO learning (ai_type, learning_type, learning_data, status)
    VALUES ('test', 'test_type', test_data, 'active')
    RETURNING id INTO test_id;
    
    RAISE NOTICE 'Test insert successful with ID: %', test_id;
    
    -- Clean up test record
    DELETE FROM learning WHERE id = test_id;
    
    RAISE NOTICE 'Schema migration completed successfully!';
END $$;

-- Show final table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'learning' 
AND table_schema = 'public'
ORDER BY ordinal_position; 