-- select a random 5000 row sample
CREATE TABLE instagram_southafrica_5000 AS 
    SELECT * 
    FROM instagram_southafrica
    WHERE 
        photo <> ''
    AND
        photo <> '[none]' 
    AND
        pkey in
            (SELECT pkey
                FROM
                    (SELECT 
                        trunc(random()*r.range + r.minimum)::int AS pkey 
                    FROM
                        (SELECT 
                            min(pkey) AS minimum, 
                            (max(pkey) - min(pkey)) AS range 
                        FROM instagram_southafrica) r 
                    CROSS JOIN 
                        (SELECT generate_series(1,100000)) s
                    ) random_pkeys
                JOIN
                    instagram_southafrica i USING(pkey)
            )
    LIMIT 5000;

-- recreate indices, add indices for -sentiment, -ambiguity, -annotater    
CREATE INDEX ON instagram_southafrica_5000 using btree(id);
CREATE INDEX ON instagram_southafrica_5000 using btree(pkey);
CREATE INDEX ON instagram_southafrica_5000 using gin(sentiment);
CREATE INDEX ON instagram_southafrica_5000 using gin(ambiguous);
CREATE INDEX ON instagram_southafrica_5000 using gin(annotater);
CREATE INDEX ON instagram_southafrica_5000 using gin(token);

-- fill in defaults for -sentiment, -ambigous, -annotater
update instagram_southafrica_5000 set sentiment = ARRAY[]::sentiment[];
update instagram_southafrica_5000 set ambiguous = ARRAY[]::boolean[];
update instagram_southafrica_5000 set annotater = ARRAY[]::text[];
update instagram_southafrica_5000 set token = ARRAY[]::text[];
