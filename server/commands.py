import gzip
from flask import Blueprint

from models import db, GeneLocation

genome_bp = Blueprint('genome', __name__)

def parse_line(line: str) -> list[GeneLocation]:
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

@genome_bp.cli.command('import_genome')
def import_genome():
    """ Import data from compressed file into database """
    with gzip.open('../hg37variants1000g.vcf.gz', 'rt') as gene_data:
        genes = []
        imported = set()
        for line in gene_data:
            if line.startswith('#'):
                continue
            for gene in parse_line(line):
                if gene.id in imported:
                    continue
                genes.append(gene)
                imported.add(gene.id)
            if len(genes) > 100000:
                print('Commiting a batch of rows.')
                db.session.add_all(genes)
                db.session.commit()
                genes = []
                print('\tDone.')
            if len(imported) > 1000000:
                break
                

