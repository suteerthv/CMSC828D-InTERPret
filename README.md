# CMSC828D-FinalProject
This is the online repository that contains the necessary filese for the final projct for CMSC828D 

## Setup

To run this you need three dependencies `vagrant`

Once `vagrant` is installed, you can use it to set up the database. 
Run `vagrant up`, in the project root, to create a new container that will hold the PostgreSQL database. 

_Note_: if you have a vagrant setup that has gotten corrupeted, run `vagrant suspend && vagrant destroy -f` to delete the corrupted container. Then run `vagrant up` again. 

Once Installed go to the project root and run the following commands: docker-machine create default

```bash
python3 src/parse_xml.py "Mitzpeh" << path to mitzpeh Issue_metadata.csv >> 
python3 src/parse_xml.py "Black Explosion" <<path to black explosion Issue_metadata.csv>>
```

repticate the above steps adjusted to your preferred shell and the location of your data.

