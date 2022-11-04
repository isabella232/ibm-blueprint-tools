from yamale.validators import Validator

class Settings(Validator):
    """ Custom Date validator """
    tag = 'settings'

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.validators = [val for val in args if isinstance(val, Validator)]

    def _is_valid(self, value):
        if value:
            found=False
            for i in value:
                if i['name'] == "TF_VERSION":
                    found=True
                    return True
            if found ==  False:
                return False
    
    def fail(self, value):
        # Called in case `_is_valid` returns False
        return 'TF_VERSION must be set in the settings.'