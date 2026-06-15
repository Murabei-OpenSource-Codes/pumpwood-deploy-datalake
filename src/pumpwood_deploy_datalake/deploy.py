"""Kubernetes deployment manifests for the Pumpwood Datalake microservice.

This module builds Secret, Deployment, and Service YAML files for
pumpwood-datalake-app and the dataloader worker. Manifests are
registered with ``DeployPumpWood.add_microservice`` from
``pumpwood-deploy``.

Storage bucket and type are read from the cluster ``storage`` ConfigMap
deployed by ``StandardMicroservices``. The cluster must also provide
``general-secrets``, ``rabbitmq-main-secrets``, and storage keys
before datalake pods can start.
"""
import base64
from importlib import resources
from pumpwood_deploy.abc import BasePumpwoodDeployMicroservice
from pumpwood_deploy.type import (
    PumpwoodDeploy, PumpwoodDeploySecret, PumpwoodDeployDeployment)


secrets = resources.files('pumpwood_deploy_datalake')\
    .joinpath('resources/secrets.yml')\
    .read_text(encoding='utf-8')
app_deployment = resources.files('pumpwood_deploy_datalake')\
    .joinpath('resources/deploy__app.yml')\
    .read_text(encoding='utf-8')
worker_deployment = resources.files('pumpwood_deploy_datalake')\
    .joinpath('resources/deploy__worker.yml')\
    .read_text(encoding='utf-8')


