
            -- Reset token usage for all AI types
            UPDATE token_usage 
            SET 
                tokens_in = 0,
                tokens_out = 0,
                total_tokens = 0,
                request_count = 0,
                usage_percentage = 0.0,
                status = 'active'
            WHERE month_year = TO_CHAR(CURRENT_DATE, 'YYYY-MM');
            
            -- Reset token usage logs
            DELETE FROM token_usage_logs 
            WHERE month_year = TO_CHAR(CURRENT_DATE, 'YYYY-MM');
            
            -- Update agent metrics to reset learning scores
            UPDATE agent_metrics 
            SET 
                learning_score = 0.0,
                success_rate = 0.0,
                failure_rate = 0.0,
                status = 'idle'
            WHERE agent_type IN ('imperium', 'guardian', 'sandbox', 'conquest');
            