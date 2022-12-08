import os
import sys
import getopt
import logging

from blueprint.circuit import draw
from blueprint.lib import dag

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

def main(argv):
   blueprint_file = ""
   try:
      opts, args = getopt.getopt(argv,"h:b:",["bpfile="])
   except getopt.GetoptError:
      print('draw.py -b <blueprint_file>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('draw.py -b <blueprint_file>')
         sys.exit()
      elif opt in ("-b", "--bpfile"):
         blueprint_file = arg
   
   if blueprint_file == "":
      blueprint_file = os.environ['BLUEPRINT_FILE']
      if blueprint_file == "":
         eprint("\nThe input blueprint_file is mandatory.")
         eprint("Usage: \n\n  draw.py -b <blueprint_file>")
         return

   br = draw.BlueprintDraw(blueprint_file = blueprint_file)
   br.draw()

if __name__ == "__main__":
   main(sys.argv[1:])