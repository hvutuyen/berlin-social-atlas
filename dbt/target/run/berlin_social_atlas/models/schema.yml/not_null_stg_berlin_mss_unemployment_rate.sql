
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select unemployment_rate
from "airflow"."staging"."stg_berlin_mss"
where unemployment_rate is null



  
  
      
    ) dbt_internal_test