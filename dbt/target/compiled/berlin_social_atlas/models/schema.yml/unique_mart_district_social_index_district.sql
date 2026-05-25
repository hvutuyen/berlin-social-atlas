
    
    

select
    district as unique_field,
    count(*) as n_records

from "airflow"."staging"."mart_district_social_index"
where district is not null
group by district
having count(*) > 1


