-- Create a dataset and analytics table using the synthetic CSV.
CREATE SCHEMA IF NOT EXISTS `YOUR_PROJECT.resolveiq`
OPTIONS(location='US');

CREATE OR REPLACE TABLE `YOUR_PROJECT.resolveiq.incidents` (
  incident_id STRING,
  service STRING,
  priority STRING,
  category STRING,
  status STRING,
  age_hours FLOAT64,
  sla_hours FLOAT64,
  customer_impact INT64,
  repeat_count INT64
);
