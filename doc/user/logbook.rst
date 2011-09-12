.. _user-logbook:

Dive Logbook
============
Kenozooid supports basic dive logbook functionality, which allows to list,
search, add and remove dives, buddies and dive sites.

.. _user-logbook-ls:

Listing and Searching
---------------------
Kenozooid supports dive, buddy and dive site listing and searching with
``dive list``, ``buddy list`` and ``site list`` commands.

Dives Listing
^^^^^^^^^^^^^
Dive list consists of the following columns

- number of a dive from a file
- date and time
- maximum depth
- duration in minutes
- minimum temperature

To list the dives from a dive computer backup file::

    $ kz dive list backup-ostc-20110728.uddf 
    backup-ostc-20110728.uddf:
        1: 2011-06-12 21:45     40.8m     58:50     5.4°C
        2: 2011-06-19 12:26     58.8m     48:40     6.2°C
        3: 2011-06-24 13:18     94.1m    107:20     5.1°C
        4: 2011-06-26 12:56     85.0m    104:42     5.5°C
        5: 2011-06-29 21:30     42.7m     57:29     6.2°C
        6: 2011-07-07 21:44     27.5m     60:38     7.0°C
        7: 2011-07-20 21:50     49.9m     65:42     5.7°C
        8: 2011-07-28 21:26     60.2m     64:08     5.7°C

Buddies Listing 
^^^^^^^^^^^^^^^
The buddy data list consists of

- buddy number from a file
- buddy id
- first name
- family name
- diving organization, i.e. CFT, PADI
- diving organization membership id

To list buddies::

    $ kz buddy list buddies.uddf
    buddies.uddf:
       1: tcora      Tom        Cora                  
       2: tex        Thelma     Ex                    
       3: jn         Johnny     Neurosis
       4: jk         John       Koval

Search string can be specified after the command to limit the list of
buddies

For example to find buddy with id ``jn``::

    $ kz buddy list jn buddies.uddf
    buddies.uddf:
       1: jn         Johnny     Neurosis

Buddies can be found by part of the name, i.e. (notice ``ohn``, could be
``John`` as well)::

    $ kz buddy list ohn examples/logbook/buddies.uddf 
    buddies.uddf:
       1: jn         Johnny     Neurosis 
       2: jk         John       Koval

Dive Sites Listing
^^^^^^^^^^^^^^^^^^
The dive site list consists of

- dive site number from a file
- dive site location
- dive site name

To list dive sites::

    $ kz site list sites.uddf                         
    sites.uddf:
       1: sckg       Scapa Flow           SMS Konig   
       2: sckn       Scapa Flow           SMS Koln
       3: scmk       Scapa Flow           SMS Markgraf
       4: bmlh       Baltimore            Lough Hyne
       5: hie        Howth                Ireland's Eye

As in case of buddy data, a dive site can be found by id::

    $ kz site list hie sites.uddf                         
    sites.uddf:
       1: hie        Howth                Ireland's Eye

To find dive sites by location name containing ``Scap`` string::

    $ kz site list Scap sites.uddf
    sites.uddf:
       1: sckg       Scapa Flow           SMS Konig   
       2: sckn       Scapa Flow           SMS Koln    
       3: scmk       Scapa Flow           SMS Markgraf

To find dive sites with name containing ``SMS`` string::

    $ kz site list SMS sites.uddf
    sites.uddf:
       1: sckg       Scapa Flow           SMS Konig   
       2: sckn       Scapa Flow           SMS Koln    
       3: scmk       Scapa Flow           SMS Markgraf


Adding Buddies and Dive Sites
-----------------------------
Adding buddies and dive sites to a logbook file is possible with ``buddy add``
and ``site add`` commands.

To add dive sites to a dive site or a logbook file::

    $ kz site add sckg 'Scapa Flow' 'SMS Konig' sites.uddf
    $ kz site add sckn 'Scapa Flow' 'SMS Koln' sites.uddf
    $ kz site add scmk 'Scapa Flow' 'SMS Markgraf' sites.uddf

    $ kz site list sites.uddf
    sites.uddf:
       1: sckg       Scapa Flow           SMS Konig   
       2: sckn       Scapa Flow           SMS Koln    
       3: scmk       Scapa Flow           SMS Markgraf

To add buddies to a buddy or a logbook file::

    $ kz buddy add tcora "Tom Cora" buddies.uddf
    $ kz buddy add tex "Thelma Ex" buddies.uddf 
    $ kz buddy add jn "Johnny Neurosis" buddies.uddf
    $ kz buddy add jk "John Koval" buddies.uddf

    $ kz buddy list buddies.uddf                  
    buddies.uddf:
       1: tcora      Tom        Cora                  
       2: tex        Thelma     Ex                    
       3: jn         Johnny     Neurosis       
       4: jk         Johnny     Koval       

If output file (``dives.uddf`` and ``buddies.uddf`` above) does not exist, then
it is created by Kenozooid. Before adding data to a file, Kenozooid creates
backup file with ``.bak`` extension, i.e. ``dives.uddf.bak``, ``buddies.uddf.bak``.

Of course, one logbook file (i.e. ``logbook.uddf``) can be used to store
dive sites and buddies information instead of two separate files. However,
it is easier to share buddies data only with friends and dive site list
with larger group of unknown people, when separate files are used.

Adding Dives
------------
.. basic data vs. profile data

Removing Data
-------------

.. vim: sw=4:et:ai
