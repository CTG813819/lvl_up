CREATE OR REPLACE FUNCTION json_extract_path_text(json_data jsonb, path text)
RETURNS text AS $$
BEGIN
    RETURN json_data #>> string_to_array(path, '.');
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

GRANT EXECUTE ON FUNCTION json_extract_path_text(jsonb, text) TO PUBLIC;
