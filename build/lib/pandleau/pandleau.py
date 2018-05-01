# -*- coding: utf-8 -*-
"""


@author: jamin
"""

import pandas
import numpy
from tableausdk import *
from tableausdk.HyperExtract import *


class pandleau( object ):
    '''
    Modification to the pandas DataFrame object
    
    '''
    
    @staticmethod
    def data_static_type(column):
            '''
            Translates pandas datatypes to static datatypes (for initial columns)
            @param column is dataframe column
            
            '''
            if pandas.api.types.infer_dtype(column) == 'string':
                return Type.UNICODE_STRING 
            elif pandas.api.types.infer_dtype(column) == 'unicode':
                return Type.UNICODE_STRING 
            elif pandas.api.types.infer_dtype(column) == 'bytes':
                return Type.BOOLEAN 
            elif pandas.api.types.infer_dtype(column) == 'floating':
                return Type.DOUBLE 
            elif pandas.api.types.infer_dtype(column) == 'integer':
                return Type.INTEGER 
            elif pandas.api.types.infer_dtype(column) == 'mixed-integer':
                # integers with non-integers
                return Type.DOUBLE 
            elif pandas.api.types.infer_dtype(column) == 'mixed-integer-float':
                # floats and integers
                return Type.DOUBLE 
            elif pandas.api.types.infer_dtype(column) == 'decimal':
                return Type.DOUBLE 
            elif pandas.api.types.infer_dtype(column) == 'complex':
                # No complex set type
                return Type.UNICODE_STRING  
            elif pandas.api.types.infer_dtype(column) == 'categorical':
                return Type.CHAR_STRING 
            elif pandas.api.types.infer_dtype(column) == 'boolean':
                return Type.BOOLEAN 
            elif pandas.api.types.infer_dtype(column) == 'datetime64':
                return Type.DATETIME 
            elif pandas.api.types.infer_dtype(column) == 'datetime':
                return Type.DATETIME 
            elif pandas.api.types.infer_dtype(column) == 'date':
                return Type.DATE 
            elif pandas.api.types.infer_dtype(column) == 'timedelta64':
                return Type.DATETIME 
            elif pandas.api.types.infer_dtype(column) == 'timedelta':
                return Type.DATETIME 
            elif pandas.api.types.infer_dtype(column) == 'time':
                return Type.DATETIME 
            elif pandas.api.types.infer_dtype(column) == 'period':
                return Type.DURATION 
            elif pandas.api.types.infer_dtype(column) == 'mixed': 
                return Type.UNICODE_STRING 
            else:
                raise Exception('Error: Unknown pandas to Tableau data type.')
    
    @classmethod 
    def __init__( self, dataframe ):
        if dataframe.__class__.__name__ != 'DataFrame':
            raise Exception('Error: object is not a pandas DataFrame.')
        
        self._dataframe = dataframe
        self._column_names = list(self._dataframe.columns)
        
        # Iniital column types
        self._column_static_type = self._dataframe.apply(lambda x: pandleau.data_static_type(x), axis = 0 )


    def set_spatial(self, column_index, indicator = True):
        '''
        Allows the user to define a spatial column
        @param column_name = index of spatial column,
                             either number or name
        @param indicator = change spatial characteristic  
        
        '''
        
        if indicator:
            if column_index.__class__.__name__ == 'int':
                self._column_static_type[column_index] = Type.SPATIAL
            elif column_index.__class__.__name__ == 'str':
                self._column_static_type[self._column_names.index(column_index)] = Type.SPATIAL
            else:
                raise Exception ('Error: could not find column in dataframe.')
        else:
            if column_index.__class__.__name__ == 'int':
                self._column_static_type[column_index] = pandleau.data_static_type(self._dataframe.iloc[:, column_index])
            elif column_index.__class__.__name__ == 'str':
                self._column_static_type[self._column_names.index(column_index)] = pandleau.data_static_type(self._dataframe.loc[:, column_index])
            else:
                raise Exception ('Error: could not find column in dataframe.')


    def to_tableau( self, path, add_index=False ):
        '''
        Converts a Pandas DataFrame to a Tableau .tde file
        @param path = path to write file
        @param tableName = name of the table in the extract
        
        '''
        
        # Create Extract and Table
        ExtractAPI.initialize( )
        new_extract = Extract( path )
        table_def = TableDefinition()
        
        # Set columns in Tableau
        if add_index:
            table_def.addColumn( 'index', Type.INTEGER )
            
        for col_index, col_name in enumerate(self._dataframe, 1):
            table_def.addColumn( col_name, self._column_static_type[col_index-1] )
        
        # Create table
        new_table = new_extract.addTable( "Extract", table_def )
        
        # Set Column values
        self.set_column_values( new_table, table_def, add_index )
        
        # Close extract
        new_extract.close()
    
    
    def set_column_values( self, tableau_table, extract_table, add_index ):
        '''
        Translates pandas datatypes to tableau datatypes
        
        '''
        # Create new row
        new_row = Row( extract_table )
        
        for row_index in self._dataframe.itertuples():

            for col_index, col_entry in enumerate(row_index, 1):
                if add_index:
                    if col_index == 1:
                        new_row.setInteger(col_index, int( row_index ) )
                if col_index != 1:
                    column_type = self._column_static_type[col_index-2]
#                    print(new_row, (col_index-2), col_entry, column_type)
                    pandleau.determine_entry_value(new_row, (col_index-2), col_entry, column_type)
                
            tableau_table.insert( new_row )
            
    
    @staticmethod
    def determine_entry_value(new_row, entry_index, entry, column_type):
        '''
        Determines the entry value
        @param new_row is the new row of the Tableau extract
        @param entry_index is the index of the entry
        @param entry is an entry of the dataframe
        @param column_type is the data type of the corresponding entry column
        
        '''
        
        try:
            if (pandas.isnull(entry)):
                new_row.setNull(entry_index)
            elif column_type == Type.SPATIAL:
                new_row.setSpatial(entry_index, 
                                  entry.encode('utf-8') )
            elif column_type == Type.UNICODE_STRING:
                new_row.setString(entry_index, 
                                  str(entry) )
            elif column_type == Type.BOOLEAN:
                new_row.setBoolean(entry_index, 
                                   entry)
            elif column_type == Type.DOUBLE:
                new_row.setDouble(entry_index, 
                                  entry)
            elif column_type == Type.INTEGER:
                new_row.setInteger(entry_index, 
                                   int( entry ) )
            elif column_type == Type.CHAR_STRING:
                new_row.setCharString(entry_index, 
                                      str( entry ) )
            elif column_type == Type.DATETIME:
                new_row.setDateTime(entry_index,
                                    entry.year,
                                    entry.month,
                                    entry.day,
                                    entry.hour,
                                    entry.minute,
                                    entry.second,
                                    entry.microsecond)
            elif column_type == Type.DATE:
                new_row.setDate(entry_index,
                                    entry.year,
                                    entry.month,
                                    entry.day)
            elif column_type == Type.DURATION:
                new_row.setDuration(entry_index,
                                    entry.day,
                                    entry.hour,
                                    entry.minute,
                                    entry.second,
                                    entry.microsecond)
            else:
                new_row.setNull(entry_index)
        except:
            new_row.setNull(entry_index)