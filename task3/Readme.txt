Firstly, make sure that you "pip install" 
-	logging
-	json
-	sys
-       getopt
-	time
-	requests
-	psycopg2

Secondly, create the database movie_db at Postgresql

Thirdly, run this command "psql -v ON_ERROR_STOP=1 -1 -h [host] -f ddl.sql movie_db"

Then, configure the connection to the database(host_name, host_port, user_name, password)  at "configuration.conf"

Finally, we run our application with this command

	"python movie_data.py [-r|--run] [update|display|all]"

So, first the name of the python script followed by the function we want to execute:
    	1| -r or --run stands for run the following function
	2| update stands for send an API call to the themoviedb.org to get the movies that are currently playing at the cinemas of Greece
	3| display stands for print the NOW PLAYING movies
	4| all stands for running the functions update and display combined.