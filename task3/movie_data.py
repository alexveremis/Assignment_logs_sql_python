import logging
import logging.config
import json, sys, getopt, time, requests, psycopg2


class MovieDatabaseHelper():

    def __init__(self, host_name, host_port, user_name, password, db, config_data):
        try:
            self.connection = psycopg2.connect(
                    host=host_name,
                    port=host_port,
                    user=user_name,
                    password=password,
                    database=db
                )
            self.cursor = self.connection.cursor()
            self.config_data = config_data
        except Exception  as e:
            logger.error ("Error %d: %s" % (e.args[0], e.args[1]))

    
    def get_updates(self):
        url = self.config_data['url1']
        headers = {
            "accept": "application/json",
            "Authorization": self.config_data['token']
            }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # If we get a 200 response search all of the pages for the active movies
                data = json.loads(response.text)
                total_pages = data.get('total_pages')
                for i in range (1, total_pages+1):
                    url += url + "&page=" + str(i)
                    response = requests.get(url, headers=headers)
                    data = json.loads(response.text)
                    results = data.get('results')
                    # For every movie
                    for result in results: 
                        id = result.get('id')
                        original_title = result.get('original_title')
                        title = result.get('title')
                        overview = result.get('overview')

                        # If it is the first time encountering this movie insert it into the movie table 
                        self.cursor.execute( self.config_data['sql_query_select_movie_id'], [id])
                        sql_result = self.cursor.fetchall()[0][0]
                        if (sql_result != 1): 
                            self.cursor.execute("""INSERT INTO movie("ID", "TITLE", "ORIGINAL_TITLE", "DESCRIPTION", "NOW_PLAYING", 
                                                "LAST_UPDATE_DATE") VALUES (%s, %s, %s, %s, true, NOW())""", [id, title, original_title, overview])
                            url_director = self.config_data['url_director1'] + str(id) + self.config_data['url_director2']
                            director_text = requests.get(url_director, headers=headers).text
                            data_director = json.loads(director_text)
                            directors = [member for member in data_director.get('crew', []) if member.get('job') == 'Director']
                            # Find every director related to this movie
                            for director in directors:
                                director_id = director.get('id')
                                self.cursor.execute("""SELECT COUNT(*) FROM director WHERE "ID" = %s""", [director_id])
                                sql_result = self.cursor.fetchall()[0][0]
                                # If it is the first time encountering this director, insert the director into the director table
                                if (sql_result != 1): 
                                    name = director.get('name')
                                    url_person = self.config_data['url_person'] + str(director_id) + "?language=en-US"
                                    person_text = requests.get(url_person, headers=headers).text
                                    data_person = json.loads(person_text)
                                    imdb_id = data_person.get('imdb_id')
                                    if (imdb_id is None):
                                        imdb_link = "No IMDB link found"
                                    else:
                                        imdb_link = self.config_data['imdb_link'] + str(imdb_id) 
                                    self.cursor.execute("""INSERT INTO director("ID", "FULL_NAME", "IMDB_LINK") VALUES (%s, %s, %s)""", [director_id, name, imdb_link])
                                    self.connection.commit()
                                # Relational DB, therefore a table connecting directors to movies
                                self.cursor.execute("""INSERT INTO movie_director("MOVIE_ID", "DIRECTOR_ID") VALUES (%s, %s)""", [id, director_id])
                                self.connection.commit()

                        else:
                            # Because we found it on the website on now playing section
                            self.cursor.execute("""UPDATE movie SET "NOW_PLAYING" = true, "LAST_UPDATE_DATE" = NOW() WHERE "ID" = %s""", [id] )
                            self.connection.commit()
                # Set to NOT playing atm the movies that we did not found at the api call.
                self.cursor.execute("""UPDATE movie SET "NOW_PLAYING" = false, "LAST_UPDATE_DATE" = NOW() WHERE "NOW_PLAYING" = true AND "LAST_UPDATE_DATE" < CURRENT_DATE""", )
                self.connection.commit()
            else:
                pass
        except Exception  as e:
            logger.error ("Error %d: %s" % (e.args[0], e.args[1]))   
        logger.info("Updated the postgresql DB to current image of the available movies")
        return 

    def display_current_movies(self):
        movies = []
        try:
            # Get the movies that are playing at the Greek cinemas atm.
            self.cursor.execute("""SELECT * FROM movie WHERE "NOW_PLAYING" = true""", )
            sql_results = self.cursor.fetchall()
            for result in sql_results:
                movie_id = result[0]
                # Get all directors that are related to a movie and have a check if there is no info about the director
                self.cursor.execute("""SELECT "DIRECTOR_ID" FROM movie_director WHERE "MOVIE_ID" = %s""", [movie_id] )
                sql_results2 = self.cursor.fetchall()
                if sql_results2 == []:
                    director_ids = []
                else:
                    director_ids = sql_results2
                directors = []
                # Put all of the directors into a list
                for director_id in director_ids:
                    director_id_ins = director_id[0]
                    self.cursor.execute("""SELECT * FROM director WHERE "ID" = %s""", [director_id_ins] )
                    sql_results3 = self.cursor.fetchall()[0]
                    director_full_name = sql_results3[1]
                    director_link = sql_results3[2]
                    director = [director_full_name, director_link]
                    directors += [director]
                movie_title = result[1]
                movie_description = result[2]
                movie_original_title = result[3]
                movie = [movie_title, movie_description, movie_original_title, directors]
                # Put all of the movies that are currently playing into a list.
                movies += [movie] 
            
            # Display NOW PLAYING movies with the info asked.
            for movie in movies:
                print(movie)
                print("\n")
        except Exception  as e:
            logger.error ("Error %d: %s" % (e.args[0], e.args[1])) 
        
        logger.info("Printed available movies found at greek cinemas")
        return 

    def run_all(self):
        self.get_updates()
        self.display_current_movies()

        
    def calculateMethodRuntime(self, method_to_execute):
        start_time = time.time()
        method_to_execute()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Elapsed Time needed for completing the procedure was: " + str(elapsed_time))

