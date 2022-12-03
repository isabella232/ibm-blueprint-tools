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

import os
from git import Repo
import giturlparse
from pathlib import Path
import shutil

class GitDownloadTemplate:
    def __init__(self, git_url, mod_name):
        self.git_url = git_url
        self.mod_name = mod_name

        cwd = os.getcwd()
        d = Path(os.path.join(cwd, mod_name))
        if d.exists() and d.is_dir():
            shutil.rmtree(d)

        p = giturlparse.parse(git_url)
        if p.resource != None:
            new_git_url = git_url[0:git_url.find(p.resource)]
        else:
            new_git_url = git_url
        # print(mod_name)
        
        # Clone all the files from the git repo
        Repo.clone_from(new_git_url, mod_name)
        self.working_dir = os.path.join(Path(cwd), mod_name)

        # Remove unnecessary files from the cloned git repo (in the local file-system)
        files = os.listdir(self.working_dir)
        for f in files:
            if f != str(p.name):
                d = Path(os.path.join(cwd, mod_name, f))
                if d.exists() and d.is_dir():
                    # TODO: Don't remove the .terraform folder & .terraform.lock.hcl file
                    shutil.rmtree(d)
                if d.exists() and d.is_file():
                    # TODO: Don't remove the blueprint.tfstate & blueprint.tfvars files
                    os.remove(d)
        self.working_dir = os.path.join(Path(cwd), mod_name, p.name)
        os.chdir(cwd)

    def get_working_dir(self):
        return self.working_dir
    