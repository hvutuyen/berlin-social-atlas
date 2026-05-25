
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select social_burden_index
from "airflow"."staging"."mart_district_social_index"
where social_burden_index is null



  
  
      
    ) dbt_internal_test