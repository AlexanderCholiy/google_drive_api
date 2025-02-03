def add_poles_for_claims_and_messages(
    constant_type: int, claim_number: str, constant_text: str
) -> str:
    return (f'''
    INSERT INTO constants (
        claim_id, constant_type, constant_text, time_stamp
    )
    SELECT DISTINCT
        cl.id, {constant_type}, ts.ts_id, CURRENT_DATE
    FROM claims AS cl
    JOIN towerstore AS ts ON ts.ts_id = '{constant_text}'
    WHERE
        cl.claim_number = '{claim_number}'
        AND NOT EXISTS (
            SELECT 1
            FROM constants
            WHERE
                claim_id = cl.id
                AND constant_type = {constant_type}
        );

    INSERT INTO messages_constants (
        message_id, constant_type, constant_text, time_stamp
    )
    SELECT DISTINCT
        ms.message_id, {constant_type}, ts.ts_id, CURRENT_DATE
    FROM messages_constants AS ms
    JOIN towerstore AS ts ON ts.ts_id = '{constant_text}'
    WHERE
        ms.constant_text = '{claim_number}'
        AND NOT EXISTS (
            SELECT 1
            FROM messages_constants
            WHERE
                message_id = ms.message_id
                AND constant_type = {constant_type}
        );
    ''')
