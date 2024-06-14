# installation
download this repo (in examples below, i show the repo loaded to c:\repos\shardmind)
install python (any version.  3.10 or 3.11 are good)
install anaconda
open anaconda console (a cmd console with environments)

execute the batch file c:\repos\shardmind\scripts\install.bat

# running code from the repo
cd \repos\shardmind

activate python environment:

env\Scripts\activate.bat

set \repos\shardmind\scripts in your path

run pre-existing scripts:
xyz.bat


# get your personal data
scrape.bat will download your emails very slowly, and you will need to periodically enter your devicelogin and restart this over a day or so.

There is also ways to get heron data, that is just now being integrated.


# build index
cd to the root directory c:\repos\shardmind
add c:\repos\shardmind to your path

or just run Scripts\buildall.bat

this will build a directory under c:\index

if you want to change the root directory of the index temporarily
set INDEX_ROOT=index2

# run the demo
Scripts\restart.bat


this opens multiple cmd windows: orchestrator, and indexserve, and logging
and opens two browser windows:  chat and debug/logging


the above calls these three batch files in different windows:
index_serve  <= launches index_serve for email
debug_server <=  starts a service to collect logs visible on a web page
                 kill it and restart it to empty logs
                 http://localhost:8080
app <= starts the chatbot... but make sure all the servers are started first

#other tools

look <= shows progress on scrape and build
test_index_serve <= hits the index serve once
                 Post http://localhost:5001/search_email 
test_debug_server  <= hits the debug server
