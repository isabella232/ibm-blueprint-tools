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

def val_type(val) -> str:
    if val == None:
        return 'unknown'
    elif isinstance(val, str):
        return 'string'
    elif isinstance(val, int):
        return 'integer'
    elif isinstance(val, float):
        return 'float'
    elif isinstance(val, bool):
        return 'bool'
    elif isinstance(val, list):
        return 'list'
    elif isinstance(val, dict):
        return 'map'
    else:
        return 'unknown'

def is_val_type(val, type) -> bool:
    if val == None:
        if type == 'unknown':
            return True    
        else:
            return False
    if isinstance(val, str):
        if type == 'string':
            return True    
        else:
            return False
    if isinstance(val, int):
        if type == 'integer':
            return True
        else:
            return False
    if isinstance(val, float):
        if type == 'float':
            return True
        else:
            return False
    if isinstance(val, bool):
        if type == 'bool':
            return True
        else:
            return False
    if isinstance(val, list):
        if type.startswith('list'):
            return True
        else:
            return False
    if isinstance(val, dict):
        if type.startswith('map'):
            return True
        else:
            return False
    return False