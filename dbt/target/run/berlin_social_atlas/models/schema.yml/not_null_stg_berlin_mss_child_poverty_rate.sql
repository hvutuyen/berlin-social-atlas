
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select child_poverty_rate
from "airflow"."staging"."stg_berlin_mss"
where child_poverty_rate is null



  
  
      
    ) dbt_internal_test