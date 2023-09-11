from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
 
from datetime import datetime
 
def _t1():
    return 42
 
def _t2(**context):
    key = 'this_is_the_key'
    value = 't2 is the value'
    context['ti'].xcom_push(key = key, value = value)

def _t3(**context):
    key = 'this_is_the_key'
    data = context['ti'].xcom_pull(task_ids = 't2',key = key)
    print("Retrieved data with key:", data)

 
with DAG("xcom_dag", start_date=datetime(2022, 1, 1), 
    schedule_interval='@daily', catchup=False) as dag:
 
    t1 = PythonOperator(
        task_id='t1',
        python_callable=_t1
    )
 
    t2 = PythonOperator(
        task_id='t2',
        python_callable=_t2
    )

    t3 = PythonOperator(
        task_id='t3',
        python_callable=_t3
    )
 
    t4 = BashOperator(
        task_id='t4',
        bash_command="echo ''"
    )
 
    t1 >> t2 >> t3 >> t4