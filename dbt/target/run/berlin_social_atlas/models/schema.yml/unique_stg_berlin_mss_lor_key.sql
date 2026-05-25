
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    lor_key as unique_field,
    count(*) as n_records

from "airflow"."staging"."stg_berlin_mss"
where lor_key is not null
group by lor_key
having count(*) > 1



  
  
      
    ) dbt_internal_test