from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker

#for test only
from table_classes import Download

class TableFactory(object):
  
  engine    = create_engine('sqlite:///pullite.db', echo=False)
  meta_data = MetaData()
  Session = sessionmaker(bind=engine)
  session = Session()
  
  @staticmethod
  def createTables(tables=[]):
    if len(tables) > 0:
      for table in tables:
        tmp_table = Table(table['name'], TableFactory.meta_data)
        for column in table['columns']:
          tmp_table.append_column(column)
        TableFactory.meta_data.create_all(TableFactory.engine)
        mapper(table['table_class'], tmp_table)

#start table creation
tables = [
  {'name': 'downloads',
   'columns': [Column('did', Integer, primary_key=True),
               Column('name', String(255)),
               Column('url', String(255)),
               Column('progress', Integer),
               Column('size', String(20)),
               Column('completed', String(20)),
               Column('created', String(30))],
  'table_class': Download}
]

TableFactory.createTables(tables)