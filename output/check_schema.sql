SELECT column_name, data_type
FROM `meli-bi-data`.WHOWNER.INFORMATION_SCHEMA.COLUMNS
WHERE table_name = 'BT_ORD_ORDERS'
AND column_name LIKE '%SELLER%'
LIMIT 20
