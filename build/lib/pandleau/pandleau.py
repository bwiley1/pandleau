# -*- coding: utf-8 -*-
"""


@author: jamin, zhiruiwang
"""

from __future__ import print_function
import pandas
import numpy
from tableausdk import *
try:
	from tableausdk.Extract import *
	print("You are using the Tableau SDK, please save the output as .tde format")
except:
	pass
try:
	from tableausdk.HyperExtract import *
	print("You are using the Extract API 2.0, please save the output as .hyper format")
except:
	pass

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
            mapper = {'string':Type.UNICODE_STRING,
                      'bytes':Type.BOOLEAN,
                      'floating':Type.DOUBLE,
                      'integer':Type.INTEGER,
                      'mixed-integer':Type.DOUBLE, # integers with non-integers
                      'mixed-integer-float':Type.DOUBLE,# floats and integers
                      'decimal':Type.DOUBLE,
                      'complex':Type.UNICODE_STRING,# No complex set type
                      'categorical':Type.CHAR_STRING,
                      'boolean':Type.BOOLEAN,
                      'datetime64':Type.DATETIME,
                      'datetime': Type.DATETIME,
                      'date': Type.DATE,
                      'timedelta64':Type.DATETIME,
                      'timedelta':Type.DATETIME,
                      'time':Type.DATETIME,
                      'period':Type.DURATION,
                      'mixed':Type.UNICODE_STRING}
            try:
            	return mapper[pandas.api.types.infer_dtype(column.dropna())]
            except:
                raise Exception('Error: Unknown pandas to Tableau data type.')
    
    @classmethod 
    def __init__( self, dataframe ):
        if dataframe.__class__.__name__ != 'DataFrame':
            raise Exception('Error: object is not a pandas DataFrame.')
        
        self._dataframe = dataframe
        self._column_names = list(self._dataframe.columns)
        
        # Iniital column types
        self._column_static_type = self._dataframe.apply(lambda x: pandleau.data_static_type(x), axis = 0)


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
        
        # Delete Extract and debug log is already exist
        for file in [path, os.path.dirname(path) + '/debug.log',
        			'./DataExtract.log','./debug.log']:
        	if os.path.isfile(file):
        		os.remove(file)

        # Create Extract and Table
        ExtractAPI.initialize( )
        new_extract = Extract( path )
        table_def = TableDefinition()
        
        # Set columns in Tableau
        if add_index:
            table_def.addColumn( 'index', Type.INTEGER )
            
        for col_index, col_name in enumerate(self._dataframe):
            table_def.addColumn( col_name, self._column_static_type[col_index] )
        
        # Create table
        new_table = new_extract.addTable( "Extract", table_def )
        
        # Set Column values
        self.set_column_values( new_table, table_def, add_index )
        
        # Close extract
        new_extract.close()
        ExtractAPI.cleanup()
    
    
    def set_column_values( self, tableau_table, extract_table, add_index ):
        '''
        Translates pandas datatypes to tableau datatypes
        
        '''
        # Create new row
        new_row = Row( extract_table )
        
        for row_index in self._dataframe.itertuples():

            for col_index, col_entry in enumerate(row_index):
                if add_index:
                    if col_index == 0:
                        new_row.setInteger(col_index, int( col_entry+1 ) )
                if col_index != 0:
                    column_type = self._column_static_type[col_index-1]
#                    print(new_row, (col_index-2), col_entry, column_type)
                    pandleau.determine_entry_value(new_row, (col_index+add_index-1), col_entry, column_type)
                
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