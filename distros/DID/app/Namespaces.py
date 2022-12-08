import re
import requests
from rdflib import Graph

class NameSpaces():
    def __init__(self, url, debug=False):
        self.stats = {}
        self.json = {}
        self.stats = {}
        self.namespaces = {}
        self.DEBUG = debug
        self.content = requests.get(url)
        self.url = url
        self.processor(self.content)
        self.graph = False
        self.statements = {}
             
    def load_graph(self, url):
        self.graph = Graph()
        self.graph.parse(url, format='ttl')
        return self.graph

    def get_namespace(self, spacestring):
        namespacecheck = re.search(r"\@prefix\s+(\S+)\:\s+<(\S+)>", spacestring)
        if namespacecheck:
            self.namespaces[namespacecheck.group(2)] = namespacecheck.group(1)
        return self.namespaces
    
    def processor(self, content):
        data = content.text.split('\n')
        success = False
        for line in data:
            if '@prefix' in line:
                self.get_namespace(line)
                success = True
        return success

    def counter(self, concept):
        for namespace in self.namespaces:
            if namespace in concept:
                if self.DEBUG:
                    print(self.namespaces[namespace])
                if self.namespaces[namespace] in self.stats:
                    self.stats[self.namespaces[namespace]] = self.stats[self.namespaces[namespace]] + 1
                else:
                    self.stats[self.namespaces[namespace]] = 1
        return self.stats
    
    def getstats(self):
        return self.stats
    
    def getnamespaces(self):
        return self.namespaces
    
    def getstatements(self):
        lines = 0
        knowns = {}
        knowno = {}
        knownp = {}
        data = {}
        for s1, p1, o1 in self.load_graph(self.url):
            s = "%s" % s1
            p = "%s" % p1
            o = "%s" % o1
            self.counter(s)
            self.counter(p)
            self.counter(o)
            lines = lines + 1
            if not s in knowns:
                knowns[s] = 1
                if not 'subjects' in data:
                    data['subjects'] = 1
                else:
                    data['subjects'] = data['subjects'] + 1
            if not p in knownp:
                knownp[p] = 1
                if not 'predicates' in data:
                    data['predicates'] = 1
                else:
                    data['predicates'] = data['predicates'] + 1
            if not o in knowno:
                knowno[o] = 1
                if not 'objects' in data:
                    data['objects'] = 1
                else:
                    data['objects'] = data['objects'] + 1

        self.statements['statements'] = lines
        self.statements['unique objects'] = data['objects']
        self.statements['unique predicates'] = data['predicates']
        self.statements['unique subjects'] = data['subjects']
#        self.statements['unique literals'] = s['literals']

        return self.statements

