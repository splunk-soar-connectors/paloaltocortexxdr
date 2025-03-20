# Palo Alto Cortex XDR

Publisher: Cyberforce Limited \
Connector Version: 1.2.0 \
Product Vendor: Palo Alto \
Product Name: Cortex XDR \
Minimum Product Version: 5.4.0

This app integrates with the Palo Alto Cortex XDR

### Configuration variables

This table lists the configuration variables required to operate Palo Alto Cortex XDR. These variables are specified when configuring a Cortex XDR asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**api_key** | required | password | API Key |
**advanced** | optional | boolean | Advanced Key |
**api_id** | required | string | API Key ID |
**fqdn** | required | string | FQDN |

### Supported Actions

[on poll](#action-on-poll) - Callback action for the on_poll ingest functionality \
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration \
[list endpoints](#action-list-endpoints) - List all the endpoints/sensors configured on the device \
[get policy](#action-get-policy) - Get the policy name for a specific endpoint \
[get action status](#action-get-action-status) - Retrieve the status of the requested actions according to the action ID \
[retrieve file](#action-retrieve-file) - Retrieve files from a specified endpoint \
[retrieve file details](#action-retrieve-file-details) - View the file retrieved by the Retrieve File action according to the action ID \
[quarantine file](#action-quarantine-file) - Quarantine file on a specified endpoint \
[unquarantine file](#action-unquarantine-file) - Restore a quarantined file on a specified endpoint \
[block hash](#action-block-hash) - Add a hash that does not exist in the allow or block list to a block list \
[allow hash](#action-allow-hash) - Add files that do not exist in the allow or block list to an allow list \
[quarantine device](#action-quarantine-device) - Quarantine a specified endpoint \
[unquarantine device](#action-unquarantine-device) - Unquarantine a specified endpoint \
[scan endpoint](#action-scan-endpoint) - Run a scan on selected endpoints \
[cancel scan endpoint](#action-cancel-scan-endpoint) - Cancel the scan of selected endpoints \
[get incidents](#action-get-incidents) - Get a list of incidents filtered by a list of incident IDs, modification time, or creation time \
[get incident details](#action-get-incident-details) - Get extra data fields of a specific incident including alerts and key artifacts \
[get alerts](#action-get-alerts) - Get a list of alerts with multiple events

## action: 'on poll'

Callback action for the on_poll ingest functionality

Type: **ingest** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**container_id** | optional | Container IDs to limit the ingestion to | string | |
**start_time** | optional | Start of time range, in epoch time (milliseconds) | numeric | |
**end_time** | optional | End of time range, in epoch time (milliseconds) | numeric | |
**container_count** | optional | The maximum number of container records to query for | numeric | |
**artifact_count** | optional | The maximum number of artifact records to query for | numeric | |

#### Action Output

No Output

## action: 'test connectivity'

Validate the asset configuration for connectivity using supplied configuration

Type: **test** \
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

No Output

## action: 'list endpoints'

List all the endpoints/sensors configured on the device

Type: **investigate** \
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get policy'

Get the policy name for a specific endpoint

Type: **investigate** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**endpoint_id** | required | Endpoint ID to get the policy name for | string | `cortex endpoint id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.endpoint_id | string | `cortex endpoint id` | |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get action status'

Retrieve the status of the requested actions according to the action ID

Type: **investigate** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**action_id** | required | Action ID to be queried | numeric | `cortex action id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.action_id | numeric | `cortex action id` | |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'retrieve file'

Retrieve files from a specified endpoint

Type: **investigate** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**endpoint_id** | required | Endpoint ID to retrieve the files for | string | `cortex endpoint id` |
**windows_path** | optional | File path in Windows | string | |
**linux_path** | optional | File path in Linux | string | |
**macos_path** | optional | File path in Mac OS | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.endpoint_id | string | `cortex endpoint id` | |
action_result.parameter.linux_path | string | | |
action_result.parameter.macos_path | string | | |
action_result.parameter.windows_path | string | | |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'retrieve file details'

View the file retrieved by the Retrieve File action according to the action ID

Type: **investigate** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**action_id** | required | Action ID of the file retrieval action | numeric | `cortex action id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.action_id | numeric | `cortex action id` | |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'quarantine file'

Quarantine file on a specified endpoint

Type: **contain** \
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**endpoint_id** | required | Endpoint ID where the file is present | string | `cortex endpoint id` |
**file_path** | required | Path of the file you want to quarantine | string | `file path` |
**file_hash** | required | Hash of the file you want to quarantine | string | `sha256` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.endpoint_id | string | `cortex endpoint id` | |
action_result.parameter.file_hash | string | `sha256` | |
action_result.parameter.file_path | string | `file path` | |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'unquarantine file'

Restore a quarantined file on a specified endpoint

Type: **correct** \
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**file_hash** | required | Hash of the file you want to restore | string | `sha256` |
**endpoint_id** | required | Endpoint ID to restore the file | string | `cortex endpoint id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.endpoint_id | string | `cortex endpoint id` | |
action_result.parameter.file_hash | string | `sha256` | |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'block hash'

Add a hash that does not exist in the allow or block list to a block list

Type: **contain** \
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**file_hash** | required | File hash in SHA256 to be added to the block list | string | `sha256` |
**comment** | optional | Additional information regarding this action | string | |
**incident_id** | optional | Incident ID related to the file hash | numeric | `cortex incident id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.comment | string | | |
action_result.parameter.file_hash | string | `sha256` | |
action_result.parameter.incident_id | numeric | `cortex incident id` | |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'allow hash'

Add files that do not exist in the allow or block list to an allow list

Type: **generic** \
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**file_hash** | required | File hash in SHA256 to be added to the allow list | string | `sha256` |
**comment** | optional | Additional information regarding this action | string | |
**incident_id** | optional | Incident ID related to the file hash | numeric | `cortex incident id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.comment | string | | |
action_result.parameter.file_hash | string | `sha256` | |
action_result.parameter.incident_id | numeric | `cortex incident id` | |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'quarantine device'

Quarantine a specified endpoint

Type: **contain** \
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**endpoint_id** | required | Endpoint ID to be isolated | string | `cortex endpoint id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.endpoint_id | string | `cortex endpoint id` | |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'unquarantine device'

Unquarantine a specified endpoint

Type: **correct** \
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**endpoint_id** | required | Endpoint ID to be unisolated | string | `cortex endpoint id` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.endpoint_id | string | `cortex endpoint id` | |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'scan endpoint'

Run a scan on selected endpoints

Type: **generic** \
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**scan_all** | optional | Scan all endpoints | boolean | |
**endpoint_id** | optional | Endpoint ID to scan | string | `cortex endpoint id` |
**dist_name** | optional | Name of the distribution list | string | |
**first_seen** | optional | When an endpoint was first seen | numeric | |
**last_seen** | optional | When an endpoint was last seen | numeric | |
**ip_list** | optional | IP address to scan | string | |
**group_name** | optional | Name of endpoint group | string | |
**platform** | optional | Type of operating system | string | |
**alias** | optional | Endpoint alias name | string | |
**isolated** | optional | Limit to only isolated hosts | boolean | |
**unisolated** | optional | Limit to only unisolated hosts | boolean | |
**hostname** | optional | Name of host | string | `host name` |
**scan_status** | optional | Scan status of an endpoint (select from defined values) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.alias | string | | |
action_result.parameter.dist_name | string | | |
action_result.parameter.endpoint_id | string | `cortex endpoint id` | |
action_result.parameter.first_seen | numeric | | |
action_result.parameter.group_name | string | | |
action_result.parameter.hostname | string | `host name` | |
action_result.parameter.ip_list | string | | |
action_result.parameter.isolated | boolean | | True False |
action_result.parameter.last_seen | numeric | | |
action_result.parameter.platform | string | | |
action_result.parameter.scan_all | boolean | | True False |
action_result.parameter.scan_status | string | | |
action_result.parameter.unisolated | boolean | | True False |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'cancel scan endpoint'

Cancel the scan of selected endpoints

Type: **generic** \
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**scan_all** | optional | Cancel all endpoints | boolean | |
**endpoint_id** | optional | Endpoint ID to cancel the scan | string | `cortex endpoint id` |
**dist_name** | optional | Name of the distribution list | string | |
**first_seen** | optional | When an endpoint was first seen | numeric | |
**last_seen** | optional | When an endpoint was last seen | numeric | |
**ip_list** | optional | IP Address to cancel the scan for | string | |
**group_name** | optional | Name of endpoint group | string | |
**platform** | optional | Type of operating system | string | |
**alias** | optional | Endpoint alias name | string | |
**isolated** | optional | Limit to only isolated hosts | boolean | |
**unisolated** | optional | Limit to only unisolated hosts | boolean | |
**hostname** | optional | Name of host | string | `host name` |
**scan_status** | optional | Scan status of an endpoint (select from defined values) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.alias | string | | |
action_result.parameter.dist_name | string | | |
action_result.parameter.endpoint_id | string | `cortex endpoint id` | |
action_result.parameter.first_seen | numeric | | |
action_result.parameter.group_name | string | | |
action_result.parameter.hostname | string | `host name` | |
action_result.parameter.ip_list | string | | |
action_result.parameter.isolated | boolean | | True False |
action_result.parameter.last_seen | numeric | | |
action_result.parameter.platform | string | | |
action_result.parameter.scan_all | boolean | | True False |
action_result.parameter.scan_status | string | | |
action_result.parameter.unisolated | boolean | | True False |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get incidents'

Get a list of incidents filtered by a list of incident IDs, modification time, or creation time

Type: **investigate** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**modification_time** | optional | Modification time of the incident in timestamp epoch milliseconds | numeric | |
**creation_time** | optional | Creation time of the incident in timestamp epoch milliseconds | numeric | |
**incident_id** | optional | Incident ID to be searched | numeric | `cortex incident id` |
**description** | optional | Incident description to be searched | string | |
**alert_sources** | optional | Source which detected the alert | string | |
**status** | optional | Status of the incident to be searched (select from defined values) | string | |
**search_from** | optional | Starting offset within the query result set from which you want incidents returned | numeric | |
**search_to** | optional | End offset within the result set after which you do not want incidents returned | numeric | |
**sort** | optional | Sorting of the returned results | boolean | |
**sort_field** | optional | Sorting field (select from defined values) | string | |
**sort_order** | optional | Sorting order (select from defined values) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.alert_sources | string | | |
action_result.parameter.creation_time | numeric | | |
action_result.parameter.description | string | | |
action_result.parameter.incident_id | numeric | `cortex incident id` | |
action_result.parameter.modification_time | numeric | | |
action_result.parameter.search_from | numeric | | |
action_result.parameter.search_to | numeric | | |
action_result.parameter.sort | boolean | | True False |
action_result.parameter.sort_field | string | | |
action_result.parameter.sort_order | string | | |
action_result.parameter.status | string | | |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get incident details'

Get extra data fields of a specific incident including alerts and key artifacts

Type: **investigate** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**incident_id** | required | Incident ID to be investigated | numeric | `cortex incident id` |
**alerts_limit** | optional | The maximum number of related alerts to be returned | numeric | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.alerts_limit | numeric | | |
action_result.parameter.incident_id | numeric | `cortex incident id` | |
action_result.data | string | | |
action_result.summary | string | | |
action_result.summary.file_name | string | | |
action_result.summary.file_sha256 | string | | |
action_result.summary.is_malicious | boolean | | True False |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'get alerts'

Get a list of alerts with multiple events

Type: **investigate** \
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alert_id** | optional | Alert ID to be searched | numeric | `cortex alert id` |
**alert_source** | optional | The source which detected the alert | string | |
**severity** | optional | The severity of the alert to be searched (select from defined values) | string | |
**creation_time** | optional | Creation time of the alert in timestamp epoch milliseconds | numeric | |
**search_from** | optional | Starting offset within the query result set from which you want incidents returned | numeric | |
**search_to** | optional | End offset within the result set after which you do not want incidents returned | numeric | |
**sort** | optional | Sorting of the returned results | boolean | |
**sort_field** | optional | Sorting field (select from defined values) | string | |
**sort_order** | optional | Sorting order (select from defined values) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.status | string | | success failed |
action_result.parameter.alert_id | numeric | `cortex alert id` | |
action_result.parameter.alert_source | string | | |
action_result.parameter.creation_time | numeric | | |
action_result.parameter.search_from | numeric | | |
action_result.parameter.search_to | numeric | | |
action_result.parameter.severity | string | | |
action_result.parameter.sort | boolean | | True False |
action_result.parameter.sort_field | string | | |
action_result.parameter.sort_order | string | | |
action_result.data | string | | |
action_result.summary | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2025 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
