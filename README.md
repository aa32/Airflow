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

**step 7: Summary of DAG file  user_processing.py**

```
After declaring all the operators, tasks, hooks in user_processing.py file. At the end ofthe file define TASK dependencies like this:
create_table >> is_api_available >>  extract_users >>   process_user  >>  store_user
________________________
TASk1 :create_table:
________________________

This makes use of "PostgresOperator" and creates empty table schema with fields in Postgres using sql "CREATE TABLE" command.
___________________________

TASK 2: is_api_available:
____________________________
It is an HTTPSensor Task, to wait for API endpoint to be available.

___________________________

TASK 3: extract_users:
____________________________
It uses SimpleHTTPOperator to extract users from API endpoint and converts the response into JSON.


TASK 4: process_user:
____________________________
It uses PythonOperator to call python function which pulls user data in JSON format from the extract_users Task output in XCOM .
uses_JSON Normalize to extract fields like first_name, last_name.. etc. and pushes it into csv file.


TASK 5: store_user:
____________________________
It uses PythonOperartor to call Python function which uses Hook (PostgresHook) --> Read more about Hooks in Airflow cheatsheet.

    The copy_expert method of the PostgresHook in Apache Airflow is used to efficiently copy 
    data from a file-like object (such as a CSV file) to a PostgreSQL table using 
    the PostgreSQL COPY command. The COPY command is a high-performance way to load data 
    into a PostgreSQL table from a file, and the copy_expert method provides a convenient way to utilize this feature.
```

**step8: Command to copy config file from docker container location to present working directory**
```
If you have your docker-compose file in "Airflow" directory, go inside that directory run this command to get container names:

docker compose ps

From the output, copy from the result "airflow scheduler" container name and run the following command to "copy" the airflow config file from docker container location to current working directory

docker cp airflow-airflow-scheduler-1:opt/airflow/airflow.cfg .


```

**step 8: To run parallel dags in celery Executor**
```
Create parallel_dag.py file in dags folder. Check the DAG graph for parallel dags. 
Enable Flower in coomand line --> Flower is web based tool for managing, configuring and administering celery clusters.

docker-compose down
docker-compose --profile flower up


To access Flower UI:
got to localhost:5555
```
**To remove the example DAGs**
```
in docker-compose.yml file , Replace the value 'true' by 'false' for the AIRFLOW__CORE__LOAD_EXAMPLES environment variables
restart  the container using following commands:
docker-compose down
docker-compose up -d

Now go to localhost:8080 and we will see only DAGs created by us.
```

**How to add more Workers in Celery?**
```
Go to Docker-compose file . find the <airflow-worker:> 
copy the complete block of configuration for <airflow-worker>

and paste it just below ==> change the name to <airflow-worker-2>

Restart the docker container with 
docker-compose down 
docker-compose up -d

```

**step 9: Create new Queue**
```
Workers run on nodes , some workers run on GPU , some Workers run on 5 core CPU  or some worker might run on single core CPU 
Based on your requirement you can send Tasks which need high processing power to high_cpu Queue and tasks which do not need any specific processing power to "default " queue. If not specified it is default queue.

In docker-compose.yml file, go to newly created worker  configuraion and change command to "celery worker -q <queue_name>"
airflow-worker-2:
    <<: *airflow-common
    command: celery worker -q high_cpu

restart docker-compose
docker-compose down 
docker-compose --profile flower down 

docker-compose up -d
docker-compose --profile flower up
```

**step 10: Direct Tasks to respective queue**
```
Below task_id in Task parameters , include one more parameter < queue = 'high_cpu'>

 transform = BashOperator(
        task_id='transform',
        queue = 'high_cpu',
        bash_command='sleep 1'
    )
 
    extract_a >> load_a
    extract_b >> load_b
    [load_a, load_b] >> transform

```








