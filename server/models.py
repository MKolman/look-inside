import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy()

class GeneLocation(db.Model):
    __tablename__ = 'gene_location'
    # RSID ex. rs568405545. Indexed on prefix for fast lookup.
    id = db.Column(db.String(100), primary_key=True, index=True)
    # Number of the chromosome for this genomic location
    chromosome = db.Column(db.SmallInteger)
    # Sequence number of this gene relative to its chromosome.
    # It's saved as a string to provide prefix index.
    position = db.Column(db.String(50))
    # Reference versiom of the genome at this location
    ref = db.Column(db.Text)
    # Alternative version of the genome at this location
    alt = db.Column(db.Text)
    # Format/Info ¯\_(ツ)_/¯
    format = db.Column(db.Text)

    # Combined index for chromosome and position.
    # This allows fast lookups for chromosome num + position prefix.
    __table_args__ = (
        db.Index('chrom_pos_idx', chromosome, position),
    )

class Genotype(db.Model):
    __tablename__ = 'genotype'
    # Unique primary key
    id = db.Column(db.Integer, primary_key=True)
    # Which user's data is this?
    user_id = db.Column(db.Integer)
    # Link to the key of the gene location.
    # Not a formal foreign key to save on time while importing.
    gene_location = db.Column(db.String(100))
    # Actual value of ref vs alt values
    value = db.Column(db.Text)

    # Combined index for user and gene_location.
    # This allows fast lookups for genotype of a single user.
    __table_args__ = (
        db.Index('user_gene_idx', user_id, gene_location),
    )



