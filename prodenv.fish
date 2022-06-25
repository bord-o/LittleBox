# reminder commands for creating/running the containers

sudo docker run -ti --rm --name lbapp -p 8000:8000 mklbapp /bin/bash
sudo docker run  --rm --name lbdb -p 5432:5432  -d mklbdb 
