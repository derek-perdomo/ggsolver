1. Update __init__ with changelog and version. 
2. Update setup.py with any new packages, if any.
3. Update docker images. 
   1. Open windows terminal. 
   2. Run `docker login` and enter login, password. 
   3. From top-level ggsolver folder, run `python .\docker\rebuild.py`
4. Generate docs. 
   1. In `ggsolver-devel` container, run `make html` in `ggsolver/docs` folder.
   2. Check if all links open properly. Sphinx makes funny mistakes! 
   3. Copy the generated html to website's folder. 
   4. Git push the website. 
