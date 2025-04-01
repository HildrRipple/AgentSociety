# Environment Configuration

The environment configuration defines the core infrastructure settings for the simulation framework. This configuration is managed through the `EnvConfig` class, which handles various components essential for the system's operation.

## Configuration Structure

The environment configuration consists of several key components:

### Redis Configuration
Redis serves as the message broker and temporary storage solution. The `redis` section configures:
- Connection parameters
- Message queue settings
- Caching configurations

The `RedisConfig` class contains the following fields:

- `server` (str, required): The Redis server address
- `port` (int, optional): Port number for Redis connection, defaults to 6379 (must be between 0-65535)
- `password` (str, optional): Password for Redis connection authentication
- `db` (int, optional): Database number for Redis connection, defaults to 0
- `timeout` (float, optional): Connection timeout in seconds, defaults to 60


### PostgreSQL Configuration 
The `pgsql` section manages the persistent storage database settings, including:
- Database connection parameters
- Table configurations
- Query settings

The `PostgreSQLConfig` class contains the following fields:

- `enabled` (bool, optional): Whether PostgreSQL storage is enabled, defaults to True
- `dsn` (str, required): Data source name for PostgreSQL connection, must start with "postgresql://"
- `num_workers` (Union[int, "auto"], optional): Number of workers for PostgreSQL operations, defaults to "auto"

The DSN (Data Source Name) string follows the format:

```
postgresql://user:password@host:port/database
```

### Avro Configuration
The `avro` section handles data serialization settings:
- Schema definitions
- Serialization formats
- Data validation rules

The `AvroConfig` class contains the following fields:

- `enabled` (bool, optional): Whether Avro storage is enabled, defaults to False
- `path` (str, required): The file system path where Avro files will be stored. Must be a valid directory path.

### MLflow Configuration
The `mlflow` component configures the machine learning experiment tracking:
- Experiment logging parameters
- Model tracking settings
- Metrics storage configuration
The `MlflowConfig` class contains the following fields:

- `enabled` (bool, optional): Whether MLflow tracking is enabled, defaults to False
- `username` (str, optional): Username for MLflow server authentication
- `password` (str, optional): Password for MLflow server authentication  
- `mlflow_uri` (str, required): URI for connecting to the MLflow tracking server