def main(argv, pythonScript):
    help_command ="python" + str(pythonScript) + " [-r] [all|update|display]"
    method_run = None
    
    try:
        opts, args = getopt.getopt(argv,"hr:",["run="])
    except getopt.GetoptError:
        print (help_command)
        sys.exit(2)
    opts, args = getopt.getopt(argv,"hr:",["run="])
    if len(opts) == 0:
        print (help_command)
        sys.exit()        
    for opt, arg in opts:
        if opt == '-h':
            print (help_command)
            sys.exit()
        elif opt in ("-r", "--run"):
            if arg.lower() not in ('all', 'update', 'display'):
                print (help_command)
                sys.exit()
            method_run = arg.lower()

    if method_run is None:
        print (help_command)
        exit(1)


    # Opening JSON file
    config_file = open('configuration.conf')
    # returns JSON object as
    # a dictionary
    config_data = json.load(config_file)  
    #open text file in read mode
    logging.config.dictConfig(config_data)
    global logger 
    logger = logging.getLogger(__name__)
    logger.info(" config= " + str(config_data))
    
    db = MovieDatabaseHelper(config_data['host_name'], config_data['host_port'], config_data['user_name'], config_data['password'], config_data['database'], config_data)



    if (method_run is not None):
        if(method_run == 'all'):
            db.calculateMethodRuntime(db.run_all)
        elif(method_run == 'update'):
            db.calculateMethodRuntime(db.get_updates)
        elif(method_run == 'display'):
            db.calculateMethodRuntime(db.display_current_movies)
    
if __name__ == '__main__':  # If it's executed like a script (not imported)
    main(sys.argv[1:], sys.argv[0])
