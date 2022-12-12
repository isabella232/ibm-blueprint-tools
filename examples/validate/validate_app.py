import sys
import getopt

from blueprint.lib import bfile
from blueprint.lib import event
from blueprint.validate import schema_validator
from blueprint.validate import blueprint_validator

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
         bv = schema_validator.SchemaValidator(input_file)
         print("\Schema validation ... \n")
         (msg, err) = bv.validate()
         if err == None:
            print(msg)
         else:
            eprint(err)
            
         print("\nAdvanced validation ... \n")
         bp = bfile.FileHelper.load_blueprint(input_file)
         if bp == None:
            eprint("Error in loading the blueprint file")
            sys.exit()

         bpv = blueprint_validator.BlueprintValidator()
         errors = bpv.validate_blueprint(bp)
         if errors != None:
            # eprint(str(errors))
            eprint(event.format_events(errors, event.Format.Table))

         sys.exit()
      else:
         print('Usage:')
         print('   validate.py -b <input_file>')
         sys.exit()

   print('Usage:')
   print('   validate.py -b <input_file>')
   sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])