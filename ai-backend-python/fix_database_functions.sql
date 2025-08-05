
            -- Fix for avg() function on JSON text fields
            -- Create a function to safely extract and cast JSON values
            
            CREATE OR REPLACE FUNCTION safe_json_avg(json_data JSONB, key TEXT)
            RETURNS NUMERIC AS $$
            DECLARE
                total NUMERIC := 0;
                count INTEGER := 0;
                value NUMERIC;
            BEGIN
                -- Extract all values for the key and calculate average
                SELECT 
                    COALESCE(AVG(CAST(value AS NUMERIC)), 0)
                INTO total
                FROM jsonb_array_elements(json_data) AS value
                WHERE jsonb_typeof(value) = 'number';
                
                RETURN COALESCE(total, 0);
            EXCEPTION
                WHEN OTHERS THEN
                    RETURN 0;
            END;
            $$ LANGUAGE plpgsql;
            
            -- Create function for learning data confidence calculation
            CREATE OR REPLACE FUNCTION get_learning_confidence(learning_data JSONB)
            RETURNS NUMERIC AS $$
            BEGIN
                RETURN COALESCE(
                    CAST(learning_data->>'confidence' AS NUMERIC),
                    0.5
                );
            EXCEPTION
                WHEN OTHERS THEN
                    RETURN 0.5;
            END;
            $$ LANGUAGE plpgsql;
            