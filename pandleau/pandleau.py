# -*- coding: utf-8 -*-
"""


@author: jamin, zhiruiwang, aawiegel
"""

from __future__ import print_function
import pandas
from tableausdk import *
from tqdm import tqdm

try:
    from tableausdk.Extract import *

    print("You are using the Tableau SDK, please save the output as .tde format")
except ModuleNotFoundError:
    pass

try:
    from tableausdk.HyperExtract import *

    print("You are using the Extract API 2.0, please save the output as .hyper format")
except ModuleNotFoundError:
    pass


class pandleau(object):
    """
    Modification to the pandas DataFrame object

    """
    mapper = {'string': Type.UNICODE_STRING,
              'bytes': Type.BOOLEAN,
              'floating': Type.DOUBLE,
              'integer': Type.INTEGER,
              'mixed-integer': Type.DOUBLE,  # integers with non-integers
              'mixed-integer-float': Type.DOUBLE,  # floats and integers
              'decimal': Type.DOUBLE,
              'complex': Type.UNICODE_STRING,  # No complex set type
              'categorical': Type.CHAR_STRING,
              'boolean': Type.BOOLEAN,
              'datetime64': Type.DATETIME,
              'datetime': Type.DATETIME,
              'date': Type.DATE,
              'timedelta64': Type.DATETIME,
              'timedelta': Type.DATETIME,
              'time': Type.DATETIME,
              'period': Type.DURATION,
              'mixed': Type.UNICODE_STRING}

    entry_writer = {Type.SPATIAL: lambda row, entry_index, entry: row.setSpatial(entry_index, entry.encode('utf-8')),
                    Type.UNICODE_STRING: lambda row, entry_index, entry: row.setString(entry_index, str(entry)),
                    Type.BOOLEAN: lambda row, entry_index, entry: row.setBoolean(entry_index, entry),
                    Type.DOUBLE: lambda row, entry_index, entry: row.setDouble(entry_index, entry),
                    Type.INTEGER: lambda row, entry_index, entry: row.setInteger(entry_index, int(entry)),
                    Type.CHAR_STRING: lambda row, entry_index, entry: row.setCharString(entry_index, str(entry)),
                    Type.DATETIME: lambda row, entry_index, entry: row.setDateTime(entry_index, entry.year,
                                                                                   entry.month, entry.day, entry.hour,
                                                                                   entry.minute, entry.second,
                                                                                   entry.microsecond),
                    Type.DATE: lambda row, entry_index, entry: row.setDate(entry_index, entry.year, entry.month,
                                                                           entry.day),
                    Type.DURATION: lambda row, entry_index, entry: row.setDuration(entry_index, entry.day, entry.hour,
                                                                                   entry.minute,
                                                                                   entry.second, entry.microsecond)}

    @staticmethod
    def data_static_type(column):
        """
            Translates pandas datatypes to static datatypes (for initial columns)
            @param column is dataframe column

            """

        try:
            # Use pandas api for inferring types for latest versions of pandas, lib method for earlier versions
            if pandas.__version__ >= '0.21.0':
                return pandleau.mapper[pandas.api.types.infer_dtype(column.dropna())]
            else:
                return pandleau.mapper[pandas.lib.infer_dtype(column.dropna())]
        except:
            raise Exception('Error: Unknown pandas to Tableau data type.')

    def __init__(self, dataframe):
        if dataframe.__class__.__name__ != 'DataFrame':
            raise Exception('Error: object is not a pandas DataFrame.')

        self._dataframe = dataframe
        self._column_names = list(self._dataframe.columns)

        # Initial column types
        self._column_static_type = self._dataframe.apply(lambda x: pandleau.data_static_type(x), axis=0)

    def set_spatial(self, column_index, indicator=True):
        """
        Allows the user to define a spatial column
        @param column_index = index of spatial column,
                             either number or name
        @param indicator = change spatial characteristic

        """

        if indicator:
            if column_index.__class__.__name__ == 'int':
                self._column_static_type[column_index] = Type.SPATIAL
            elif column_index.__class__.__name__ == 'str':
                self._column_static_type[self._column_names.index(column_index)] = Type.SPATIAL
            else:
                raise Exception('Error: could not find column in dataframe.')
        else:
            if column_index.__class__.__name__ == 'int':
                self._column_static_type[column_index] = pandleau.data_static_type(
                    self._dataframe.iloc[:, column_index])
            elif column_index.__class__.__name__ == 'str':
                self._column_static_type[self._column_names.index(column_index)] = pandleau.data_static_type(
                    self._dataframe.loc[:, column_index])
            else:
                raise Exception('Error: could not find column in dataframe.')

    def to_tableau(self, path, table_name='Extract', add_index=False):
        """
        Converts a Pandas DataFrame to a Tableau .tde file
        @param path = path to write file
        @param table_name = name of the table in the extract
        @param add_index = adds incrementing integer index before dataframe columns

        """

        # Delete debug log if already exists
        for file in [os.path.dirname(path) + '/debug.log',
                     './DataExtract.log', './debug.log']:
            if os.path.isfile(file):
                os.remove(file)

        # Create Extract and Table
        ExtractAPI.initialize()
        new_extract = Extract(path)

        if not new_extract.hasTable(table_name):
            print('Table \'{}\' does not exist in extract {}, creating.'.format(table_name, path))
            self.set_table_structure(new_extract, table_name, add_index)

        new_table = new_extract.openTable(table_name)
        table_def = new_table.getTableDefinition()

        # Set Column values
        self.set_column_values(new_table, table_def, add_index)

        # Close extract
        new_extract.close()
        ExtractAPI.cleanup()

    def set_table_structure(self, new_extract, table_name, add_index=False):
        """
        Checks if the provided table name exists in the extract, and if not, creates it.
        @param new_extract = extract that's been created
        @param table_name = name of the table in the extract
        @param add_index = adds incrementing integer index before dataframe columns
        """

        table_def = TableDefinition()
        # Set columns in Tableau
        if add_index:
            index_col = 'index'
            suffix = 1
            while index_col in self._dataframe.columns:
                index_col = '%s_%s' % (index_col, suffix)
                suffix += 1
            table_def.addColumn(index_col, Type.INTEGER)
        for col_index, col_name in enumerate(self._dataframe):
            table_def.addColumn(col_name, self._column_static_type[col_index])
        # Create table
        new_extract.addTable(table_name, table_def)

    def set_column_values(self, tableau_table, extract_table, add_index):
        """
        Translates pandas datatypes to tableau datatypes

        """
        # Create new row
        new_row = Row(extract_table)
        cols_range = range(len(self._dataframe.columns))
        column_set_functions = [
            pandleau.entry_writer.get(col_type, lambda row, entry_index, _: row.setNull(entry_index))
            for col_type in
            self._column_static_type]
        i = 0

        for row_index in tqdm(self._dataframe.itertuples(index=False), desc='processing table'):

            if add_index:
                new_row.setInteger(0, i)
                i += 1

            for col_index in cols_range:
                col_index_corrected = col_index+add_index
                col_entry = row_index[col_index]
                column_set_function = column_set_functions[col_index]

                try:
                    if pandas.isnull(col_entry):
                        new_row.setNull(col_index_corrected)
                    else:
                        column_set_function(new_row, col_index_corrected, col_entry)
                except:
                    new_row.setNull(col_index_corrected)

            tableau_table.insert(new_row)

    @staticmethod
    def determine_entry_value(new_row, entry_index, entry, column_type):
        """
        Determines the entry value
        @param new_row is the new row of the Tableau extract
        @param entry_index is the index of the entry
        @param entry is an entry of the dataframe
        @param column_type is the data type of the corresponding entry column

        """

        try:
            if pandas.isnull(entry):
                new_row.setNull(entry_index)
            else:
                (pandleau.entry_writer
                 .get(column_type, lambda row, index, _: row.setNull(index))(new_row, entry_index, entry))

        except:
            new_row.setNull(entry_index)
