import sys
import getopt

from blueprint.validate.validator import Validator

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

def main(argv):
   input_file = ''
   try:
      opts, args = getopt.getopt(argv,"hi:",["ifile="])
   except getopt.GetoptError:
      print('validate.py -i <input_file>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('validate.py -i <input_file>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         input_file = arg
   
   Validator(input_file)

if __name__ == "__main__":
   main(sys.argv[1:])