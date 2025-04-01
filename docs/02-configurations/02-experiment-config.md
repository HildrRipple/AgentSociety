# Experiment Configuration

The experiment configuration defines the overall settings and workflow for running a simulation. This configuration is managed through the `ExpConfig` class.

## Configuration Structure

The experiment configuration consists of several key components:

### Basic Information
- `name` (str, required): Name identifier for the experiment. Defaults to "default_experiment".
- `id` (UUID): Unique identifier for the experiment. Auto-generated if not specified.

### Workflow Configuration
The `workflow` field (required) defines a sequence of workflow steps that control how the simulation runs. Each step is configured through `WorkflowStepConfig` with the following types:

- `STEP`: Execute simulation for a specified number of steps
  - `steps`: Number of steps to run
  - `ticks_per_step`: Number of ticks per step
  
- `RUN`: Execute simulation for a specified number of days
  - `days`: Number of days to run
  - `ticks_per_step`: Number of ticks per step

- `INTERVIEW`: Send interview questions to specific agents
  - `target_agent`: List of agent IDs to interview
  - `interview_message`: The interview question/prompt

- `SURVEY`: Send surveys to specific agents
  - `target_agent`: List of agent IDs to survey
  - `survey`: Survey object containing questions

- `ENVIRONMENT_INTERVENE`: Modify environment variables
  - `key`: Environment variable to modify
  - `value`: New value to set

- `UPDATE_STATE_INTERVENE`: Update agent states directly
  - `target_agent`: List of agent IDs to update
  - `key`: State variable to modify
  - `value`: New value to set

- `MESSAGE_INTERVENE`: Send intervention messages to agents
  - `target_agent`: List of agent IDs to message
  - `intervene_message`: Message content

- `INTERVENE`: Custom intervention via function
  - `func`: Function implementing the intervention

- `FUNCTION`: Execute arbitrary function
  - `func`: Function to execute

### Environment Configuration
The `environment` field (required) contains environment settings through `EnvironmentConfig` that define the simulation environment parameters.

### Message Interception
The `message_intercept` field (optional) configures message interception through `MessageInterceptConfig`:

- `mode`: Either "point" or "edge" interception mode
- `max_violation_time`: Maximum allowed violations
- `blocks`: List of message block rules
- `listener`: Message block listener class

### Metric Collection
The `metric_extractors` field (optional) defines metrics to collect during simulation through `MetricExtractorConfig`:

- Function-based metrics:
  - `type`: "FUNCTION"
  - `func`: Function that computes the metric
  - `step_interval`: How often to collect the metric
  - `description`: Description of what is being measured

- State-based metrics:
  - `type`: "STATE" 
  - `target_agent`: Agents to collect from
  - `key`: State variable to measure
  - `method`: Aggregation method ("mean", "sum", "max", "min")
  - `step_interval`: Collection frequency
  - `description`: Description of the metric
