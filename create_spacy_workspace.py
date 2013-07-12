
from geoserver.catalog import Catalog

cat = Catalog("http://localhost:8080/geoserver/rest")
print cat.get_layers()
# cat.create_workspace("the best workspace", "http://example.com/")
# 
# d = cat.create_datastore("test datastore", "the best workspace")
# cat.save(d)
# 
# for s in cat.get_workspaces():
#     print s.name 
# 
# for s in cat.get_stores():
#     print s.workspace.name, s.name
