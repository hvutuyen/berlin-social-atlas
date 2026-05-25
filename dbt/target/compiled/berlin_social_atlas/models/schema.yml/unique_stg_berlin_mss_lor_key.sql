
    
    

select
    lor_key as unique_field,
    count(*) as n_records

from "airflow"."staging"."stg_berlin_mss"
where lor_key is not null
group by lor_key
having count(*) > 1


