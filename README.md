# hardware_synchronizer

This is an on-going project/repo that I'm using to carry out some experiments in sychronizing some low-throughput hardware synchronization needs in both research and educational settings.  The primary structure is a basic, standa-alone archictecture for holding, distributing, and logging commands and responses between a master computer and remote worker computers, which are assumed to be distributed, small, "IOT" (shudder)-style devices such as single-board computers, microcontrollers, or even other traditional "computers."  



```
            +---------------+
            | Central Server|
            |  testsite.py  |
            +---------------+
                    ^
                    |
                    |
           +--------+---------+----....
           |                  |
          \/                  \/
     +-----+--------+   +-----+--------+
     | Distributed 1|   | Distributed 2|
     | heartbeat.py |   | heartbeat.py |
     +--------------+   +--------------+

```

This structure is nothing groundbreaking, and is basically how lots of the internet works, but a ready implementation of what I need doesn't exist so this is more about polishing and specifying up a structure.
 
## Development Version:
Current Repo contains Python-Based backend Hardware Monitor for Education Users (Flask-Based Version).  Commands can be inputted to the system via http `POST` commands that can be executed (currently using Python only) on any listening system. Outputs will be generated and reported back and then any user is free to assess those responses.  

Functioning distributions are found <a href="https://github.com/jodalyst/mostec17" target="_blank">here</a> and a slightly older version (that still works) <a href="https://github.com/jodalyst/mites17" target="_blank">here</a>

**Working notes below**

The database has the following things in it:

{user, state, command, hw_command, hw_response, server_analysis, time}

* `state`: state of state machine. It can be:
    * `0`: rest state
    * `1`: hardware_command requested (waiting to be picked up by hardware) (accessible in hw_command field)
    * `2`: hardware_command collected (waiting for response from hardware)
    * `3`: hardware_result returned (result from hardware returned, waiting for server analysis) 
* `command`: current operation to be desired (valid options depend on system state)
* `login`: whether you are logged in or not (not used right now)


All `GET` and `POST` requests return the status (db) fields for that particular piece of hardware.


GET (does not modify system state):

* `command=status_query`

POST (modifies system state depending on proper arguments, etc..):

* `command=hw_command_request`. Must come with a `hw_comm` value that is a Python program to run (only valid when system in state 0. Moves immediately to state 1)
* `command=hw_command_retrieval`: No values in request body.  (only valid when system in state 1. Moves to state 2 immediately)
* `command=hw_response_provide`. Must come with a `hw_resp` value that is a parseable string. (only valid in state 2. Moves to state 3)
* `command=server_analysis_provide`: Must come with `server_anal` value that is an arbitrary value. (only valid in state 3, Moves to state 0)
 
In all states, status_query:

* `state == 0`:
    * `command==status_query`: returns current state, hw_command
