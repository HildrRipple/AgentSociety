# Launching the Web UI

```{admonition} Caution
:class: caution
This document is currently under active development. The complete version will be available soon. Stay tuned!
```

To launch the Web UI, you first need to set up the environment as described in [Prerequisites](../01-quick-start/01-prerequisites.md), including PostgreSQL, MLflow, and Redis.

Then, create a configuration file (e.g., `config.yaml`) with the required environment information. The configuration include:

- Required field:
  ```yaml
  env: EnvConfig  # Environment configuration, see EnvConfig definition in `agentsociety/configs/env.py`
  ```

- Optional fields:
  ```yaml
  addr: str            # Service address, default ":8080"
  read_only: bool      # Read-only mode, default false
  debug: bool          # Debug mode, default false
  logging_level: str   # Logging level, default "INFO"
  ```

Once the configuration is ready, start the backend service using the following command:

 ```bash
 agentsociety ui --config config.yaml
 ```

- config.yaml example
    ```yaml
    addr: localhost:8080 # Optional: Address for the UI service
    env: # Required
      avro:
        enabled: true    # Enable avro data storage
        path: avro       # Path to store avro files
      mlflow:
        enabled: true    # Enable MLflow integration
        mlflow_uri: http://localhost:59000  # MLflow server address
        password: YOUR_PASSWORD  # MLflow password
        username: YOUR_USERNAME  # MLflow username
      pgsql:
        dsn: postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE  # PostgreSQL connection string
      redis:
        password: PASSWORD  # Redis password
        port: 6379         # Redis port
        server: localhost  # Redis server address
    ```

The UI service will be available at http://localhost:8080 or the address specified in your configuration file.
