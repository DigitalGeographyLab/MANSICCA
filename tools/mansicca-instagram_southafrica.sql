
-- connect to other database
SELECT dblink_connect_u('conn1', 'host=localhost dbname=instagram_aws user=chrisfin');

-- copy table (with region selector)
CREATE TABLE instagram_southafrica AS
    SELECT * FROM dblink(
        'conn1',
        'SELECT
            id::bigint AS id, 
            time_utc, 
            text AS caption,
            medialink::text AS url,
            ''''::text AS photo,
            likes,
            regexp_split_to_array('''','';'')::text[] AS comments
        FROM instagram
        WHERE ST_Within(
            geom,
            ST_GeomFromText(
                ''POLYGON((32.79 -25.87,33.79 -26.64,33.34 -28.69,28.08 -33.95,19.68 -35.72,17.47 -34.63,17.17 -31.92,15.33 -28.45,16.72 -27.18,18.88 -27.97,19.34 -24.03,20.68 -24.15,21.65 -25.48,23.04 -24.41,24.87 -24.82,27.56 -22.05,30.85 -21.3,32.08 -21.99,32.79 -25.87))'',
                4326
            )
        );'               
    ) 
    AS instagram_southafrica(
        id bigint, 
        time_utc timestamp, 
        caption text,
        url text,
        photo text, 
        likes int,
        comments text[]
    );    

-- disconnect from other database
SELECT dblink_disconnect('conn1');

-- add primary key (for random selection) + indices
ALTER TABLE instagram_southafrica ADD COLUMN pkey SERIAL PRIMARY KEY;
CREATE INDEX ON instagram_southafrica using btree(pkey);
CREATE INDEX ON instagram_southafrica using btree(id);
    
-- add columns for -sentiment, -ambiguity, -person, lock-token
ALTER TABLE instagram_southafrica ADD COLUMN sentiment sentiment[];
ALTER TABLE instagram_southafrica ADD COLUMN ambiguous boolean[];
ALTER TABLE instagram_southafrica ADD COLUMN annotater text[];
ALTER TABLE instagram_southafrica ADD COLUMN token text[];

\echo 'instagram_southafrica created,';
\echo 'now run download-instagram-images.sh,';
\echo 'then mansicca-instagram_southafrica_5000.sql';
