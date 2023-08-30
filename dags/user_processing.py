from airflow import DAG
from datetime import datetime
from airflow.operators.python_operator import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from pandas import json_normalize
from airflow.providers.postgres.hooks.postgres import PostgresHook
import json

def _process_user(**kwargs):
    ti = kwargs['ti']
    user = ti.xcom_pull(task_ids='extract_users')
    a = f"hello_{user}"
    print(a)
    user = user['results'][0]
    processed_user = json_normalize({
        'firstname': user['name']['first'],
        'lastname': user['name']['last'],
        'country': user['location']['country'],
        'username': user['login']['username'],
        'password': user['login']['password'],
        'email': user['email'] })
    processed_user.to_csv('/tmp/processed_user.csv', index=False, header=False)


def _store_user():

    hook = PostgresHook(postgres_conn_id = 'postgres')

    '''
    The copy_expert method of the PostgresHook in Apache Airflow is used to efficiently copy 
    data from a file-like object (such as a CSV file) to a PostgreSQL table using 
    the PostgreSQL COPY command. The COPY command is a high-performance way to load data 
    into a PostgreSQL table from a file, and the copy_expert method provides a convenient way to utilize this feature.
    '''
    hook.copy_expert(
        sql="COPY users FROM stdin WITH DELIMITER as ','",
        filename='/tmp/processed_user.csv'
    )


#Task1: Action Operator

with DAG('user_processing', start_date = datetime(2023,8,25),schedule_interval = '@daily', catchup = False, tags=["postgres"]) as dag:
    create_table = PostgresOperator(task_id = 'create_table',postgres_conn_id = 'postgres', 
                                    sql = '''
                                            CREATE TABLE IF NOT EXISTS users (
                                                firstname TEXT NOT NULL,
                                                lastname TEXT NOT NULL,
                                                country TEXT NOT NULL,
                                                username TEXT NOT NULL,
                                                password TEXT NOT NULL,
                                                email TEXT NOT NULL
                                            
                                            );
                                        '''
    )

# Task 2: Sensor Operator(HTTPSensor : to wait for valid API point)
# https://airflow.apache.org/docs/apache-airflow-providers-http/stable/_api/airflow/providers/http/sensors/http/index.html

    is_api_available = HttpSensor(task_id = 'is_api_available', 
                                http_conn_id = 'user_api',
                                endpoint = 'api/'
                                )

    extract_users = SimpleHttpOperator(
        task_id='extract_users',
        method='GET',
        http_conn_id='user_api',  # Create an HTTP connection in Airflow with API credentials
        endpoint='api/',
        response_filter=lambda response: json.loads(response.text),
        log_response = True
    )

    process_user = PythonOperator(task_id = 'process_user',
                                python_callable = _process_user,
                                provide_context=True
                                )

    store_user = PythonOperator(task_id = 'store_user',
                                python_callable = _store_user
                                )

    create_table >> is_api_available >>  extract_users >>   process_user  >>  store_user