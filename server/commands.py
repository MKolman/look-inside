import gzip
import sys
import typing
import time

import click
import psycopg2
from flask import Blueprint

import queries
import config
from models import db, GeneLocation, Genotype

genome_bp = Blueprint('import', __name__)

def delete_gene_locations():
    """ Delete all rows from gene_location table """
    print(f'You are about to delete {queries.count_all_genes()} rows of gene data.')
    if not input('Are you sure? (y/N): ').lower().startswith('y'):
        print('Stopping program.')
        sys.exit(0)
    print('Deleting...')
    queries.delete_all_genes()
    print('\tDone.')

def parse_gene_location_line(line: str) -> list[GeneLocation]:
    chrom, pos, rsids, ref, alt, info = line.split('\t')
    for rsid in rsids.split(';'):
        yield GeneLocation(
            id=rsid,
            chromosome=int(chrom),
            position=pos,
            ref=ref,
            alt=alt,
            format=info,
        )

def import_gene_location_data(
        gene_data: typing.TextIO,
        batch_size: int,
        row_limit: int,
    ):
    """ Import gene location data from an open file gene_data in batches of at
    least `batch_size` and import at least `row_limit` rows in total. """
    genes = []
    imported = set()
    start_time = time.time()
    for line in gene_data:
        if line.startswith('#'):
            continue
        
        for gene in parse_gene_location_line(line):
            if gene.id in imported:
                continue
            genes.append(gene)
            imported.add(gene.id)
        
        if len(genes) >= batch_size:
            print(f'Commiting a batch of {len(genes)} rows.')
            db.session.add_all(genes)
            db.session.commit()
            genes = []
            new_time = time.time()
            print(f'\tDone. Committed {len(imported)} rows in total. That\'s {len(imported)/(new_time-start_time)}/s.')
        
        if row_limit >= 0 and len(imported) >= row_limit:
            break

def copy_gene_location_data(gene_data: typing.TextIO):
    """ Alternative (faster?) way to import data into postgres is
    to use its COPY command. """
    while next(gene_data).startswith('#'):
        # Manually remove comments from file
        pass
    connection = psycopg2.connect(
        database=config.database,
        user=config.user,
        password=config.password,
        host=config.host,
        port=config.port,
    )
    cursor = connection.cursor()
    cursor.copy_from(gene_data, 'gene_location', sep='\t', columns=('chromosome', 'position', 'rsid', 'ref', 'alt', 'format'))

@genome_bp.cli.command('genome')
@click.option('--delete-first/--no-delete-first', default=True)
@click.option('--data-filename', default='../hg37variants1000g.vcf.gz', type=click.Path(exists=True))
@click.option('--batch-size', default=100000)
@click.option('--row-limit', default=-1)
def import_genome(delete_first, data_filename, batch_size, row_limit):
    """ Import data from compressed file into database """
    if delete_first:
        delete_gene_locations()
    with gzip.open(data_filename, 'rt') as gene_data:
        import_gene_location_data(gene_data, batch_size, row_limit)


def delete_genotype(user_id):
    print(f'You are about to delete {queries.count_all_genotype(user_id)} rows of genotype data for user {user_id}.')
    if not input('Are you sure? (y/N): ').lower().startswith('y'):
        print('Stopping program.')
        sys.exit(0)
    print('Deleting...')
    queries.delete_all_genotype(user_id)
    print('\tDone.')

def parse_genotype_line(user_id: int, line: str) -> Genotype:
    _, _, rsid, *_, value = line.split('\t')
    return Genotype(user_id=user_id, gene_location=rsid, value=value)

def import_genotype_location_data(
        user_id: int,
        gene_data: typing.TextIO,
        batch_size: int,
        row_limit: int,
    ):
    """ Import genotype data from an open file gene_data in batches of at
    least `batch_size` and import at least `row_limit` rows in total. """
    genotypes = []
    imported = set()
    start_time = time.time()
    for line in gene_data:
        if line.startswith('#'):
            continue
        
        row = parse_genotype_line(user_id, line)
        if row.gene_location in imported:
            continue
        genotypes.append(row)
        imported.add(row.gene_location)
        
        if len(genotypes) >= batch_size:
            print(f'Commiting a batch of {len(genotypes)} rows.')
            db.session.add_all(genotypes)
            db.session.commit()
            genotypes = []
            new_time = time.time()
            print(f'\tDone. Committed {len(imported)} rows in total. That\'s {len(imported)/(new_time-start_time)}/s.')
        
        if row_limit >= 0 and len(imported) >= row_limit:
            break


@genome_bp.cli.command('genotype')
@click.option('--user-id', default=1)
@click.option('--delete-first/--no-delete-first', default=True)
@click.option('--data-filename', default='../sample1.vcf.gz', type=click.Path(exists=True))
@click.option('--batch-size', default=100000)
@click.option('--row-limit', default=-1)
def import_genotype(user_id, delete_first, data_filename, batch_size, row_limit):
    """ Import data from compressed file into database """
    if delete_first:
        delete_genotype(user_id)
    with gzip.open(data_filename, 'rt') as gene_data:
        import_genotype_location_data(user_id, gene_data, batch_size, row_limit)

