"""Kubernetes deployment package for the Pumpwood Datalake microservice.

Use ``PumpWoodDatalakeMicroservice`` with ``DeployPumpWood`` from
``pumpwood-deploy`` to generate and apply datalake manifests.

Example:
    ```python
    from pumpwood_deploy_datalake import PumpWoodDatalakeMicroservice

    datalake = PumpWoodDatalakeMicroservice(
        app_version="1.0",
        worker_version="1.0",
    )
    deploy.add_microservice(datalake)
    ```

Cluster prerequisites include ``StandardMicroservices`` (storage
ConfigMap, general secrets, RabbitMQ), ``PumpWoodAuthMicroservice`` for
authorization, and Postgres via ``PGBouncerDatabase``.
"""
from .deploy import PumpWoodDatalakeMicroservice

__all__ = [
    PumpWoodDatalakeMicroservice
]
