import os
import sys
import getopt
import logging

from blueprint.run import bprunner

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

def main(argv):
   blueprint_file = ""
   input_data_file = ""
   working_dir = "./"
   try:
      opts, args = getopt.getopt(argv,"h:b:i:w:",["bpfile=","ifile=","wdir="])
   except getopt.GetoptError:
      print('run.py -b <blueprint_file> -i <input_data_file> -w <working_directory>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('run.py -b <blueprint_file> -i <input_data_file> -w <working_directory>')
         sys.exit()
      elif opt in ("-b", "--bpfile"):
         blueprint_file = arg
      elif opt in ("-i", "--ifile"):
         input_data_file = arg
      elif opt in ("-w", "--wdir"):
         working_dir = arg
   
   if blueprint_file == "" or input_data_file == "" :
      blueprint_file = os.environ['BLUEPRINT_FILE']
      input_data_file = os.environ['INPUT_DATA_FILE']
      working_dir = os.environ['WORKING_DIR']
      if blueprint_file == "" or input_data_file == "" :
         eprint("\nThe input blueprint_file, input_data_file and working_directory are mandatory.")
         eprint("Usage: \n\n  run.py -b <blueprint_file> -i <input_data_file> -w <working_directory>")
         return

   br = bprunner.BlueprintRunner(blueprint_file = blueprint_file, 
                                 input_data_file = input_data_file, 
                                 dry_run = True,
                                 working_dir = working_dir)
   e = br.init_modules()
   print("Init errors \n" + str(e))
   e = br.plan_modules()
   print("Plan errors \n" + str(e))
   e = br.apply_modules()
   print("Apply errors \n" + str(e))
   print(br.bp)
   print(br.module_data)

if __name__ == "__main__":
   main(sys.argv[1:])