import requests
import json
import time

from requests.exceptions import HTTPError
from flytekit import task, workflow


DOMINO_API_HOST = "https://pipe-research.train-sandbox.domino.tech"
DOMINO_PROJECT_ID = "6578bbe3162ea841ff16cf89"
DOMINO_USER_API_KEY = "465e795295fa43b52dd80042ada9e813d287adf07531ffad306aee1a4b3aaf64"
SAS_ENVIRONMENT_ID = "657b1d33162ea841ff16d31e"


@task
def ADSL() -> str:
    return execute_task("prod/adam/ADSL.sas")


@task
def ADAE() -> str:
    return execute_task("prod/adam/ADAE.sas")


@task
def ADCM() -> str:
    return execute_task("prod/adam/ADCM.sas")


@task
def ADLB() -> str:
    return execute_task("prod/adam/ADLB.sas")


@task
def ADMH() -> str:
    return execute_task("prod/adam/ADMH.sas")


@task
def ADVS() -> str:
    return execute_task("prod/adam/ADVS.sas")


@task
def t_vscat() -> str:
    return execute_task("prod/tfl/t_vscat.sas")


@task
def qc_ADSL() -> str:
    return execute_task("qc/adam/qc_ADSL.sas")


@task
def qc_ADAE() -> str:
    return execute_task("qc/adam/qc_ADAE.sas")


@task
def qc_ADCM() -> str:
    return execute_task("qc/adam/qc_ADCM.sas")


@task
def qc_ADMH() -> str:
    return execute_task("qc/adam/qc_ADMH.sas")


@task
def qc_ADVS() -> str:
    return execute_task("qc/adam/qc_ADVS.sas")


@workflow
def gsk() -> None:
    adsl_promise = ADSL()
    adae_promise = ADAE()
    adcm_promise = ADCM()
    adlb_promise = ADLB()
    admh_promise = ADMH()
    advs_promise = ADVS()
    t_vscat_promise = t_vscat()
    qc_adsl_promise = qc_ADSL()
    qc_adae_promise = qc_ADAE()
    qc_adcm_promise = qc_ADCM()
    qc_admh_promise = qc_ADMH()
    qc_advs_promise = qc_ADVS()

    adsl_promise >> adae_promise
    adsl_promise >> adcm_promise
    adsl_promise >> adlb_promise
    adsl_promise >> admh_promise
    adsl_promise >> advs_promise
    advs_promise >> t_vscat_promise
    adsl_promise >> qc_adsl_promise
    adae_promise >> qc_adae_promise
    adcm_promise >> qc_adcm_promise
    admh_promise >> qc_admh_promise
    advs_promise >> qc_advs_promise
    qc_adsl_promise >> qc_adae_promise
    qc_adsl_promise >> qc_adcm_promise
    qc_adsl_promise >> qc_admh_promise
    qc_adsl_promise >> qc_advs_promise


def execute_task(command):
    job_info = submit_task(command)
    job_id = job_info['job']['id']
    job_status = wait_for_job_completion(job_id)

    return job_status


def submit_task(command):
    method = 'POST'
    endpoint = 'api/jobs/v1/jobs'
    request_body = {}
    request_body['environmentId'] = SAS_ENVIRONMENT_ID
    request_body['projectId'] = DOMINO_PROJECT_ID
    request_body['runCommand'] = command

    job_info = submit_api_call(method, endpoint, data=json.dumps(request_body))
    print(job_info)

    return job_info


def wait_for_job_completion(job_id):
    while True:
        job_status = get_job_status(job_id)
        if job_status in ("Succeeded", "Stopped", "Failed", "Error"):
            return job_status;
        time.sleep(1)


def get_job_status(job_id):
    method = 'GET'
    endpoint = f'api/jobs/beta/jobs/{job_id}'
    job_info = submit_api_call(method, endpoint)
    job_status = job_info['job']['status']['executionStatus']
    print(f"Job id {job_id} status is: {job_status}")

    return job_status


def submit_api_call(method, endpoint, data=None):
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json',
        'X-Domino-Api-Key': DOMINO_USER_API_KEY,
    }
    url = f'{DOMINO_API_HOST}/{endpoint}'

    try:
        response = requests.request(method, url, headers=headers, data=data)
        response.raise_for_status()
    except HTTPError as err:
        print(err)
        if data:
            print(f'Request Body: {data}')
        print(f'Request Response: {response.text}')
        exit(1)

    # Some API responses have JSON bodies, some are empty
    try:
        return response.json()
    except:
        try:
            return response.text
        except:
            return response

