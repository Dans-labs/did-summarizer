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
        return
             
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
        for s, p, o in self.load_graph(self.url):
            self.counter("%s" % s)
            self.counter("%s" % p)
            self.counter("%s" % o)
            lines = lines + 1
        return lines

