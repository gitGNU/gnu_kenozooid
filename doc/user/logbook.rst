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
- dive number
- date and time
- maximum depth
- average depth
- duration in minutes
- minimum temperature

To list the dives from a logbook file or from a dive computer backup file::

    $ kz dive list logbook.uddf
    logbook.uddf:
        1:   14 2009-10-22 15:32     30.3m ( --- )     64:16    29.0°C
        2:   15 2010-10-29 06:02     29.4m ( --- )     61:30    26.7°C

Enumerating Dives
^^^^^^^^^^^^^^^^^
Dives can be enumerated with dive number by using ``dive enum`` command.

If a dive has no dive number assigned, then the dive listing shows ``--``
instead of a dive number::

    $ kz dive list logbook.uddf
    logbook.uddf:
        1:  --  2009-10-22 15:32     30.3m ( --- )     64:16    29.0°C
        2:  --  2010-10-29 06:02     29.4m ( --- )     61:30    26.7°C

To enumerate dives in a logbook file (or in multiple logbook files)::

    $ kz dive enum -ns 14 logbook.uddf
    $ kz dive list logbook.uddf
    logbook.uddf:
        1:   14 2009-10-22 15:32     30.3m ( --- )     64:16    29.0°C
        2:   15 2010-10-29 06:02     29.4m ( --- )     61:30    26.7°C

When dives are enumerated, the specific dives can be found with ``-n``
option. For example, enumerate all backup files first::

    $ kz dive enum backup-su-20110728.uddf backup-ostc-20110728.uddf
    $ kz dive list backup-su-20110728.uddf backup-ostc-20110728.uddf
    backup-su-20110728.uddf:
        1:    1 2009-09-19 13:25     12.0m ( --- )     02:50    15.5°C
    ...
      139:  139 2011-05-29 14:17     25.4m ( --- )     48:20     7.5°C
    backup-ostc-20110728.uddf:
        1:  140 2011-06-12 21:45     40.8m ( --- )     58:50     5.4°C
        2:  141 2011-06-19 12:26     58.8m ( --- )     48:40     6.2°C
    ...
        6:  145 2011-07-07 21:44     27.5m ( 8.4m)     60:38     7.0°C
        7:  146 2011-07-20 21:50     49.9m (19.6m)     65:42     5.7°C
        8:  147 2011-07-28 21:26     60.2m (20.9m)     64:08     5.7°C

Plot dive 139, 141, 145 and 146 (``-n`` option is used to find dives in all
files)::

    $ kz dive plot -n 139,141,145-146 backup-su-20110728.uddf backup-ostc-20110728.uddf


Buddies Listing 
^^^^^^^^^^^^^^^
The buddy data list consists of

- buddy number from a file
- buddy id
- first name
- family name
- diving organisation, i.e. CFT, PADI
- diving organisation membership id

To list buddies::

    $ kz buddy list logbook.uddf    
    logbook.uddf:
       1: tcora      Tom        Cora                 PADI  1374       
       2: tex        Thelma     Ex                    
       3: jn         Johnny     Neurosis             CFT   1370       
       4: jk         John       Koval                PADI  13676   

Search string can be specified after the command to limit the list of
buddies. The search string can be one of

- buddy id
- part of buddy name (first name, family name)
- organisation name, i.e. ``PADI``, ``CMAS``, ``CFT``
- organisation membership id

To find buddy by her or his name, i.e. ``John``::

    $ kz buddy list John logbook.uddf
    logbook.uddf:
       1: jn         Johnny     Neurosis             CFT   1370       
       2: jk         John       Koval                PADI  13676  

To find all ``PADI`` buddies::

    $ kz buddy list PADI logbook.uddf 
    logbook.uddf:
       1: tcora      Tom        Cora                 PADI  1374       
       2: jk         John       Koval                PADI  13676 

Dive Sites Listing
^^^^^^^^^^^^^^^^^^
The dive site list consists of

- dive site number from a file
- location (city, geographical area), i.e. ``Howth``, ``Scapa Flow``
- dive site name, i.e. 
- coordinates (longitude, latitude)

To list dive sites::

    $ kz site list logbook.uddf
    logbook.uddf:
       1: sckg       Scapa Flow           SMS Konig           
       2: sckn       Scapa Flow           SMS Koln            
       3: scmk       Scapa Flow           SMS Markgraf        
       4: bmlh       Baltimore            Lough Hyne            -9.29718000, 51.5008090
       5: hie        Howth                Ireland's Eye         -6.06416900, 53.4083170

