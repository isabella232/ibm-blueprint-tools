import getopt
import sys

from blueprint.merge import bpload

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

def main(argv):
   input_manifest_file = ''
   output_blueprint_file = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print('bpmerge.py -i <input_manifest_file> -o <output_blueprint_file>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('bpmerge.py -i <input_manifest_file>  -o <output_blueprint_file>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         input_manifest_file = arg
      elif opt in ("-o", "--ofile"):
         output_blueprint_file = arg
   
   if input_manifest_file == None or input_manifest_file == '':
      input_manifest_file = 'data-1/manifest.yaml'

   loader = bpload.BPLoader(input_manifest_file)
   errors = loader.get_errors()
   if len(errors) > 0:
      eprint(errors)
      return -1

   out_yaml_str = loader.to_yaml_str()

   if output_blueprint_file == None or output_blueprint_file == '':
      print(out_yaml_str)
   else:
      with open(output_blueprint_file, 'w') as yaml_file:
         yaml_file.write(out_yaml_str)

if __name__ == "__main__":
   main(sys.argv[1:])