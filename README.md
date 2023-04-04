[comment]: # "Auto-generated SOAR connector documentation"
# Palo Alto Cortex XDR

Publisher: Cyberforce Limited  
Connector Version: 1\.0\.1  
Product Vendor: Palo Alto  
Product Name: Cortex XDR  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 4\.9\.39220  

This app integrates with the Palo Alto Cortex XDR

### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Cortex XDR asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**api\_key** |  required  | password | API Key
**advanced** |  optional  | boolean | Advanced Key
**api\_id** |  required  | string | API Key ID
**fqdn** |  required  | string | FQDN

### Supported Actions  
[on poll](#action-on-poll) - Callback action for the on\_poll ingest functionality  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration  
[list endpoints](#action-list-endpoints) - List all the endpoints/sensors configured on the device  
[get policy](#action-get-policy) - Get the policy name for a specific endpoint  
[get action status](#action-get-action-status) - Retrieve the status of the requested actions according to the action ID  
[retrieve file](#action-retrieve-file) - Retrieve files from a specified endpoint  
[retrieve file details](#action-retrieve-file-details) - View the file retrieved by the Retrieve File action according to the action ID  
[quarantine file](#action-quarantine-file) - Quarantine file on a specified endpoint  
[unquarantine file](#action-unquarantine-file) - Restore a quarantined file on a specified endpoint  
[block hash](#action-block-hash) - Add a hash that does not exist in the allow or block list to a block list  
[allow hash](#action-allow-hash) - Add files that do not exist in the allow or block list to an allow list  
[quarantine device](#action-quarantine-device) - Quarantine a specified endpoint  
[unquarantine device](#action-unquarantine-device) - Unquarantine a specified endpoint  
[scan endpoint](#action-scan-endpoint) - Run a scan on selected endpoints  
[cancel scan endpoint](#action-cancel-scan-endpoint) - Cancel the scan of selected endpoints  
[get incidents](#action-get-incidents) - Get a list of incidents filtered by a list of incident IDs, modification time, or creation time  
[get incident details](#action-get-incident-details) - Get extra data fields of a specific incident including alerts and key artifacts  
[get alerts](#action-get-alerts) - Get a list of alerts with multiple events  

## action: 'on poll'
Callback action for the on\_poll ingest functionality

Type: **ingest**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**container\_id** |  optional  | Container IDs to limit the ingestion to | string | 
**start\_time** |  optional  | Start of time range, in epoch time \(milliseconds\) | numeric | 
**end\_time** |  optional  | End of time range, in epoch time \(milliseconds\) | numeric | 
**container\_count** |  optional  | The maximum number of container records to query for | numeric | 
**artifact\_count** |  optional  | The maximum number of artifact records to query for | numeric | 

#### Action Output
No Output  

## action: 'test connectivity'
Validate the asset configuration for connectivity using supplied configuration

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'list endpoints'
List all the endpoints/sensors configured on the device

Type: **investigate**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get policy'
Get the policy name for a specific endpoint

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**endpoint\_id** |  required  | Endpoint ID to get the policy name for | string |  `cortex endpoint id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.endpoint\_id | string |  `cortex endpoint id` 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get action status'
Retrieve the status of the requested actions according to the action ID

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**action\_id** |  required  | Action ID to be queried | numeric |  `cortex action id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.action\_id | numeric |  `cortex action id` 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'retrieve file'
Retrieve files from a specified endpoint

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**endpoint\_id** |  required  | Endpoint ID to retrieve the files for | string |  `cortex endpoint id` 
**windows\_path** |  optional  | File path in Windows | string | 
**linux\_path** |  optional  | File path in Linux | string | 
**macos\_path** |  optional  | File path in Mac OS | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.endpoint\_id | string |  `cortex endpoint id` 
action\_result\.parameter\.windows\_path | string | 
action\_result\.parameter\.linux\_path | string | 
action\_result\.parameter\.macos\_path | string | 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'retrieve file details'
View the file retrieved by the Retrieve File action according to the action ID

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**action\_id** |  required  | Action ID of the file retrieval action | numeric |  `cortex action id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.action\_id | numeric |  `cortex action id` 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'quarantine file'
Quarantine file on a specified endpoint

Type: **contain**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**endpoint\_id** |  required  | Endpoint ID where the file is present | string |  `cortex endpoint id` 
**file\_path** |  required  | Path of the file you want to quarantine | string |  `file path` 
**file\_hash** |  required  | Hash of the file you want to quarantine | string |  `sha256` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.endpoint\_id | string |  `cortex endpoint id` 
action\_result\.parameter\.file\_path | string |  `file path` 
action\_result\.parameter\.file\_hash | string |  `sha256` 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'unquarantine file'
Restore a quarantined file on a specified endpoint

Type: **correct**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**file\_hash** |  required  | Hash of the file you want to restore | string |  `sha256` 
**endpoint\_id** |  required  | Endpoint ID to restore the file | string |  `cortex endpoint id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.file\_hash | string |  `sha256` 
action\_result\.parameter\.endpoint\_id | string |  `cortex endpoint id` 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'block hash'
Add a hash that does not exist in the allow or block list to a block list

Type: **contain**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**file\_hash** |  required  | File hash in SHA256 to be added to the block list | string |  `sha256` 
**comment** |  optional  | Additional information regarding this action | string | 
**incident\_id** |  optional  | Incident ID related to the file hash | numeric |  `cortex incident id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.file\_hash | string |  `sha256` 
action\_result\.parameter\.comment | string | 
action\_result\.parameter\.incident\_id | numeric |  `cortex incident id` 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'allow hash'
Add files that do not exist in the allow or block list to an allow list

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**file\_hash** |  required  | File hash in SHA256 to be added to the allow list | string |  `sha256` 
**comment** |  optional  | Additional information regarding this action | string | 
**incident\_id** |  optional  | Incident ID related to the file hash | numeric |  `cortex incident id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.file\_hash | string |  `sha256` 
action\_result\.parameter\.comment | string | 
action\_result\.parameter\.incident\_id | numeric |  `cortex incident id` 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'quarantine device'
Quarantine a specified endpoint

Type: **contain**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**endpoint\_id** |  required  | Endpoint ID to be isolated | string |  `cortex endpoint id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.endpoint\_id | string |  `cortex endpoint id` 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'unquarantine device'
Unquarantine a specified endpoint

Type: **correct**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**endpoint\_id** |  required  | Endpoint ID to be unisolated | string |  `cortex endpoint id` 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.endpoint\_id | string |  `cortex endpoint id` 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'scan endpoint'
Run a scan on selected endpoints

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**scan\_all** |  optional  | Scan all endpoints | boolean | 
**endpoint\_id** |  optional  | Endpoint ID to scan | string |  `cortex endpoint id` 
**dist\_name** |  optional  | Name of the distribution list | string | 
**first\_seen** |  optional  | When an endpoint was first seen | numeric | 
**last\_seen** |  optional  | When an endpoint was last seen | numeric | 
**ip\_list** |  optional  | IP address to scan | string | 
**group\_name** |  optional  | Name of endpoint group | string | 
**platform** |  optional  | Type of operating system | string | 
**alias** |  optional  | Endpoint alias name | string | 
**isolated** |  optional  | Limit to only isolated hosts | boolean | 
**unisolated** |  optional  | Limit to only unisolated hosts | boolean | 
**hostname** |  optional  | Name of host | string |  `host name` 
**scan\_status** |  optional  | Scan status of an endpoint \(select from defined values\) | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.scan\_all | boolean | 
action\_result\.parameter\.endpoint\_id | string |  `cortex endpoint id` 
action\_result\.parameter\.dist\_name | string | 
action\_result\.parameter\.first\_seen | numeric | 
action\_result\.parameter\.last\_seen | numeric | 
action\_result\.parameter\.ip\_list | string | 
action\_result\.parameter\.group\_name | string | 
action\_result\.parameter\.platform | string | 
action\_result\.parameter\.alias | string | 
action\_result\.parameter\.isolated | boolean | 
action\_result\.parameter\.unisolated | boolean | 
action\_result\.parameter\.hostname | string |  `host name` 
action\_result\.parameter\.scan\_status | string | 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'cancel scan endpoint'
Cancel the scan of selected endpoints

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**scan\_all** |  optional  | Cancel all endpoints | boolean | 
**endpoint\_id** |  optional  | Endpoint ID to cancel the scan | string |  `cortex endpoint id` 
**dist\_name** |  optional  | Name of the distribution list | string | 
**first\_seen** |  optional  | When an endpoint was first seen | numeric | 
**last\_seen** |  optional  | When an endpoint was last seen | numeric | 
**ip\_list** |  optional  | IP Address to cancel the scan for | string | 
**group\_name** |  optional  | Name of endpoint group | string | 
**platform** |  optional  | Type of operating system | string | 
**alias** |  optional  | Endpoint alias name | string | 
**isolated** |  optional  | Limit to only isolated hosts | boolean | 
**unisolated** |  optional  | Limit to only unisolated hosts | boolean | 
**hostname** |  optional  | Name of host | string |  `host name` 
**scan\_status** |  optional  | Scan status of an endpoint \(select from defined values\) | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.scan\_all | boolean | 
action\_result\.parameter\.endpoint\_id | string |  `cortex endpoint id` 
action\_result\.parameter\.dist\_name | string | 
action\_result\.parameter\.first\_seen | numeric | 
action\_result\.parameter\.last\_seen | numeric | 
action\_result\.parameter\.ip\_list | string | 
action\_result\.parameter\.group\_name | string | 
action\_result\.parameter\.platform | string | 
action\_result\.parameter\.alias | string | 
action\_result\.parameter\.isolated | boolean | 
action\_result\.parameter\.unisolated | boolean | 
action\_result\.parameter\.hostname | string |  `host name` 
action\_result\.parameter\.scan\_status | string | 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get incidents'
Get a list of incidents filtered by a list of incident IDs, modification time, or creation time

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**modification\_time** |  optional  | Modification time of the incident in timestamp epoch milliseconds | numeric | 
**creation\_time** |  optional  | Creation time of the incident in timestamp epoch milliseconds | numeric | 
**incident\_id** |  optional  | Incident ID to be searched | numeric |  `cortex incident id` 
**description** |  optional  | Incident description to be searched | string | 
**alert\_sources** |  optional  | Source which detected the alert | string | 
**status** |  optional  | Status of the incident to be searched \(select from defined values\) | string | 
**search\_from** |  optional  | Starting offset within the query result set from which you want incidents returned | numeric | 
**search\_to** |  optional  | End offset within the result set after which you do not want incidents returned | numeric | 
**sort** |  optional  | Sorting of the returned results | boolean | 
**sort\_field** |  optional  | Sorting field \(select from defined values\) | string | 
**sort\_order** |  optional  | Sorting order \(select from defined values\) | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.modification\_time | numeric | 
action\_result\.parameter\.creation\_time | numeric | 
action\_result\.parameter\.incident\_id | numeric |  `cortex incident id` 
action\_result\.parameter\.description | string | 
action\_result\.parameter\.alert\_sources | string | 
action\_result\.parameter\.status | string | 
action\_result\.parameter\.search\_from | numeric | 
action\_result\.parameter\.search\_to | numeric | 
action\_result\.parameter\.sort | boolean | 
action\_result\.parameter\.sort\_field | string | 
action\_result\.parameter\.sort\_order | string | 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get incident details'
Get extra data fields of a specific incident including alerts and key artifacts

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**incident\_id** |  required  | Incident ID to be investigated | numeric |  `cortex incident id` 
**alerts\_limit** |  optional  | The maximum number of related alerts to be returned | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.incident\_id | numeric |  `cortex incident id` 
action\_result\.parameter\.alerts\_limit | numeric | 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
action\_result\.summary\.is\_malicious | boolean | 
action\_result\.summary\.file\_name | string | 
action\_result\.summary\.file\_sha256 | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get alerts'
Get a list of alerts with multiple events

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**alert\_id** |  optional  | Alert ID to be searched | numeric |  `cortex alert id` 
**alert\_source** |  optional  | The source which detected the alert | string | 
**severity** |  optional  | The severity of the alert to be searched \(select from defined values\) | string | 
**creation\_time** |  optional  | Creation time of the alert in timestamp epoch milliseconds | numeric | 
**search\_from** |  optional  | Starting offset within the query result set from which you want incidents returned | numeric | 
**search\_to** |  optional  | End offset within the result set after which you do not want incidents returned | numeric | 
**sort** |  optional  | Sorting of the returned results | boolean | 
**sort\_field** |  optional  | Sorting field \(select from defined values\) | string | 
**sort\_order** |  optional  | Sorting order \(select from defined values\) | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.alert\_id | numeric |  `cortex alert id` 
action\_result\.parameter\.alert\_source | string | 
action\_result\.parameter\.severity | string | 
action\_result\.parameter\.creation\_time | numeric | 
action\_result\.parameter\.search\_from | numeric | 
action\_result\.parameter\.search\_to | numeric | 
action\_result\.parameter\.sort | boolean | 
action\_result\.parameter\.sort\_field | string | 
action\_result\.parameter\.sort\_order | string | 
action\_result\.data | string | 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 