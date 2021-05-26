## Guide for a regolith GUI

#### Overview
- This GUI is written with the help of PySimpleGUI (a wrapper for Tk inter) 
- The GUI uses the `SCHEMAS` class objects in `schemas.py` module for building the user interface. 
- A schema object should contain (recommendation comment : couple to schema.org standards):
    - description
    - type 
    - anyof_type (if no 'type')
    - required (opt. for 'dict')
    - schema (if type is 'dict')
- Filtration criteria need unique setup for each catalog

#### Usage
- window #1
    1. Set path to database
        1. Using local: set the path to `/rg-db-group/db`
    1. Select a desired catalog. 
    1. Export data from selected database 
- window #2
    1. Select filtration category and load
    1. Edit
    1. Save (#TODO - roundtrip + ask to add and commit current database with a msg + ask if to push to origin (set up an ssh))
    1. Create a PR 
- window when pressing [`->`] (=explore)
    1. shows nested dictionary or a list of dictionaries. For the latter it requires selection by the first key.
     
    
    