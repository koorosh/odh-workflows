import pytest
from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.models import DagBag, Connection
from pytest_mock import MockerFixture

from dags.download_organizations import get_last_update_info, dag


def test_get_last_update_info(test_dag: DAG, mocker: MockerFixture):
    mocker.patch.object(
        BaseHook,
        "get_connection",
        return_value=Connection(schema="https", host="data.gov.ua"),
    )
    get_last_update_info.dag = test_dag
    test_dag.add_task(get_last_update_info)
    result = get_last_update_info.execute(context={})

    # pytest.helpers.run_task

    # task = BashOperator(task_id="test", bash_command=f"echo 'hello' > {tmpfile}", dag=test_dag)
    # pytest.helpers.run_task(task=get_last_update_info, dag=test_dag)
    #
    assert result == "helo"
    # assert tmpfile.read().replace("\n", "") == "hello"