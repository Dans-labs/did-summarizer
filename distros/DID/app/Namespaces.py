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

    def getnamespaces(self, s):
        for ns in self.namespaces:
            if ns in s:
                return self.namespaces[ns]
        return

    def counterstats(self, ns1, istats):
        if ns1:
            if ns1 in istats:
                #print(istats[ns1])
                istats[ns1] = istats[ns1] + 1
            else:
                istats[ns1] = 1
            return istats
        return 

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
    
    def getnamespace(self):
        return self.namespaces
    
    def getstatements(self):
        lines = 0
        globalstats = {}
        subjects = {}
        objects = {}
        predicates = {}
        knowns = {}
        knowno = {}
        knownp = {}
        data = {}
        for s1, p1, o1 in self.load_graph(self.url):
            s = "%s" % s1
            p = "%s" % p1
            o = "%s" % o1
            ns1 = self.getnamespaces(s)
            ns2 = self.getnamespaces(p)
            ns3 = self.getnamespaces(o)
            if ns1:
                if 'subjects' in globalstats:
                    subjects = globalstats['subjects']
                    subjects =self.counterstats(ns1, subjects)
                    globalstats['subjects'] = subjects
                else:
                    subjects = {}
                    subjects =self.counterstats(ns1, subjects)
                globalstats['subjects'] = subjects
            else:
                if not 'subjects' in globalstats:
                    globalstats['subjects'] = {}
                if 'literals' in globalstats['subjects']:
                    globalstats['subjects']['literals'] = globalstats['subjects']['literals'] + 1
                else:
                    globalstats['subjects']['literals'] = 1
                
            if ns2:
                if 'predicates' in globalstats:
                    predicates = globalstats['predicates']
                    predicates =self.counterstats(ns2, predicates)
                    #globalstats['p'] = predicates
                else:
                    predicates = {}
                    predicates =self.counterstats(ns2, predicates)
                globalstats['predicates'] = predicates
            else:
                if not 'predicates' in globalstats:
                    globalstats['predicates'] = {}
                if 'literals' in globalstats['predicates']:
                    globalstats['predicates']['literals'] = globalstats['predicates']['literals'] + 1
                else:
                    globalstats['predicates']['literals'] = 1
                    
            if ns3:
                if 'objects' in globalstats:
                    objects = globalstats['objects']
                    objects =self.counterstats(ns3, objects)
                    #globalstats['o'] = objects
                else:
                    objects = {}
                    objects =self.counterstats(ns3, objects)
                globalstats['objects'] = objects
            else:
                if not 'objects' in globalstats:
                    globalstats['objects'] = {}
                if 'literals' in globalstats['objects']:
                    globalstats['objects']['literals'] = globalstats['objects']['literals'] + 1
                else:
                    globalstats['objects']['literals'] = 1

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
        self.statements['objects'] = data['objects']
        self.statements['predicates'] = data['predicates']
        self.statements['subjects'] = data['subjects']
        self.statements['statements'] = globalstats
#        self.statements['unique literals'] = s['literals']

        return self.statements

