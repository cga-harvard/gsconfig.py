gsconfig.py
===========

gsconfig.py is a python library for manipulating a GeoServer instance via the GeoServer RESTConfig API. 

Installing
==========

For users: ``pip install gsconfig`` 

For developers: ``git clone git://github.com/dwins/gsconfig.py.git && cd gsconfig.py && python setup.py develop``
(`virtualenv <http://virtualenv.org/>`_ to taste.)

Getting Help
============
There is a brief manual at http://dwins.github.com/gsconfig.py/ .
If you have questions, please ask them on the GeoServer Users mailing list: http://geoserver.org/display/GEOS/Mailing+Lists .
Please use the Github project at http://github.com/dwins/gsconfig.py for any bug reports (and pull requests are welcome, but please include tests where possible.)

Sample Layer Creation Code
==========================

.. code-block::

    from geoserver.catalog import Catalog
    cat = Catalog("http://localhost:8080/geoserver/")
    topp = self.cat.get_workspace("topp")
    shapefile_plus_sidecars = shapefile_and_friends("states")
    # shapefile_and_friends should look on the filesystem to find a shapefile
    # and related files based on the base path passed in
    #
    # shapefile_plus_sidecars == {
    #    'shp': 'states.shp',
    #    'shx': 'states.shx',
    #    'prj': 'states.prj',
    #    'dbf': 'states.dbf'
    # }
    
    # 'data' is required (there may be a 'schema' alternative later, for creating empty featuretypes)
    # 'workspace' is optional (GeoServer's default workspace is used by... default)
    # 'name' is required
    ft = self.cat.create_featuretype(name, workspace=topp, data=shapefile_plus_sidecars)

Running Tests
=============

Since the entire purpose of this module is to interact with GeoServer, the test suite is mostly composed of `integration tests <http://en.wikipedia.org/wiki/Integration_testing>`_.  
These tests necessarily rely on a running copy of GeoServer, and expect that this GeoServer instance will be using the default data directory that is included with GeoServer.
This data is also included in the GeoServer source repository as ``/data/release/``.
In addition, it is expected that there will be a postgres database available at ``postgres:postgres@localhost:5432/db``.
You can test connecting to this database with the ``psql`` command line client by running ``$ psql -d db -Upostgres -h localhost -p 5432`` (you will be prompted interactively for the password.)

Here are the commands that I use to reset before running the gsconfig tests::

   $ cd ~/geoserver/src/web/app/
   $ PGUSER=postgres dropdb db 
   $ PGUSER=postgres createdb db -T template_postgis
   $ git clean -dxff -- ../../../data/release/
   $ git checkout -f
   $ MAVEN_OPTS="-XX:PermSize=128M -Xmx1024M" \
   GEOSERVER_DATA_DIR=../../../data/release \
   mvn jetty:run

At this point, GeoServer will be running foregrounded, but it will take a few seconds to actually begin listening for http requests.
You can stop it with ``CTRL-C`` (but don't do that until you've run the tests!)
You can run the gsconfig.py tests with the following command::

  $ python setup.py test
