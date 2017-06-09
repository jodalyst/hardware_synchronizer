# hardware_synchronizer
Python-Based Hardware Monitor for Education Users (Flask-Based Version)

**Working notes below**

The database has the following things in it:

{user, state, command, hw_command, hw_response, server_analysis, time}

* `state`: state of state machine. It can be:
    * `0`: rest state
    * `1`: hardware_command requested (waiting to be picked up by hardware) (accessible in hw_command field)
    * `2`: hardware_command collected (waiting for response from hardware)
    * `3`: hardware_result returned (result from hardware returned, waiting for server analysis) 
* `command`: current operation to be desired (valid options depend on system state)
* `login`: whether you are logged in or not


All GET and POST requests return the status (db) fields for that particular piece of hardware.
i


GET: 

* `command=status_query`

POST:

* `command=hw_command_request`. Must come with a `hw_comm` value that is a Python program to run (only valid when system in state 0. Moves immediately to state 1)
* `command=hw_command_retrieval`: No values in request body.  (only valid when system in state 1. Moves to state 2 immediately)
* `command=hw_response_provide`. Must come with a `hw_resp` value that is a parseable string. (only valid in state 2. Moves to state 3)
* `command=server_analysis_provide`: Must come with `server_anal` value that is an arbitrary value. (only valid in state 3, Moves to state 0)
 
In all states, status_query)

* `state == 0`:
    * `command==status_query`: returns current state, hw_command
