# Airflow with docker
 **Step1 : Install Airflow with docker-compose**
 ```
 Create Airflow folder inside Ubuntu Environment
 With the given docker-compose file and .env file, install Airflow with dependencies in docker. 

 docker-compose up -d 
```

```
The given docker-compose file install airflow with celery executor and redis as Queue **
 It also installs postgres on port 5432
 It will create 3 folders 1. dags, 2. logs and 3. plugins in airflow folder .

 Change the permission of Airflow folder from outside directory in Ubuntu using below command:

sudo chmod -R 777 airflow
```

 **Step2:  Access Airflow Webserver UI built using Flask**
 ```
 localhost:8080
 user name : airflow
 pwd : airflow
 check DAG examples try to run one of them . see grid view , gantt view, code, logs etc. in UI
 ```

 **Step3: Define DAGs , Taks, operators**
 ```
 Save user_processing.py file inside your "dags" folder. UI will process new file every 5 mins by default.
 Go to UI , refresh it . Check if it displays any errors at top on UI. Expand on arrow to see the error. go To code and correct it. 
``` 
**step4: Define Connection in Airflow UI**
```
Go to Airflow UI ==> Click on Admin in Top Menu==> connections==> Add Connection
connection name : postgres
connection type: Postgres (select from drop down)
host : postgres
login : airflow
pwd : airflow
port : 5432
Test the connection save the connection
```
**step5 : Run the DAG file**
```
Go to Ubuntu terminal . run the coammand 

 docker ps

copy the docker container name of airflow scheduler <airflow-airflow-scheduler-1 >
Run the following command :

docker exec -it <airflow scheduler container name> bash
```
**step6: Execute the following command to run your Task**
```
airflow tasks test <DAG id> <Task id> <any date in past ex: 2023-01-01>
```

Successfull task will display this msg :

```
INFO - Marking task as SUCCESS. dag_id=user_processing, task_id=create_table, execution_date=20230101T000000, start_date=, end_date=20230825T085252

```







