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

from typing import List
from enum import Enum
import json
from prettytable import PrettyTable


BPError   = int(0)
BPWarning = int(1)
BPInfo    = int(2)
BPDebug   = int(3)

class ValidationEvent(dict):
    yaml_tag = u'!ValidationEvent'

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
        
    def toJson(self):
        ret_str = '{'
        if self.level == BPError: 
            ret_str += '"level" : "error", '
        elif self.level == BPWarning:
            ret_str += '"level" : "warning", '
        elif self.level == BPInfo:
            ret_str += '"level" : "info", '
        else:
            ret_str += '"level" : "debug", '
        
        ret_str += '"message" : "' + str(self.message) + '", '
        if self.evidence != None:
            ret_str += '"evidence" : ' + (str(self.evidence)).replace("'", '"') 
        # if self.context != None:
        #     ret_str += '"context" : "' + str(self.context) + '", '
        
        ret_str += '}'
        return ret_str


##====================================================================##

class Format(Enum):
    Table = 'table'
    Json = 'json'

def format_events(events:List[ValidationEvent] = [], format = Format.Table) -> str:
    if len(events) == 0:
        return "{'msg': 'Empty, no events'}"
    
    errors = []
    warnings = []
    infos = []
    debugs = []

    for e in events:
        if e.level == BPError:
            errors.append(e)
        elif e.level == BPWarning:
            warnings.append(e)
        elif e.level == BPInfo:
            infos.append(e)
        else:
            debugs.append(e)

    ret_str = ''
    if format == Format.Table:
        ret_str += f'Errors: {len(errors)}  Warnings: {len(warnings)}  Info: {len(infos)}  Debug: {len(debugs)}'
        ret_str += '\n'
        if len(errors) > 0:
            ret_str += "\n-----------------------------\n"
            ret_str += f'  Error count: {len(errors)}'
            ret_str += "\n=============================\n"
            t = PrettyTable(['T', 'Message', 'Evidence', 'Context'])
            t.align = 'l'
            for e in errors:
                ctx_str = '' if e.context==None else str(e.context)
                context_str = (ctx_str[:40] + '..') if len(ctx_str) > 40 else ctx_str
                evd_str = '' if e.evidence==None else str(e.evidence)
                evidence_str = (evd_str[:40] + '..') if len(evd_str) > 40 else evd_str
                t.add_row(['E', e.message, evidence_str, context_str])
            ret_str += str(t)
            ret_str += '\n\n'

        if len(warnings) > 0:
            ret_str += "\n-----------------------------\n"
            ret_str += f'  Warning count: {len(warnings)}'
            ret_str += "\n=============================\n"
            t = PrettyTable(['T', 'Message', 'Context', 'Evidence'])
            t.align = 'l'
            for e in warnings:
                ctx_str = '' if e.context==None else str(e.context)
                context_str = (ctx_str[:40] + '..') if len(ctx_str) > 40 else ctx_str
                evd_str = '' if e.evidence==None else str(e.evidence)
                evidence_str = (evd_str[:40] + '..') if len(evd_str) > 40 else evd_str
                t.add_row(['E', e.message, evidence_str, context_str])
            ret_str += str(t)
            ret_str += '\n\n'

        if len(infos) > 0:
            ret_str += "\n-----------------------------\n"
            ret_str += f'  Info count: {len(infos)}'
            ret_str += "\n=============================\n"
            t = PrettyTable(['T', 'Message', 'Context', 'Evidence'])
            t.align = 'l'
            for e in infos:
                ctx_str = '' if e.context==None else str(e.context)
                context_str = (ctx_str[:40] + '..') if len(ctx_str) > 40 else ctx_str
                evd_str = '' if e.evidence==None else str(e.evidence)
                evidence_str = (evd_str[:40] + '..') if len(evd_str) > 40 else evd_str
                t.add_row(['E', e.message, evidence_str, context_str])
            ret_str += str(t)
            ret_str += '\n\n'

        if len(debugs) > 0:
            ret_str += "\n-----------------------------\n"
            ret_str += f'  Debug count: {len(debugs)}'
            ret_str += "\n=============================\n"
            t = PrettyTable(['T', 'Message', 'Context', 'Evidence'])
            t.align = 'l'
            for e in debugs:
                ctx_str = '' if e.context==None else str(e.context)
                context_str = (ctx_str[:40] + '..') if len(ctx_str) > 40 else ctx_str
                evd_str = '' if e.evidence==None else str(e.evidence)
                evidence_str = (evd_str[:40] + '..') if len(evd_str) > 40 else evd_str
                t.add_row(['E', e.message, evidence_str, context_str])
            ret_str += str(t)
            ret_str += '\n\n'
    
    elif format == Format.Json:
        # ret_str = json.dumps(errors + warnings + infos + debugs)

        ret_str = '{errors: ['
        if len(errors) == 0:
            ret_str += '],'
        else:
            for e in errors:
                ret_str += e.toJson()
                ret_str += ', '
            ret_str += ']'

        ret_str = ', warnings: ['
        if len(warnings) == 0:
            ret_str += '],'
        else: 
            for e in warnings:
                ret_str += e.toJson()
                ret_str += ', '
            ret_str += ']'

        ret_str = ', infos: ['
        if len(infos) == 0:
            ret_str += '],'
        else: 
            for e in infos:
                ret_str += e.toJson()
                ret_str += ', '
            ret_str += ']'

        ret_str = ', debugs: ['
        if len(debugs) == 0:
            ret_str += '],'
        else: 
            for e in debugs:
                ret_str += e.toJson()
                ret_str += ', '
            ret_str += ']'

        ret_str += '}'

    return ret_str
