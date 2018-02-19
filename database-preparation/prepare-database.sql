-- create postgis extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- create type for sentiment, plus index functions for arrays of sentiment
-- cf. http://adpgtech.blogspot.fi/2016/03/gin-indexing-array-of-enums.html
CREATE TYPE sentiment AS ENUM('positive', 'neutral', 'negative');
CREATE OPERATOR CLASS _sentiment_ops 
    default for type public.sentiment[] 
    using gin 
    family array_ops as  
        function 1 enum_cmp(anyenum,anyenum), 
        function 2 pg_catalog.ginarrayextract(anyarray, internal), 
        function 3 ginqueryarrayextract(anyarray, internal, smallint, internal, internal, internal, internal), 
        function 4 ginarrayconsistent(internal, smallint, anyarray, integer, internal, internal, internal, internal),
        function 6 ginarraytriconsistent(internal, smallint, anyarray, integer, internal, internal, internal), 
    storage oid ;
