from operator import truediv
import yamale
import uuid
import re
from yamale.validators import DefaultValidators, Validator


class Settings(Validator):
    """ Custom Date validator """
    tag = 'settings'

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.validators = [val for val in args if isinstance(val, Validator)]

    def _is_valid(self, value):
        found=False
        for i in value:
            if i['name'] == "TF_VERSION":
                found=True
                return True
            
        if found ==  False:
            raise ValueError('TF_VERSION must be passed in the parent settings as well as module settings')

validators = DefaultValidators.copy()  # This is a dictionary
validators[Settings.tag]=Settings
schema = yamale.make_schema('./schema.yaml', validators=validators)

#example data sets
data = yamale.make_data('./detection-rule.yaml')
# data = yamale.make_data('./test-sample/test-rule1.yaml')
# data = yamale.make_data('./test-sample/test-rule2.yaml')
# data = yamale.make_data('./test-sample/test-rule3.yaml')

try:
    yamale.validate(schema, data)
    print('Blueprint Yaml Validation success! 👍')
except ValueError as e:
    print('Blueprint Yaml Validation failed!\n%s' % str(e))
    exit(1)
