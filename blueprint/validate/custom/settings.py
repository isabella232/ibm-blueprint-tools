# (C) Copyright IBM Corp. 2022.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from yamale.validators import Validator

class Settings(Validator):
    """ Custom validator """
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