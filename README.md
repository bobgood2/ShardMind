# ShardMind
Scraper, Indexer, search engine, query planner, chat bot, LLM


# Download data for personal indexing

Install steps.
1. download from github into \repos\shardMind
2. install python and anaconda
3. C:\Users\bobgood>secrets.bat [you need to get this file from me personally to use the software]
4. in windows search look for and open anaconda prompt
5. cd \repos\shardMind
6. if there is a 'env' directory under shardMind, delete it if this is your first installation
7. (base) C:\repos\shardMind>python -m venv env
6. (base) C:\repos\shardMind>env\Scripts\activate
7. (env) (base) C:\repos\shardMind>pip install -r requirements.txt
8. (env) (base) C:\repos\shardMind>python auth.py
9. open a web browser and copy this url:   http://127.0.0.1:8000/login

# Build an Index
1.  Start separate Anaconda prompt for building index

# Start local servers
1.  Start separate Anaconda prompts for each local server

# run chat UI
1.  Start separate Anaconda prompt for running UI
2.  (base) C:\repos\shardMind>env\Scripts\activate
3.  (env) (base) C:\repos\ShardMind>chainlit run chatbot.py