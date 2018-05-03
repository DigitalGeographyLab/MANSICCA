CREATE TEMPORARY TABLE
    export_media
AS
    SELECT
        id
    FROM
        media
    WHERE id IN
        (
            SELECT
                unnest(media)
            FROM
                tweets_rhino
        )
    AND id IN
        (
            SELECT
                mediaId
            FROM
                tweets_rhino_media_predictions
            WHERE
                prediction_label = 'rhino'
        );

ALTER TABLE
    export_media
ADD COLUMN
    pkey SERIAL PRIMARY KEY;

CREATE TEMPORARY TABLE
    export_sample
AS
    SELECT DISTINCT ON (m.origin_url)
        r.id,
        r.text AS caption,
        m.origin_url
    FROM
        media m
        INNER JOIN
            tweets_rhino r
            ON(m.id = ANY(r.media))
    WHERE
        m.id IN
            (
                SELECT
                    id
                FROM
                    export_media
                WHERE
                    pkey IN (
                        SELECT
				                distinct pkey as pkey
			                FROM
				                (
					                SELECT
						                trunc(random() * r.range + r.minimum)::INT AS pkey
					                FROM
						                (
							                SELECT
							                    min(pkey) AS minimum,
							                    (max(pkey) - min(pkey)) AS range
							                FROM
							                    export_media
					                    ) r
					                CROSS JOIN
					                    (
					                        SELECT
					                            generate_series(1,1000000)
					                    ) s
		                        ) random_pkeys
		                    LIMIT 5000
		                )
            )
    ORDER BY m.origin_url;


\COPY export_sample TO '/tmp/export_sample.csv' CSV HEADER;
