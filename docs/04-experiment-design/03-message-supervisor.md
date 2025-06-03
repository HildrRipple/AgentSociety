# Message Supervisor

The message interception system provides control over agent communications in the simulation environment. This feature allows you to monitor, filter, and regulate messages exchanged between agents based on customizable rules.

## Overview

The message interception system consists of two main components:

1. **Message Interceptor**: The core component that handles message validation and forwarding
2. **Supervisor**: A specialized agent that implements message validation logic and intervention strategies

## Message Interceptor

The `MessageInterceptor` class is responsible for intercepting and processing messages based on configured rules. It works in conjunction with a Supervisor to validate messages and handle interventions.

Key features:
- Message validation through a Supervisor
- Violation tracking
- Message forwarding with intervention support
- Integration with LLM for advanced processing

### Example Configuration

```python
from agentsociety.message import MessageInterceptor
from agentsociety.llm import LLMConfig

# Initialize the interceptor with LLM configuration
interceptor = MessageInterceptor(
    llm_config=[LLMConfig(...)]
)

# Initialize the interceptor
await interceptor.init()

# Set the supervisor
await interceptor.set_supervisor(supervisor)
```

## Supervisor

The `SupervisorBase` class is a specialized agent that implements message validation and intervention logic. To create a custom supervisor, inherit from `SupervisorBase` and implement the `forward` method.

### Example of a Custom Supervisor

```python
from agentsociety.agent import SupervisorBase
from agentsociety.message import Message

class CustomSupervisor(SupervisorBase):
    async def forward(
        self,
        current_round_messages: list[Message],
    ) -> tuple[dict[Message, bool], list[Message]]:
        """
        Process and validate messages from the current round
        
        Args:
            current_round_messages: List of messages for the current round
            
        Returns:
            validation_dict: Dictionary mapping messages to their validation status
            persuasion_messages: List of intervention messages
        """
        validation_dict = {}
        persuasion_messages = []
        
        # Implement your validation logic here
        for message in current_round_messages:
            # Example validation logic
            is_valid = True  # Replace with actual validation
            validation_dict[message] = is_valid
            
            if not is_valid:
                # Add intervention message if needed
                persuasion_messages.append(...)
                
        return validation_dict, persuasion_messages
```

## Message Processing Flow

1. Messages are sent to the MessageInterceptor
2. The interceptor forwards messages to the Supervisor for validation
3. The Supervisor processes messages and returns:
   - A validation dictionary indicating which messages are valid
   - Any intervention messages that should be sent
4. The interceptor processes the results and:
   - Forwards valid messages
   - Sends failure notifications for invalid messages
   - Includes any intervention messages in the final output

## Usage Example

Here's how to configure message interception in your experiment:

```python
from agentsociety.config import Config, ExpConfig, MessageInterceptConfig

config = Config(
    ...
    exp=ExpConfig(
        ...
        message_intercept=MessageInterceptConfig(
            supervisor=CustomSupervisor,  # Your custom supervisor class
        ),
        environment=EnvironmentConfig(
            start_tick=6 * 60 * 60,
            total_tick=18 * 60 * 60,
        ),
    ),
)
```
