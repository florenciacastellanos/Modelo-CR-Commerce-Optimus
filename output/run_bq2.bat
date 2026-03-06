@echo off
SET CLOUDSDK_PYTHON=C:\Users\flocastellanos\AppData\Local\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe
"C:\Users\flocastellanos\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd" query --use_legacy_sql=false --format=csv < "C:\Users\flocastellanos\Modelo-CR-Commerce-Optimus\output\query_cdu_reputacion.sql" > "C:\Users\flocastellanos\Modelo-CR-Commerce-Optimus\output\result_reputacion.csv" 2>&1
echo Exit code: %ERRORLEVEL%