The dive site listing can be searched with one of the search string

- id
- part of location, i.e. ``Scapa``
- part of name, i.e. ``Lough``

To find dive sites by location containing ``Scapa`` string::

    $ kz site list Scapa logbook.uddf
    logbook.uddf:
       1: sckg       Scapa Flow           SMS Konig   
       2: sckn       Scapa Flow           SMS Koln    
       3: scmk       Scapa Flow           SMS Markgraf

To find dive sites with name containing ``Lough`` string::

    $ kz site list Lough logbook.uddf
    logbook.uddf:
       1: bmlh       Baltimore            Lough Hyne            -9.29718000, 51.5008090


Adding Buddies and Dive Sites
-----------------------------
Adding buddies and dive sites to a logbook file is possible with ``buddy add``
and ``site add`` commands.

To add a dive site to a logbook file::

    $ kz site add bath Bathroom Bath logbook.uddf
    $ kz site list logbook.uddf      
    examples/logbook.uddf:
       1: sckg       Scapa Flow           SMS Konig           
       2: sckn       Scapa Flow           SMS Koln            
       3: scmk       Scapa Flow           SMS Markgraf        
       4: bmlh       Baltimore            Lough Hyne            -9.29718000, 51.5008090
       5: hie        Howth                Ireland's Eye         -6.06416900, 53.4083170
       6: bath       Bathroom             Bath 


To add a buddy to a logbook file::

    $ kz buddy add frog "John Froggy" logbook.uddf                     

    $ kz buddy list logbook.uddf     
    logbook.uddf:
       1: tcora      Tom        Cora                 PADI  1374       
       2: tex        Thelma     Ex                    
       3: jn         Johnny     Neurosis             CFT   1370       
       4: jk         John       Koval                PADI  13676      
       5: frog       John       Froggy 


If logbook file (``logbook.uddf`` above) does not exist, then it is created
by Kenozooid. Before adding data to a file, Kenozooid creates backup file
with ``.bak`` extension, i.e. ``logbook.uddf.bak``.

Adding and Copying Dives
------------------------
Kenozooid supports two modes of adding dives into logbook file

- adding basic dive data (date and time of dive, maximum depth, dive duration)
- copying dive data from another file (i.e. from dive computer backup file)

To add a dive use ``dive add`` command::

    $ kz dive add '2011-10-12 13:14' 32.5 51 logbook.uddf                              
    $ kz dive list logbook.uddf
    logbook.uddf:
        1:   14 2009-10-22 15:32     30.3m ( --- )     64:16    29.0°C
        2:   15 2010-10-29 06:02     29.4m ( --- )     61:30    26.7°C
        3:  --  2011-10-12 13:14     32.5m ( --- )     51:00 


To copy dives from a file use ``dive copy`` command. For example, to
add 4th dive from dive computer backup file to logbook file::

    $ kz dive copy -k 4 backup-ostc-20110728.uddf logbook.uddf
    $ kz dive list logbook.uddf
    logbook.uddf:
        1:   14 2009-10-22 15:32     30.3m ( --- )     64:16    29.0°C
        2:   15 2010-10-29 06:02     29.4m ( --- )     61:30    26.7°C
        3:  --  2011-06-26 12:56     85.0m (24.4m)    104:42     5.5°C

Removing Data
-------------
To remove a buddy or a dive site use ``buddy del`` or ``site del``
commands. Identify buddy or dive site to be removed with its id.

For example, to remove ``John Froggy`` buddy::

    $ kz buddy del frog logbook.uddf
    $ kz buddy list logbook.uddf
    logbook.uddf:
       1: tcora      Tom        Cora                 PADI  1374       
       2: tex        Thelma     Ex                    
       3: jn         Johnny     Neurosis             CFT   1370       
       4: jk         John       Koval                PADI  13676 


To remove ``Bathroom`` dive site::

    $ kz site del bath logbook.uddf
    $ kz site list logbook.uddf
    logbook.uddf:
       1: sckg       Scapa Flow           SMS Konig           
       2: sckn       Scapa Flow           SMS Koln            
       3: scmk       Scapa Flow           SMS Markgraf        
       4: bmlh       Baltimore            Lough Hyne            -9.29718000, 51.5008090
       5: hie        Howth                Ireland's Eye         -6.06416900, 53.4083170

.. vim: sw=4:et:ai
