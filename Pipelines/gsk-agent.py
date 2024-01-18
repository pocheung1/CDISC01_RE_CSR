# pyflyte run --remote --project flytesnacks --domain staging Pipelines/gsk-agent.py gsk

import requests
import json
import time

from requests.exceptions import HTTPError
from flytekit import task, workflow
from domino.flyte.task import DominoJobConfig, DominoJobTask

DOMINO_API_HOST = "https://pipe-research.train-sandbox.domino.tech"
DOMINO_PROJECT = "CDISC01_RE_CSR"
DOMINO_PROJECT_ID = "6578bbe3162ea841ff16cf89"
DOMINO_USER_API_KEY = "465e795295fa43b52dd80042ada9e813d287adf07531ffad306aee1a4b3aaf64"
SAS_ENVIRONMENT_ID = "657b1d33162ea841ff16d31e"


def ADSL() -> str:
    return execute_task("prod/adam/ADSL.sas")


def ADAE() -> str:
    return execute_task("prod/adam/ADAE.sas")


def ADCM() -> str:
    return execute_task("prod/adam/ADCM.sas")


def ADLB() -> str:
    return execute_task("prod/adam/ADLB.sas")


def ADMH() -> str:
    return execute_task("prod/adam/ADMH.sas")


def ADVS() -> str:
    return execute_task("prod/adam/ADVS.sas")


def t_vscat() -> str:
    return execute_task("prod/tfl/t_vscat.sas")


def qc_ADSL() -> str:
    return execute_task("qc/adam/qc_ADSL.sas")


def qc_ADAE() -> str:
    return execute_task("qc/adam/qc_ADAE.sas")


def qc_ADCM() -> str:
    return execute_task("qc/adam/qc_ADCM.sas")


def qc_ADMH() -> str:
    return execute_task("qc/adam/qc_ADMH.sas")


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
    job_config = DominoJobConfig(
        Username="integration-test",
        ProjectName=DOMINO_PROJECT,
        EnvironmentId=SAS_ENVIRONMENT_ID,
        ApiKey=DOMINO_USER_API_KEY,
        Command=command,
        Title=command,
    )

    job = DominoJobTask(
        name=command,
        task_config=job_config,
    )

    return job()
