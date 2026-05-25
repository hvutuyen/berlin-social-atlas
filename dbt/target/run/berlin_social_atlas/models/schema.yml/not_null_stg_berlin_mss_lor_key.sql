
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select lor_key
from "airflow"."staging"."stg_berlin_mss"
where lor_key is null



  
  
      
    ) dbt_internal_test