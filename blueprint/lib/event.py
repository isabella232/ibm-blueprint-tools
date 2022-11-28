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

BPError   = int(0)
BPWarning = int(1)
BPInfo    = int(2)
BPDebug   = int(3)

class ValidationEvent:

    def __init__(self, level=BPError, message="Blueprint error", context=None, evidence=None, chain=None):
        self.level = level # 0: BPError, 1: BPWarning, 2:Info, 3:Debug
        if(level > BPDebug):
            self.level = BPDebug
        self.message = message
        self.context = context
        self.evidence = evidence
        self.chain = chain
        
    def __str__(self):
        if self.level == BPError:
            return f'\nBPError: {self.message}: \n>>Evidence: {self.evidence},\n>>Chain: {self.chain}\n'
        elif self.level == BPWarning:
            return f'\nBPWarning: {self.message}: \n>>Evidence: {self.evidence},\n>>Chain: {self.chain}\n'
        elif self.level == BPInfo:
            return f'\nBPInfo: {self.message}: \n>>Evidence: {self.evidence},\n>'
        elif self.level == BPDebug:
            return f'\nBPDebug: {self.message}: \n>>Context: {self.context}\n >>Evidence: {self.evidence}\n'

    def __repr__(self):
        return self.__str__()
        
##====================================================================##
