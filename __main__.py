import os 
import sys 
import json
import shutil

if __name__ == "__main__":
	path = "/".join(os.path.dirname(__file__).split("/")[:-1])
	sys.path.append(path)
	import spider
	arg1 = sys.argv[1]
	if arg1 == "all":
		spider.run() 
	elif arg1 == "commit":
		spider.run_commit()
	elif arg1 == "debug":
		spider.debug = True
		spider.run_cat(sys.argv[2], sys.argv[3]) 
	elif arg1 == "test":
		spider.run_module_test(sys.argv[2], sys.argv[3]) 
	else: 
		spider.run_cat(sys.argv[1], sys.argv[2]) 

