# Changelog

## [1.4.0a0] - 2025-05-12

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Fixed
- N/A

## [1.3.7] - 2025-04-28

### Added
- N/A

### Changed
- Update wechat group QR code.

### Deprecated
- N/A

### Fixed
- N/A


## [1.3.6] - 2025-04-17

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Fixed
- Refactor chat history gathering to handle grouped data structure across multiple files, ensuring consistent data format for agent interactions.
- Fix the `from pyparsing import deque` error.


## [1.3.5] - 2025-04-14

### Added
- Add automatic monitoring of LLM requests, if a request is stuck for a long time, it will be logged.
    - To use this feature, you need to set `logging_level` to `DEBUG` in `AdvancedConfig`.

### Changed
- N/A

### Deprecated
- N/A

### Fixed
- Fix bug in survey dispatching.
- Fix bug in inconsistent schema when writing survey results to SQL.

## [1.3.4] - 2025-04-14

### Added
- Add docs for `reset` method in `Agent` and `Block`.

### Changed
- Return 404 rather than 200 for empty delete/update.
- Move webui config into database.

### Deprecated
- N/A

### Fixed
- Solve the problem of not being able to exit.
- Fix raising error when from memory.
- Enhance lock_decorator with exception logging for better error tracking.
- Fix bug in `NeedsBlock`.

## [1.3.3] - 2025-04-07

### Added
- Add `input_tokens` and `output_tokens` to experiment info.
- Add S3 storage support.
- Web API to export experiment data including agent profiles, agent statuses, agent dialogs, agent surveys, and global prompts.
- Add `NEXT_ROUND` step type, support multiple rounds of simulation.
- Add abstract method `reset` for `Agent` and implement it for all city agents.

### Changed
- Hide sensitive experiment information in AVRO and PostgreSQL storage.
- UI details.
- Removed `total_tick` in `EnvironmentConfig` - always 24 hours.
- Support float days in `RUN` step, for example, `RUN: 1.5 days`.

### Deprecated
- `Tool` abstract class.

### Fixed
- Bug in avro saver.

## [1.3.2] - 2025-04-02

### Removed
- Remove useless files due to merge error

## [1.3.1] - 2025-04-02

### Changed
- Update Python version requirements and cibuildwheel skip list.

## [1.3.0] - 2025-04-02

See [Version 1.3](https://agentsociety.readthedocs.io/en/latest/02-version-1.3/01.v1.3.0.html) for more details.

## [1.2.10] - 2025-03-18

### Added
- N/A

### Changed
- Add retry for syncer connections.

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Fix typo in `simulator.sence`

### Security
- N/A

## [1.2.9] - 2025-03-14

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Fixed bug for `update_environment` in `AgentGroup`.
- Bug for calling sequence of `agent.step` and `OnlyClientSidecar.step`.

### Security
- N/A

## [1.2.8] - 2025-03-14

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Fixed bug for `PlaceSelectionBlock.forward` when selecting POI.
- Bug for `OnlyClientSidecar` calling

### Security
- N/A

## [1.2.7] - 2025-03-14

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Fixed bug for `PlaceSelectionBlock.forward` when selecting POI.

### Security
- N/A

## [1.2.6] - 2025-03-12

### Added
- N/A

### Changed
- WeChat QR code.

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A
  
## [1.2.5] - 2025-03-07

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- Remove `Agent._uuid`

### Fixed
- Fixed bug for `simulation.init_agents` when creating group parameters for agents.

### Security
- N/A



## [1.2.4] - 2025-03-04

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- Remove `Agent._uuid`

### Fixed
- Fixed issue with `EconomyClient.update` when handling InstitutionAgent updates.
- Fixed bug for `MobilityBlock.MoveBlock.forward`.
- Added adjustment logic to ensure the sum of the returned employee counts exactly equals N in matching firms and employees.

### Security
- N/A


## [1.2.3] - 2025-03-03

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Fix typo in quick start docs.

### Security
- N/A



## [1.2.2] - 2025-03-02

### Added
- N/A

### Changed
- Change the download URL for `agentsociety-sim` to a publicly accessible address that does not require authentication in `setup.py`.

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Missed match between the dictionary and `economyv2.Firm` as input arguments in the `EconomyClient.update` method.

### Security
- N/A



## [1.2.1] - 2025-03-01

### Added
- Add docker compose for china user (use huawei cloud docker registry)

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Definition bug of `EconomyEntityType`

### Security
- N/A


## [1.2.0] - 2025-02-28

### Added
- N/A

### Changed
- Update `pycityproto` version to v2.2.8, splitting organization into bank, firm, government and statistical bureau.
- Adapt `environment.economy` to align with the new definitions of economic entities.

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [1.1.5] - 2025-02-28

### Added
- N/A

### Changed
- Update doc at `05-custom-agents`.
- Add more comments in agentsociety.cityagent

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A



## [1.1.4] - 2025-02-27

### Added
- Add log of original LLM response during handling LLM calling error.

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [1.1.3] - 2025-02-27

### Added
- N/A

### Changed
- The WeChat group chat QR code has been replaced to the second group. Welcome to join and participate in the discussions.

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Add retry for `syncer` server connecting, providing enough time for start.

### Security
- N/A


## [1.1.2] - 2025-02-26

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Calling `syncer` that didn't have time to start causes the gRPC service to report an error.

### Security
- N/A

## [1.1.1] - 2025-02-25

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Inconsistency of python 3.12 and current pydantic version. 

### Security
- N/A


## [1.1.0] - 2025-02-21

### Added
- N/A

### Changed
- The simulator has been converted to a synchronous mode, controlled by `ExpConfig.SimulatorConfig.steps_per_simulation_step` and `ExpConfig.SimulatorConfig.steps_per_simulation_day` parameters that determine the number of seconds per step for advancing the urban environment time in each simulation step and day.

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [1.0.13] - 2025-02-21

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- Delete `enable_institution` in ExpConfig

### Fixed
- N/A

### Security
- N/A

## [1.0.12] - 2025-02-21

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Document typo on `agentsociety-ui` activation.

### Security
- N/A

## [1.0.11] - 2025-02-21

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Bug of inconsistent length of `agent_counts` and `agent_class` in `simulation.init_agents`.

### Security
- N/A

## [1.0.10] - 2024-02-21

### Added
- N/A

### Changed
- Example map data download link in the document.

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [1.0.9] - 2024-02-20

### Added
- WeChat group QR code.

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A
  
## [1.0.8] - 2024-02-19

### Added
- N/A

### Changed
- Detailed document.

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A
 
## [1.0.7] - 2024-02-18

### Added
- N/A

### Changed
- Update agentsociety-ui to version v0.3.3.

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A
  
## [1.0.6] - 2024-02-18

### Added
- N/A

### Changed
- Detailed document.

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A
  
## [1.0.5] - 2024-02-15

### Added
- N/A

### Changed
- Set parent_id and lnglat of InstitutionAgent as NULL for pgsql

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [1.0.4] - 2024-02-14

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Bug of incorrect experiment uid for MLflow tag.

### Security
- N/A

## [1.0.3] - 2024-02-13

### Added
- Social experiment use case document.

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- 

### Security
- N/A

## [1.0.2] - 2024-02-08

### Added
- Social experiment use case with our platform.

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [1.0.1] - 2024-02-07

### Added
- Add `README.md`

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [1.0.0] - 2024-02-06

### Added
- Initial commit.

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A
