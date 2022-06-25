# a reminder command for creating/running the dev env
sudo docker run -ti --rm --name lbdev --network="host" -v (pwd):/usr/src/app lbdev /bin/bash
