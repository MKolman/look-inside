# Look Inside
An application to search for and view info about the DNA molecule. This is an Interview assignment for GenePlanet.

# Prerequisites
To run this repo you have to install Docker on your machine. See (official installation instructions here)[https://docs.docker.com/engine/install/].

Additionally, you will need docker-compose command which can be installed with aptitude
```
sudo apt install docker-compose
```

There are also data dependencies. In case you want to import data into the database you can fetch it using
```
wget https://gpgeno-reference-files.s3-eu-west-1.amazonaws.com/hg37variants1000g.vcf.gz
```

# Running the demo
```
docker-compose -f "docker-compose.yml" up -d --build
```
Navigate to port 5000 on the web docker container to see the page.