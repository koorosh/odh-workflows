import json
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import ShortCircuitOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'koorosh',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

dag = DAG(
    'edrpou',
    default_args=default_args,
    description='Get FOP and OU organizations from data.gov.ua',
    schedule_interval=None
)

# link to get resource information (JSON)
# https://data.gov.ua/api/3/action/package_show?id=1c7f3815-3259-45e0-bdf1-64dca07ddc10
# TODO: extract to airflow vars
registry_id = '1c7f3815-3259-45e0-bdf1-64dca07ddc10'
dataset_id = '266bfef3-6d69-4e17-9f69-a5edf7db6ad2'  # "17-ufop_full_01.03.2021"

"""
`metadata_url_id` refers to website host (https://data.gov.ua)  
"""
get_last_update_info = SimpleHttpOperator(
    task_id='get_last_update_info',
    method='GET',
    http_conn_id='DATA_GOV_UA_URL',
    endpoint='/api/3/action/package_show?id=' + registry_id,
    response_filter=lambda r: r.json()['result']['resources'],
    log_response=True,
    dag=dag,
)


def get_ds_url_if_new_fn(**context):
    ds_meta = context['ti'].xcom_pull(task_ids='get_last_update_info')
    ds = next(x for x in ds_meta if x['id'] == dataset_id)
    ds_date = datetime.fromisoformat(ds['last_modified']).date()
    ds_download_url = ds['url']
    # test if resource creation date is earlier than yesterday
    if ds_date < (datetime.today() - timedelta(days=1)).date():
        context['ti'].xcom_push(key='ds_url', value=ds_download_url)
        return True
    return False


get_ds_url_if_new = ShortCircuitOperator(
    task_id='get_ds_url_if_new',
    python_callable=get_ds_url_if_new_fn,
    dag=dag,
)

"""
download archive, unzip it, and return path to the directory with unzipped files
"""
download_ds_archive = BashOperator(
    task_id='download_ds_archive',
    bash_command="""
    dest_path=/shared/{{ task.task_id }}/{{ ti.job_id }}
    archive_path=$dest_path/ds.zip
    unzipped_dir=$dest_path/files
    curl --retry 10 -C - {{ task_instance.xcom_pull(task_ids='get_ds_url_if_new', key='ds_url') }} --create-dirs -o $archive_path
    unzip -j -q $archive_path -d $unzipped_dir
    echo $unzipped_dir
    """,
    dag=dag,
)

# Original XML files have been detected with wrong encoding and has to be converted to UTF-8 encoding
conv_to_utf = BashOperator(
    task_id='conv_to_utf',
    bash_command="""
    # get the directory path with unzipped XML files
    src_dir={{ ti.xcom_pull(task_ids="download_ds_archive", key="return_value") }}
    out_dir="${src_dir}/encoded"
    mkdir -p $out_dir
    # iterate over files and convert them to UTF8
    # 17 - is first chars for filenames from archive
    for in_file in $(ls $src_dir | grep 17) 
    do 
       iconv -f windows-1251 -t utf-8 "${src_dir}/${in_file}" > "${out_dir}/${in_file}"
    done
    echo $out_dir
    """,
    dag=dag,
)

# TODO: upload encoded files to azure file storage
# TODO: clean up local storage
# TODO: attach NSF to docker containers and use it instead of local shared volume


get_last_update_info >> get_ds_url_if_new >> download_ds_archive >> conv_to_utf
