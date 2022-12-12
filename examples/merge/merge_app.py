import getopt
import sys

from blueprint.merge import manifest

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
      opts, args = getopt.getopt(argv,"hb:o:",["bfile=","ofile="])
   except getopt.GetoptError:
      print('bpmerge.py -b <input_manifest_file> -o <output_blueprint_file>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('Usage:')
         print('  bpmerge.py -b <input_manifest_file>  -o <output_blueprint_file>')
         sys.exit()
      elif opt in ("-b", "--bfile"):
         input_manifest_file = arg
      elif opt in ("-o", "--ofile"):
         output_blueprint_file = arg
   
   # if input_manifest_file == None or input_manifest_file == '':
   #    input_manifest_file = './examples/merge/data-1/manifest.yaml'

   if len(input_manifest_file) == 0:
         print('Usage:')
         print('  bpmerge.py -b <input_manifest_file>  -o <output_blueprint_file>')
         sys.exit()

   bp_manifest = manifest.BlueprintManifest.from_yaml_file(input_manifest_file)
   (bp, errors) = bp_manifest.generate_blueprint()
   if len(errors) > 0:
      eprint(errors)

   (out_yaml_str, errors) = bp.to_yaml_str()
   if len(errors) > 0:
      eprint(errors)


   if output_blueprint_file == None or output_blueprint_file == '':
      print(out_yaml_str)
   else:
      with open(output_blueprint_file, 'w') as yaml_file:
         yaml_file.write(out_yaml_str)

if __name__ == "__main__":
   main(sys.argv[1:])