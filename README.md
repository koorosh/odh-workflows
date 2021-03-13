# odh-workflows

### How to setup local dev environment
- install `python 3.8` with `pyenv`
  ```shell
  pyenv install -v 3.8.2
  ```
- install `pip` and `virtualenv venv`
    ```shell
    python3 -m pip install --user --upgrade pip
    python3 -m pip install --user virtualenv
    ```
- create virtual env inside of `<project>/venv` dir and activate environment
    ```shell
    # specify your own path 
    virtualenv -p ~/.pyenv/versions/3.8.2/bin/python3 venv
    source ./env/bin/activate
    ```
- install local dependencies
    ```shell
    pip install --trusted-host pypi.python.org "apache-airflow[postgres,apache.spark,microsoft.azure,ssh]==2.0.1" --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.0.1/constraints-3.8.txt
    pip install -r airflow.requirements.txt -r local.requirements.txt
    ```

### How to deactivate python env
  ```shell
  deactivate
  ```

### How to deploy to production (TBD)