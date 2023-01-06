# (C) Copyright IBM Corp. 2022.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

type_patterns_dict = [
    {
        "pattern":"endswith", 
        "snippets":["_name", "name"],
        "type":"string"
    },{
        "pattern":"endswith", 
        "snippet":["_id", "guid", "resource_id", "instance_id"],
        "type":"string"
    },{
        "pattern":"endswith", 
        "snippet":["_crn"],
        "type":"string"
    },{
        "pattern":"endswith", 
        "snippet":["_resource_group", "_rg", "_group"],
        "type":"string"
    },{
        "pattern":"endswith", 
        "snippet":["_plan"],
        "type":"string"
    },{
        "pattern":"endswith", 
        "snippet":["_region", "location"],
        "type":"string"
    },{
        "pattern":"endswith", 
        "snippet":"count", 
        "type":"integer"
    }
]