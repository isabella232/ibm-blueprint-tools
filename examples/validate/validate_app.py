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
      opts, args = getopt.getopt(argv,"hb:",["bfile="])
   except getopt.GetoptError:
      print('validate.py -b <input_file>')
      sys.exit(2)
   
   for opt, arg in opts:
      if opt == '-h':
         print('Usage:')
         print('   validate.py -b <input_file>')
         sys.exit()
      elif opt in ("-b", "--bfile"):
         input_file = arg
         Validator(input_file)
         exit()
      else:
         print('Usage:')
         print('   validate.py -b <input_file>')
         sys.exit()

   print('Usage:')
   print('   validate.py -b <input_file>')
   sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])