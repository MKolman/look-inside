from models import GeneLocation

def genes_by_rsid_prefix(rsid: str):
    # TODO(maks): escape rsid
    return GeneLocation.query.filter(GeneLocation.id.like(f' {rsid}%'))

def genes_by_chrom_pos(chromosome: int, position: str):
    # TODO(maks): escape position
    return GeneLocation.query.filter(
        GeneLocation.chromosome == chromosome,
        GeneLocation.position.like(f' {position}%'))