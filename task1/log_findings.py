import logging
import logging.config
import json
import sys, getopt
import time

class Helper():
            
    def __init__(self, config_data):
        try:
            self.config_data = config_data
        except Exception  as e:
            logger.error ("Error %d: %s" % (e.args[0], e.args[1]))

    def get_404_URLs(self):
        # Create a dictionary with the URLs that cannot be found
        dictionary_404_URLs = dict()

        try:
            with open(self.config_data['file_to_read'], 'r' , encoding='utf-8') as file:
                log_lines = file.readlines()
                # Process each line 
                for line in log_lines:
                    if("heroku/router" in line and "status=404" in line):
                        # We concentrate on the lines that include heroku/router and status=404
                        after_path = line.split("path=\"")[1]
                        path_name = after_path.split("\"")[0]
                        after_host = after_path.split("host=")[1]
                        host_name = after_host.split(" ")[0]
                        # We isolate the path and the host name to create the url name
                        url_name = host_name + path_name
                        if (url_name not in dictionary_404_URLs):
                            dictionary_404_URLs[url_name] = 1
                        else:
                            dictionary_404_URLs[url_name] += 1
        except Exception  as e:
            logger.error ("Error %d: %s" % (e.args[0], e.args[1]))   
        print(dictionary_404_URLs)
        return 
    
    def get_avg_response_time(self):
        total_response_time = 0
        counter = 0 # Counts the requests

        try:
            with open(self.config_data['file_to_read'], 'r' , encoding='utf-8') as file:
                log_lines = file.readlines()
                # Process each line 
                for line in log_lines:
                    # We take into account only the successful transactions
                    if("status=2" in line or "status=3" in line):
                        counter +=1
                        # There is a different logic in calculating the response time when it is a heroku/router request and when it is an app/web
                        if("heroku/router" in line):
                            connect_path = line.split("connect=")[1]
                            connect_time = float(connect_path.split("ms")[0])
                            after_connect = connect_path.split("service=")[1]
                            service_time = float(after_connect.split("ms")[0])
                            total_time = connect_time + service_time
                        elif("app/web" in line):
                            duration_path = line.split("duration=")[1]
                            duration_time = float(duration_path.split(" ")[0])
                            total_time = duration_time
                        total_response_time += total_time
        except Exception  as e:
            logger.error ("Error %d: %s" % (e.args[0], e.args[1]))   
        avg_response_time = total_response_time / counter
        print("Average response time is: " + str(avg_response_time) + " ms")
        return 
    
    def get_most_freq_db_table(self):
        dictionary_db_tables = dict()

        try:
            with open(self.config_data['file_to_read'], 'r' , encoding='utf-8') as file:
                log_lines = file.readlines()
                # Process each line 
                for line in log_lines:
                    # These are the keywords where we will find the table as the next word following
                    for keyword in ["FROM", "UPDATE", "INTO", "JOIN"]:
                        if( keyword in line):
                            after_path = line.split(keyword + " ")[1]
                            while True:
                                table_name = after_path.split(" ")[0]
                                table_name = table_name.split('\x1b')[0]
                                
                                cleaned_table_name = table_name.replace("\"", "")
                                # Isolate the table name and if SELECT is the following word go to next iteration or break if no table name is following
                                if( "SELECT" in table_name):
                                    if(keyword not in after_path):
                                        break
                                    continue
                                # Check that is a lowercase table and not just parentheses (common after updates)
                                if (any(ord(char) >= 97 and ord(char) <= 122 for char in cleaned_table_name)):
                                    if (cleaned_table_name not in dictionary_db_tables):
                                        dictionary_db_tables[cleaned_table_name] = 1
                                    else:
                                        dictionary_db_tables[cleaned_table_name] += 1
                                if(keyword not in after_path):
                                    break
                                else:
                                    after_path = after_path.split(keyword)[1]
                            
        except Exception  as e:
            logger.error ("Error %d: %s" % (e.args[0], e.args[1]))   

        sorted_items = sorted(dictionary_db_tables.items(), key=lambda x: x[1], reverse=True)
        print(sorted_items)
        return 
    
    def get_server_errors(self):
        counter = 0

        try:
            with open(self.config_data['file_to_read'], 'r' , encoding='utf-8') as file:
                log_lines = file.readlines()
                # Process each line 
                for line in log_lines:
                    # Find all lines where a server error has occured. 
                    if("status=5" in line):
                        counter +=1
        except Exception  as e:
            logger.error ("Error %d: %s" % (e.args[0], e.args[1]))   
        print("Server errors: " + str(counter))
        return 

    def run_all(self):
        
        self.get_404_URLs()
        self.get_avg_response_time()
        self.get_most_freq_db_table()
        self.get_server_errors()
      


        
    def calculateMethodRuntime(self, method_to_execute):
        start_time = time.time()
        method_to_execute()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Elapsed Time needed for completing the procedure was: " + str(elapsed_time))

def main(argv, pythonScript):
    help_command = str(pythonScript) + " [-r] [all]"
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
            if arg.lower() not in ('all'):
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

    db = Helper(config_data)

    if (method_run is not None):
        if(method_run == 'all'):
            db.calculateMethodRuntime(db.run_all)
    
if __name__ == '__main__':  # If it's executed like a script (not imported)
    main(sys.argv[1:], sys.argv[0])


