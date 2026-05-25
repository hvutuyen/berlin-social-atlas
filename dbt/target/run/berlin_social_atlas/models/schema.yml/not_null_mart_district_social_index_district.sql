
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select district
from "airflow"."staging"."mart_district_social_index"
where district is null



  
  
      
    ) dbt_internal_test