class PumpWoodDatalakeMicroservice(BasePumpwoodDeployMicroservice):
    """Deploy Kubernetes manifests for the Pumpwood Datalake microservice.

    Datalake is the core data-storage service for Pumpwood. It defines
    modeling units and exposes APIs for reading and writing structured
    data. The dataloader worker consumes RabbitMQ messages and uploads
    data in parallel chunks to Postgres.

    The deploy class renders three manifests: datalake secrets, the
    application (pumpwood-datalake-app), and the dataloader worker
    (pumpwood-datalake-dataloader-worker).

    Example:
        ```python
        import os
        from pumpwood_deploy.deploy import DeployPumpWood
        from pumpwood_deploy_datalake import PumpWoodDatalakeMicroservice

        deploy.add_microservice(
            PumpWoodDatalakeMicroservice(
                app_version=os.getenv("PUMPWOOD_DATALAKE_APP"),
                worker_version=os.getenv("PUMPWOOD_DATALAKE_WORKER"),
                db_host="pgbouncer-pumpwood-datalake",
                db_database="pumpwood_datalake",
                db_password=secrets["postgres_password"],
                microservice_password=secrets["microservice--datalake"],
            ))
        ```
    """

    def __init__(self,
                 app_version: str,
                 worker_version: str,
                 microservice_password: str = "microservice--datalake",
                 db_username: str = "pumpwood",
                 db_password: str = "pumpwood",
                 db_host: str = "postgres-pumpwood-datalake",
                 db_port: str = "5432",
                 db_database: str = "pumpwood",
                 repository: str = "gcr.io/repositorio-geral-170012",
                 app_debug: str = "FALSE",
                 app_replicas: int = 1,
                 app_timeout: int = 300,
                 app_workers: int = 10,
                 app_limits_memory: str = "60Gi",
                 app_limits_cpu: str = "12000m",
                 app_requests_memory: str = "20Mi",
                 app_requests_cpu: str = "1m",
                 worker_debug: str = "FALSE",
                 worker_replicas: int = 1,
                 worker_n_parallel: int = 4,
                 worker_chunk_size: int = 1000,
                 worker_query_limit: int = 1000000,
                 worker_limits_memory: str = "60Gi",
                 worker_limits_cpu: str = "12000m",
                 worker_requests_memory: str = "20Mi",
                 worker_requests_cpu: str = "1m"):
        """Initialize Pumpwood Datalake deployment configuration.

        Args:
            app_version (str):
                Container image tag for ``pumpwood-datalake-app``.
            worker_version (str):
                Container image tag for
                ``pumpwood-datalake-dataloader-worker``.
            microservice_password (str):
                Password for the ``microservice--datalake`` service
                user. Defaults to ``microservice--datalake``.
            db_username (str):
                Postgres connection username. Defaults to ``pumpwood``.
            db_password (str):
                Postgres connection password. Defaults to ``pumpwood``.
            db_host (str):
                Postgres hostname, usually a PgBouncer service. Defaults
                to ``postgres-pumpwood-datalake``.
            db_port (str):
                Postgres port. Defaults to ``5432``.
            db_database (str):
                Postgres database name. Defaults to ``pumpwood``.
            repository (str):
                Docker registry for app and worker images. Defaults to
                ``gcr.io/repositorio-geral-170012``.
            app_debug (str):
                Debug flag for the application. Accepts ``TRUE`` or
                ``FALSE``. Defaults to ``FALSE``.
            app_replicas (int):
                Number of app pod replicas. Defaults to ``1``.
            app_timeout (int):
                Request timeout in seconds for the app. Defaults to
                ``300``.
            app_workers (int):
                Number of Granian workers for the app. Defaults to
                ``10``.
            app_limits_memory (str):
                Memory limit for app pods. Defaults to ``60Gi``.
            app_limits_cpu (str):
                CPU limit for app pods. Defaults to ``12000m``.
            app_requests_memory (str):
                Memory request for app pods. Defaults to ``20Mi``.
            app_requests_cpu (str):
                CPU request for app pods. Defaults to ``1m``.
            worker_debug (str):
                Debug flag for the dataloader worker. Accepts ``TRUE``
                or ``FALSE``. Defaults to ``FALSE``.
            worker_replicas (int):
                Number of dataloader worker replicas. Defaults to ``1``.
            worker_n_parallel (int):
                Parallel upload requests per worker. Defaults to ``4``.
            worker_chunk_size (int):
                Rows uploaded per parallel request. Defaults to
                ``1000``.
            worker_query_limit (int):
                Maximum rows processed per upload cycle. Defaults to
                ``1000000``.
            worker_limits_memory (str):
                Memory limit for worker pods. Defaults to ``60Gi``.
            worker_limits_cpu (str):
                CPU limit for worker pods. Defaults to ``12000m``.
            worker_requests_memory (str):
                Memory request for worker pods. Defaults to ``20Mi``.
            worker_requests_cpu (str):
                CPU request for worker pods. Defaults to ``1m``.
        """
        self.repository = repository.rstrip("/")

        # Database
        self._db_password = base64.b64encode(db_password.encode()).decode()
        self.db_username = db_username
        self.db_host = db_host
        self.db_port = db_port
        self.db_database = db_database

        # Microservice
        self._microservice_password = base64.b64encode(
            microservice_password.encode()).decode()

        # App
        self.app_version = app_version
        self.app_debug = app_debug
        self.app_replicas = app_replicas
        self.app_timeout = app_timeout
        self.app_workers = app_workers
        self.app_limits_memory = app_limits_memory
        self.app_limits_cpu = app_limits_cpu
        self.app_requests_memory = app_requests_memory
        self.app_requests_cpu = app_requests_cpu

        # Worker
        self.worker_version = worker_version
        self.worker_debug = worker_debug
        self.worker_replicas = worker_replicas
        self.worker_n_parallel = worker_n_parallel
        self.worker_chunk_size = worker_chunk_size
        self.worker_query_limit = worker_query_limit
        self.worker_limits_memory = worker_limits_memory
        self.worker_limits_cpu = worker_limits_cpu
        self.worker_requests_memory = worker_requests_memory
        self.worker_requests_cpu = worker_requests_cpu

    def create_deployment_file(self) -> list[PumpwoodDeploy]:
        """Build Kubernetes manifests for Pumpwood Datalake.

        Returns:
            list[PumpwoodDeploy]:
                Secret ``pumpwood_datalake__secrets``, application
                deploy ``pumpwood_datalake__deploy``, and worker deploy
                ``pumpwood_datalake_dataloader__worker``.
        """
        secrets_text_formated = secrets\
            .format(db_password=self._db_password,
                    microservice_password=self._microservice_password)

        app_deployment_frmtd = \
            app_deployment.format(
                repository=self.repository,
                version=self.app_version,
                replicas=self.app_replicas,
                requests_memory=self.app_requests_memory,
                requests_cpu=self.app_requests_cpu,
                limits_cpu=self.app_limits_cpu,
                limits_memory=self.app_limits_memory,
                workers_timeout=self.app_timeout,
                n_workers=self.app_workers,
                debug=self.app_debug,
                db_username=self.db_username,
                db_host=self.db_host,
                db_port=self.db_port,
                db_database=self.db_database)

        worker_deployment_text_frmted = worker_deployment.format(
            repository=self.repository,
            version=self.worker_version,
            db_username=self.db_username,
            db_host=self.db_host,
            db_port=self.db_port,
            db_database=self.db_database,
            n_parallel=self.worker_n_parallel,
            chunk_size=self.worker_chunk_size,
            query_limit=self.worker_query_limit,
            replicas=self.worker_replicas,
            requests_memory=self.worker_requests_memory,
            requests_cpu=self.worker_requests_cpu,
            limits_cpu=self.worker_limits_cpu,
            limits_memory=self.worker_limits_memory,
            debug=self.worker_debug)

        return [
            PumpwoodDeploySecret(
                name='pumpwood_datalake__secrets',
                content=secrets_text_formated),
            PumpwoodDeployDeployment(
                name='pumpwood_datalake__deploy',
                content=app_deployment_frmtd),
            PumpwoodDeployDeployment(
                name='pumpwood_datalake_dataloader__worker',
                content=worker_deployment_text_frmted)]
