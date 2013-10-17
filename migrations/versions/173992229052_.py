"""empty message

Revision ID: 173992229052
Revises: 582f981ffa5e
Create Date: 2013-10-16 14:59:51.712984

"""

# revision identifiers, used by Alembic.
revision = '173992229052'
down_revision = '582f981ffa5e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer


def upgrade():
    op.create_table('product',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('sku', sa.String(length=10), nullable=False),
                    sa.Column('name', sa.String(length=80), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name'))

    op.create_table('category',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=80), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name'))

    op.create_table('category_product',
                    sa.Column('category_id', sa.Integer(),
                              sa.ForeignKey('category.id')),
                    sa.Column('product_id', sa.Integer(),
                              sa.ForeignKey('product.id')))

    # Create ad-hoc tables to use for the insert statements
    product_table = table('product',
                          column('id', Integer),
                          column('sku', String),
                          column('name', String))

    category_table = table('category',
                           column('id', Integer),
                           column('name', String))

    category_product_table = table('category_product',
                                   column('category_id', Integer),
                                   column('product_id', Integer))

    op.bulk_insert(product_table, [
        {'id': 1, 'sku': '10150', 'name': 'pharMAX Nerve Pain Relief Cream'},
        {'id': 2, 'sku': '10250', 'name':
            'pharMAX Relief: Homeopathic Pain Cream'},
        {'id': 3, 'sku': '10311', 'name':
            '100% New Zealand Colostrum Capsules'},
        {'id': 4, 'sku': '10400', 'name':
            'Flora Source Multi Probiotic Capsules'},
        {'id': 5, 'sku': '10401', 'name':
            'Flora Source Multi Probiotic Powder'},
        {'id': 6, 'sku': '10402', 'name': 'Probiotic Supplements for Women'},
        {'id': 7, 'sku': '10404', 'name': 'Flora Sinus Seasonal Support'},
        {'id': 8, 'sku': '10450', 'name': 'FloraZyme Digestive Aid'},
        {'id': 9, 'sku': '10501', 'name': 'ArthroZyme Joint &amp; Muscle'},
        {'id': 10, 'sku': '10502', 'name': 'ZymaZorb Digestive Enzymes'},
        {'id': 11, 'sku': '10503', 'name':
            'ArthroZyme Plus Joint &amp; Muscle'},
        {'id': 12, 'sku': '10805', 'name':
            'Focus Force Memory &amp; Brain Supplements'},
        {'id': 13, 'sku': '11406', 'name': 'Sleep Wave Rest &amp; Relax'},
        {'id': 14, 'sku': '11411', 'name': 'FloraBright Oral Probiotics'},
        {'id': 15, 'sku': '11505', 'name':
            'D-Ribose Gold Muscle &amp; Energy Support'},
        {'id': 16, 'sku': '11506', 'name':
            'D-Ribose GoldM - Muscle &amp; Energy Support'},
        {'id': 17, 'sku': '11508', 'name': 'TruBone Complete - New!'},
        {'id': 18, 'sku': '11601', 'name': 'Memoril Memory &amp; Mood'},
        {'id': 19, 'sku': '11703', 'name': 'NH-D3 Cellular Health Support*'},
        {'id': 20, 'sku': '11706', 'name': 'Nutri-Daily Multivitamin for Men'},
        {'id': 21, 'sku': '11707', 'name':
            'Nutri-Daily Multivitamin for Women'},
        {'id': 22, 'sku': '11709', 'name': 'NH-D3 Spray - NEW!'},
        {'id': 23, 'sku': '11802', 'name': 'Advanced Cell Rescue'},
        {'id': 24, 'sku': '11805', 'name': 'Bi-Optium Eye Health'},
        {'id': 25, 'sku': '11902', 'name': 'BG-Cor Advanced Heart Health'},
        {'id': 26, 'sku': '11903', 'name':
            'Glucoprotect 6X Blood Sugar Control Supplements'},
        {'id': 27, 'sku': '11904', 'name': 'Advanced-Q CoQ10 with VESIsorb'}])

    op.bulk_insert(category_table, [
        {'id': 1, 'name': 'Digestive & Immune Health'},
        {'id': 8, 'name': 'Joint & Muscle Health'},
        {'id': 12, 'name': 'Heart Health'},
        {'id': 18, 'name': 'Aging Support'},
        {'id': 28, 'name': 'Vitamin & Supplement Sales'},
        {'id': 31, 'name': 'Healthy Lifestyle Savings'},
        {'id': 37, 'name': 'Health Info'},
        {'id': 52, 'name': 'Bestsellers 20% OFF'},
        {'id': 53, 'name': 'Bundles: Now Only $99 for 3'},
        {'id': 54, 'name': 'Probiotic Formulas'},
        {'id': 56, 'name': 'Enzymes'},
        {'id': 57, 'name': 'Natural Supplements'},
        {'id': 61, 'name': 'Invisible Group'},
        {'id': 62, 'name': 'Brain Health'},
        {'id': 66, 'name': 'BuyFloraSinus-LP'},
        {'id': 67, 'name': 'TryMemorilLP'},
        {'id': 97, 'name': 'TryFloraBright LP'},
        {'id': 105, 'name': 'FREE NHD3'},
        {'id': 117, 'name': 'TryFloraSinusLP'},
        {'id': 123, 'name': 'NutriDaily Hidden Bogo'},
        {'id': 129, 'name': 'Memoril 20'},
        {'id': 130, 'name': 'FloraSource 20'},
        {'id': 131, 'name': 'FloraSinus 20'},
        {'id': 132, 'name': 'ArthoZyme Plus 20'},
        {'id': 133, 'name': 'GlucoProtect6X 20'},
        {'id': 134, 'name': 'AdvancedQ 20'},
        {'id': 136, 'name': 'FSK-136-SAVE50'},
        {'id': 140, 'name': 'Men\'s Health'},
        {'id': 141, 'name': 'Women\'s Health'},
        {'id': 142, 'name': 'Memory Health'},
        {'id': 145, 'name': 'Remarket-10'},
        {'id': 146, 'name': 'Remarket-20'},
        {'id': 147, 'name': 'Free NHD3 Spray'},
        {'id': 148, 'name': 'AZRecapture136'},
        {'id': 149, 'name': 'Flora Source Multi-Probiotic Formulas'},
        {'id': 150, 'name': 'Supplements for Immune Health'},
        {'id': 154, 'name': '50% Detox & Physician\'s Comfort'},
        {'id': 156, 'name': 'AZPtrial'},
        {'id': 159, 'name': 'BG-Cor Save 30%'},
        {'id': 160, 'name': 'NutriDaily60'},
        {'id': 161, 'name': 'Limited Time Only - Specials'},
        {'id': 162, 'name': 'TruDigest-20'},
        {'id': 163, 'name': 'pharMax Nerve & Relief'}])

    op.bulk_insert(category_product_table, [
        {'category_id': 1, 'product_id': 2},
        {'category_id': 1, 'product_id': 3},
        {'category_id': 1, 'product_id': 4},
        {'category_id': 1, 'product_id': 5},
        {'category_id': 1, 'product_id': 6},
        {'category_id': 1, 'product_id': 7},
        {'category_id': 1, 'product_id': 163},
        {'category_id': 8, 'product_id': 9},
        {'category_id': 8, 'product_id': 10},
        {'category_id': 8, 'product_id': 11},
        {'category_id': 8, 'product_id': 78},
        {'category_id': 8, 'product_id': 119},
        {'category_id': 8, 'product_id': 143},
        {'category_id': 8, 'product_id': 144},
        {'category_id': 12, 'product_id': 13},
        {'category_id': 12, 'product_id': 14},
        {'category_id': 12, 'product_id': 15},
        {'category_id': 12, 'product_id': 16},
        {'category_id': 12, 'product_id': 17},
        {'category_id': 12, 'product_id': 64},
        {'category_id': 18, 'product_id': 19},
        {'category_id': 18, 'product_id': 20},
        {'category_id': 18, 'product_id': 21},
        {'category_id': 18, 'product_id': 22},
        {'category_id': 18, 'product_id': 23},
        {'category_id': 18, 'product_id': 24},
        {'category_id': 18, 'product_id': 25},
        {'category_id': 18, 'product_id': 26},
        {'category_id': 18, 'product_id': 27},
        {'category_id': 18, 'product_id': 63},
        {'category_id': 18, 'product_id': 65},
        {'category_id': 18, 'product_id': 81},
        {'category_id': 18, 'product_id': 92},
        {'category_id': 18, 'product_id': 118},
        {'category_id': 18, 'product_id': 139},
        {'category_id': 28, 'product_id': 29},
        {'category_id': 28, 'product_id': 32},
        {'category_id': 28, 'product_id': 33},
        {'category_id': 28, 'product_id': 34},
        {'category_id': 28, 'product_id': 35},
        {'category_id': 28, 'product_id': 36},
        {'category_id': 28, 'product_id': 109},
        {'category_id': 37, 'product_id': 38},
        {'category_id': 37, 'product_id': 39},
        {'category_id': 37, 'product_id': 40},
        {'category_id': 37, 'product_id': 41},
        {'category_id': 37, 'product_id': 42},
        {'category_id': 37, 'product_id': 43},
        {'category_id': 37, 'product_id': 48},
        {'category_id': 37, 'product_id': 50},
        {'category_id': 37, 'product_id': 51},
        {'category_id': 57, 'product_id': 46},
        {'category_id': 57, 'product_id': 55},
        {'category_id': 57, 'product_id': 58},
        {'category_id': 57, 'product_id': 59},
        {'category_id': 57, 'product_id': 60}])


def downgrade():
    op.drop_table('category_product')
    op.drop_table('product')
    op.drop_table('category')
