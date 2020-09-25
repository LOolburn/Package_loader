import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import io

def load (url):
    with urllib.request.urlopen(url) as f:
        data = f.read()
    return data

def get_package_url(name):
    data = load("https://pypi.org/simple/%s/" % name)
    root = ET.fromstring(data)
    package_url = None
    for elem in root[1]:
        if elem.tag == "a":
            url = elem.attrib["href"]
            if ".whl" in url:
                package_url = url
    return package_url

def get_package_deps(url):
    data = load(url)
    obj = io.BytesIO(data)
    zipf = zipfile.ZipFile(obj)
    meta_path = [s for s in zipf.namelist() if "METADATA" in s][0]
    with zipf.open(meta_path) as f:
        meta = f.read().decode("utf-8")
    #    print(meta)
    deps = []
    for line in meta.split("\n"):
        line = line.replace(";", " ").split()
        if not line:
            break
        if line[0] == "Requires-Dist:" and "extra" not in line:
            deps.append(line[1])
    return deps

def get_graph(name):
    graph = {}
    def rec(name):
        print(name)
        graph[name] = set()
        url = get_package_url(name)
        if not url:
            return
        deps = get_package_deps(url)
        for d in deps:
            graph[name].add(d)
            if d not in graph:
                rec(d)
    rec(name)
    return graph

def graph_v(graph):
    lines = ["digraph sphinx {"]
    for v1 in graph:
        for v2 in graph[v1]:
            lines.append('"%s" -> "%s"' % (v1, v2))
    lines.append("}")
    return "\n".join(lines)


g = get_graph("sphinx")
print(graph_v(g))