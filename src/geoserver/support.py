import logging
from xml.etree.ElementTree import TreeBuilder, tostring
from tempfile import mkstemp
from zipfile import ZipFile


logger = logging.getLogger("gsconfig.support")

FORCE_DECLARED = "FORCE_DECLARED"
"""
The projection handling policy for layers that should use coordinates
directly while reporting the configured projection to clients.  This should be
used when projection information is missing from the underlying datastore.
"""

FORCE_NATIVE = "FORCE_NATIVE"
"""
The projection handling policy for layers that should use the projection
information from the underlying storage mechanism directly, and ignore the
projection setting.
"""

REPROJECT = "REPROJECT"
"""
The projection handling policy for layers that should use the projection
information from the underlying storage mechanism to reproject to the
configured projection.
"""


class ResourceInfo(object):
  """A base class for all resource types managed by the catalog """

  save_method = "PUT"
  """The HTTP method to use when saving this object"""

  resource_type = 'abstractResourceType'
  """A string identifier for the *type* of resource, such as layer or style"""

  def get_url(self, base):
      return self.href

  def update(self):
    self.metadata = self.catalog.get_xml(self.href)
    if self.metadata is None:
        raise Exception("no xml found at " + self.href)
    name = self.metadata.find('name')
    self.name = name.text if name is not None else None

  def delete(self):
    raise NotImplementedError()

  def serialize(self):
    builder = TreeBuilder()
    builder.start(self.resource_type, dict())
    self.encode(builder)
    builder.end(self.resource_type)
    return tostring(builder.close())

  def encode(self, builder):
    """
    Add appropriate XML nodes to this object.  The builder will be passed in
    ready to go, with the appropriate top-level node already added.
    """
    pass

def prepare_upload_bundle(name, data):
    """GeoServer's REST API uses ZIP archives as containers for file formats such
  as Shapefile and WorldImage which include several 'boxcar' files alongside
  the main data.  In such archives, GeoServer assumes that all of the relevant
  files will have the same base name and appropriate extensions, and live in
  the root of the ZIP archive.  This method produces a zip file that matches
  these expectations, based on a basename, and a dict of extensions to paths or
  file-like objects. The client code is responsible for deleting the zip
  archive when it's done."""
    handle, f = mkstemp() # we don't use the file handle directly. should we?
    if 'shp' in data:
        zip = ZipFile(f, 'w')
        for ext, stream in data.iteritems():
            fname = "%s.%s" % (name, ext)
            if (isinstance(stream, basestring)):
                zip.write(stream, fname)
            else:
                zip.writestr(fname, stream.read())
        zip.close()
    elif 'zip' in data: #Assume it's a zipfile
        """Create ZipFile object from uploaded data """
        oldf = open(data['zip'], 'r')
        oldzip = ZipFile(oldf)

        """New zip file"""
        noo = open(f, "wb")
        newzip = ZipFile(f, "w")

        """Get the necessary files from the uploaded zip, and add them to the new zip
        with the desired layer name"""
        zipFiles = oldzip.namelist()
        files = ['.shp', '.prj', '.shx', '.dbf']
        fname = "%s" % (name)
        for file in zipFiles:
            ext = file[-4:].lower()
            if ext in files:
                files.remove(ext) #OS X creates hidden subdirectory with garbage files having same extensions; ignore.
                logger.debug("================Write [%s].[%s]", fname, ext)
                newzip.writestr(name + ext, oldzip.read(file))
    return f

def atom_link(node):
    if 'href' in node.attrib:
        return node.attrib['href']
    else:
        l = node.find("{http://www.w3.org/2005/Atom}link")
        return l.get('href')

def atom_link_xml(builder, href):
    builder.start("atom:link", {
        'rel': 'alternate',
        'href': href,
        'type': 'application/xml',
        'xmlns:atom': 'http://www.w3.org/2005/Atom'
    })
    builder.end("atom:link")

def bbox(node):
    if node is not None:
        minx = node.find("minx")
        maxx = node.find("maxx")
        miny = node.find("miny")
        maxy = node.find("maxy")
        crs  = node.find("crs")
        crs  = crs.text if crs is not None else None

        if (None not in [minx, maxx, miny, maxy]):
            return (minx.text, maxx.text, miny.text, maxy.text, crs)
        else:
            return None
    else:
        return None

def bbox_xml(builder, bbox):
    minx, maxx, miny, maxy, crs = bbox
    builder.start("minx", dict())
    builder.data(minx)
    builder.end("minx")
    builder.start("maxx", dict())
    builder.data(maxx)
    builder.end("maxx")
    builder.start("miny", dict())
    builder.data(miny)
    builder.end("miny")
    builder.start("maxy", dict())
    builder.data(maxy)
    builder.end("maxy")
    if crs is not None:
        builder.start("crs", {"class": "projected"})
        builder.data(crs)
        builder.end("crs")

