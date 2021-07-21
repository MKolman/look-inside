from models import db, GeneLocation, Genotype

def genes_by_rsid_prefix(rsid: str):
    # TODO(maks): escape rsid
    return GeneLocation.query.filter(GeneLocation.id.like(f' {rsid}%'))

def genes_by_chrom_pos(chromosome: int, position: str):
    # TODO(maks): escape position
    return GeneLocation.query.filter(
        GeneLocation.chromosome == chromosome,
        GeneLocation.position.like(f' {position}%'))

def delete_all_genes():
    GeneLocation.query.delete()
    db.session.commit()

def count_all_genes():
    return GeneLocation.query.count()

def delete_all_genotype(user_id: int):
    Genotype.query.filter(Genotype.user_id==user_id).delete()
    db.session.commit()

def count_all_genotype(user_id: int):
    return Genotype.query.filter(Genotype.user_id==user_id).count()
    
def get_genotype(user_id: int, rsids: list[str]):
    return Genotype.query.filter(
        Genotype.user_id==user_id,
        Genotype.gene_location.in_(rsids))