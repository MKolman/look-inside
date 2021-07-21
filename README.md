# Look Inside
An application to search for and view info about the DNA molecule. This is an Interview assignment for GenePlanet.

## Web app
The web app is written in flask because it's a lightweight framework that handles a lot of boilerplate code for us. The app has two endpoints:
* `/` serves static HTML website
* `/api/search?q=rs123` that searches for genome data and has an optional `user` param which adds data for specific user.
It communicates with database using SQLAlchemy.

## Database
Database is PostgreSQL. It has two tables one got gene location data and one for individual genotype data. In total there are three indexes on the database:
* Gene locations
  * Index on RSID that can be used for fast prefix searches.
  * Combined on chromosome and gene's position on that chromosome
* Genotype
  * Combined index for user_id and RSID, which allows for fast fetches for user data of a specific gene.

## TODO

- [ ] Consult about data inconsistencies
    - multiple rows can have the same rsid
    - some rows have multiple rsids
    - some rows have longer alt and ref values
    - some genotype value columns are longer than just simple `x|y`
- [ ] Write tests
- [ ] Create CI with code style checks and tests
- [ ] Parallelize importing of data
- [ ] Use Postgres's COPY function to faster import data
- [ ] Authentication and authorization so that not every user can see all others


# Prerequisites
To run this repo you have to install Docker on your machine. See (official installation instructions here)[https://docs.docker.com/engine/install/].

Additionally, you will need docker-compose command which can be installed with aptitude
```
sudo apt install docker-compose
```

# Running the demo
```
docker-compose -f "docker-compose.yml" up -d --build
```
Navigate to port 5000 on the web docker container to see the page.

# Populate demo
You can run import commands locally by running flask CLI. To set it up in a virtualenv do:
```
python3.9 -m venv venv
source venv/bin/activate
set -o allexport
source database.conf
set -o allexport
export POSTGRES_HOST=localhost
export FLASK_APP=app.py
cd server
flask import --help
```
## Gene locations
There are also data dependencies. In case you want to import data into the database you can fetch it and then import it using
```
wget https://gpgeno-reference-files.s3-eu-west-1.amazonaws.com/hg37variants1000g.vcf.gz
flask import genome
```
Import genome has a few options to define its behavior.
```
Usage: flask import genome [OPTIONS]

  Import data from compressed file into database

Options:
  --delete-first / --no-delete-first Should the entire table be deleted before import?
  --data-filename PATH Path to compressed data file. Default='../hg37variants1000g.vcf.gz'
  --batch-size INTEGER Number of rows to be committed into the database at the same time. Default=100000
  --row-limit INTEGER Total number of rows to be imported. Default=-1
  --help                          
```
This import happens at a rate of around 10k rows/s on my machine and takes 3 hours to complete fully.

## Genotype data
You can import the first million data points of both sample genotypes using the following:
```
wget https://gpgeno-reference-files.s3-eu-west-1.amazonaws.com/mixedgtvcfs/sample1/sample1.vcf.gz
wget https://gpgeno-reference-files.s3-eu-west-1.amazonaws.com/mixedgtvcfs/sample2/sample2.vcf.gz
flask import genotype --data-filename=../sample1.vcf.gz --user-id=1 --row-limit=1000000
flask import genotype --data-filename=../sample2.vcf.gz --user-id=2 --row-limit=1000000
```
This runs at a rate of 15k rows/s on my machine. As long as your computer can handle it you can run both commands in parallel. On my machine both still run at 12k rows/s.