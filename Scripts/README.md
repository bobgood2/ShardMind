start an anaconda prompt

cd \repos\shardmind
env\scripts\activate
pip install -r requirements.txt

run scipt batch files from below, but do not change the directory

if you want to change the root directory of the index temporarily
set INDEX_ROOT=index2

# scripts  (i add this direcory to my path)

scrape <=  downloads emails from microsoft graph
buildall <=  builds an email index.
look <= shows progress on scrape and build
index_serve  <= launches index_serve for email
test_index_serve <= hits the index serve once


not yet:
plan_runner service
app service