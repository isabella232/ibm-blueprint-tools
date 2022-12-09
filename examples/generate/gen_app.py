import sys
import os
from os.path import exists

from blueprint.lib import event
from blueprint.schema import blueprint

from bp_basic import blueprint_manifest

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

#======================================================================
def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)
#======================================================================
def main(argv):

    bp, errors = blueprint_manifest()

    while True:
        print("\n MENU")
        print("============================")
        print("1. validate()")
        print("2. to_yaml_str()")
        print("3. generate_input_file()")
        print("4. from_yaml_str()")
        print("5. exit")
        print("============================")

        menu_choice = int(input("\nEnter the choice: "))
        
        if menu_choice == 1:
            errors = bp.validate(event.BPWarning)
            if len(errors) == 0:
                print("No validation errors !\n")
            else:
                print("Found validation errors !\n")
                eprint(errors)
        
        elif menu_choice == 2:
            bpyaml = bp.to_yaml_str()
            print(bpyaml)
        
        elif menu_choice == 3:
            sample_inputs = bp.generate_input_file()
            print(sample_inputs)
        
        elif menu_choice == 4:
            while True:
                filename = input("\nBlueprint file name (with path): ")
                if filename == 'quit':
                    break
                file_exists = os.path.exists(filename)
                if file_exists:
                    print("Loading blueprint file " + filename + " ...")
                    with open(filename) as f:
                        yaml_str = f.read()
                        bp = blueprint.Blueprint.from_yaml_str(yaml_str)
                    print("Success loading blueprint file " + filename + ". \nValidating ...")
                    errors = bp.validate(event.BPWarning)
                    if len(errors) == 0:
                        print("No validation errors !\n")
                    else:
                        print("Found validation errors !\n")
                        eprint(errors)
                    break
                else:
                    print("Blueprint file does not exist\n Try again, or type \'quit\'")
        
        else:
            print("Exiting menu ...\n")
            break

if __name__ == "__main__":
   main(sys.argv[1:])
