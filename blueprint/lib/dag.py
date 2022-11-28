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

from collections import defaultdict

class BlueprintGraph():
    def __init__(self, module_count):
        self.dag = defaultdict(list)
        self.module_count = module_count

    def addEdge(self, source, dest):
        if not (dest in self.dag[source]):
            self.dag[source].append(dest)

    def findCyclicDependency(self, module, visited_module, recursion_stack):
        visited_module[module] = True     # Mark current module as visited
        recursion_stack[module] = True    # Adds module to the recursion stack

        # the graph is cyclic, if any neighbour is already visited or in the recursion_stack
        for neighbour in self.dag[module]:
            if neighbour in visited_module.keys() and visited_module[neighbour] == False:
                # if self.findCyclicDependency(neighbour, visited_module, recursion_stack) == True:
                path = self.findCyclicDependency(neighbour, visited_module, recursion_stack)
                if path != None :
                    path.append((module, neighbour))
                    return path # True
            elif neighbour in recursion_stack.keys() and recursion_stack[neighbour] == True:
                return [(module, neighbour)] #True

        # Pop the node from recursion_stack
        recursion_stack[module] = False
        return None # False

    # Returns true: BlueprintGraph is cyclic
    def isCyclic(self):
        nodes = self.dag.keys()
        visited_module = {}
        recursion_stack = {}
        for node in nodes:
            visited_module[node] = False
            recursion_stack[node] = False
        for node in nodes:
            if visited_module[node] == False:
                path = self.findCyclicDependency(node, visited_module, recursion_stack)
                if path != None:
                    return True
        return False

    # Returns true: BlueprintGraph is cyclic
    def getCyclicPath(self):
        nodes = self.dag.keys()
        visited_module = {}
        recursion_stack = {}
        for node in nodes:
            visited_module[node] = False
            recursion_stack[node] = False
        for node in nodes:
            if visited_module[node] == False:
                path = self.findCyclicDependency(node, visited_module, recursion_stack)
                if path != None:
                    return path[::-1]
        return []


# g = BlueprintGraph(4)
# g.addEdge("a", "b")
# g.addEdge("a", "c")
# g.addEdge("b", "c")
# g.addEdge("c", "a")
# g.addEdge("b", "d")
# g.addEdge("d", "d")
# g.addEdge(0, 1)
# g.addEdge(0, 2)
# g.addEdge(1, 2)
# g.addEdge(2, 0)
# g.addEdge(2, 3)
# g.addEdge(3, 3)
# if g.isCyclic() == 1:
#     print("Graph contains cycle")
# else:
#     print("Graph doesn't contain cycle")

# print(g.getCyclicPath())