import pandas
import numpy
from tableausdk import *
from tableausdk.Extract import *


class pandleau( object ):
    '''
    Modification to the pandas DataFrame object
    
    '''
    
    def __init__( self, dataframe ):
        if dataframe.__class__.__name__ != 'DataFrame':
            print('Error: object is not a pandas DataFrame.')
            return
        
        self._dataframe = dataframe
        self._column_names = list(self._dataframe.columns)
        self._spatial = numpy.zeros(len(self._column_names))
        self.data_panda_type(self._dataframe)
        self.data_static_type()


    def set_spatial(self, column_index, indicator = True):
        '''
        Allows the user to define a spatial column
        @param column_name = index of spatial column,
                             either number or name
        @param indicator = change spatial characteristic  
        
        '''
        
        if column_index.__class__.__name__ == 'int':
            self._spatial[column_index] = indicator
            self.data_static_type()
        elif column_index.__class__.__name__ == 'str':
            self._spatial[self._column_names.index(column_index)] = indicator
            self.data_static_type()
        else:
            print('Error: could not find column in dataframe.')


    def to_tableau( self, path ):
        '''
        Converts a Pandas DataFrame to a Tableau .tde file
        @param path = path to write file
        @param tableName = name of the table in the extract
        
        '''
        
        # Create Extract and Table
        new_extract = Extract( path )
        table_def = TableDefinition()
        
        # Set columns in Tableau
        for i in range(len(self._column_names)):
            table_def.addColumn(self._column_names[i], self._column_static_types[i])
        
        # Create table
        new_table = new_extract.addTable( "Extract", table_def )
        
        # Set Column values
        self.set_column_values( new_table, table_def )
        
        # Close extract
        new_extract.close()
        
    
    @classmethod
    def data_panda_type(self, dataframe):
        '''
        Infer column data type
        
        '''
        
        data_type = []
        for i in range(len(dataframe.columns)):
            data_type.append(pandas.api.types.infer_dtype(dataframe.iloc[:, i]))
            
        self._column_panda_types = data_type
    
    
    def data_static_type(self):
        '''
        Translates pandas datatypes to static datatypes (for initial columns)
        
        '''
        
        data_static_types = []
        for i in range(len(self._column_panda_types)):
            if self._spatial[i]:
                data_static_types.append( Type.SPATIAL )
            elif self._column_panda_types[i] == 'string':
                data_static_types.append( Type.UNICODE_STRING )
            elif self._column_panda_types[i] == 'unicode':
                data_static_types.append( Type.UNICODE_STRING )
            elif self._column_panda_types[i] == 'bytes':
                data_static_types.append( Type.BOOLEAN )
            elif self._column_panda_types[i] == 'floating':
                data_static_types.append( Type.DOUBLE )
            elif self._column_panda_types[i] == 'integer':
                data_static_types.append( Type.INTEGER )
            elif self._column_panda_types[i] == 'mixed-integer':
                # integers with non-integers
                data_static_types.append( Type.DOUBLE )
            elif self._column_panda_types[i] == 'mixed-integer-float':
                # floats and integers
                data_static_types.append( Type.DOUBLE )
            elif self._column_panda_types[i] == 'decimal':
                data_static_types.append( Type.DOUBLE )
            elif self._column_panda_types[i] == 'complex':
                # No complex set type
                data_static_types.append( Type.UNICODE_STRING  )
            elif self._column_panda_types[i] == 'categorical':
                data_static_types.append( Type.CHAR_STRING )
            elif self._column_panda_types[i] == 'boolean':
                data_static_types.append( Type.BOOLEAN )
            elif self._column_panda_types[i] == 'datetime64':
                data_static_types.append( Type.DATETIME )
            elif self._column_panda_types[i] == 'datetime':
                data_static_types.append( Type.DATETIME )
            elif self._column_panda_types[i] == 'date':
                data_static_types.append( Type.DATE )
            elif self._column_panda_types[i] == 'timedelta64':
                data_static_types.append( Type.DATETIME )
            elif self._column_panda_types[i] == 'timedelta':
                data_static_types.append( Type.DATETIME )
            elif self._column_panda_types[i] == 'time':
                data_static_types.append( Type.DATETIME )
            elif self._column_panda_types[i] == 'period':
                data_static_types.append( Type.DURATION )
            elif self._column_panda_types[i] == 'mixed': 
                data_static_types.append( Type.UNICODE_STRING )
            else:
                raise  ### TODO: raise error here
                
        self._column_static_types = data_static_types
        
    
    def set_column_values( self, tableau_table, extract_table ):
        '''
        Translates pandas datatypes to tableau datatypes
        
        '''
        # Create new row
        new_row = Row( extract_table )
        
        for j in range(len(self._dataframe)):
            
            for i in range(len(self._column_panda_types)):
                
                if not (pandas.isnull(self._dataframe.iloc[j, i])):
                    
                    if self._spatial[i]:
                        new_row.setSpatial(i, 
                                          (self._dataframe.iloc[j, i]).encode('utf-8') )
                    elif self._column_panda_types[i] == 'string':
                        new_row.setString(i, 
                                          str(self._dataframe.iloc[j, i]) )
                    elif self._column_panda_types[i] == 'unicode':
                        new_row.setString(i, 
                                          str(self._dataframe.iloc[j, i]) )
                    elif self._column_panda_types[i] == 'bytes':
                        new_row.setBoolean(i, 
                                           self._dataframe.iloc[j, i])
                    elif self._column_panda_types[i] == 'floating':
                        new_row.setDouble(i, 
                                          self._dataframe.iloc[j, i])
                    elif self._column_panda_types[i] == 'integer':
                        new_row.setInteger(i, 
                                           int(self._dataframe.iloc[j, i]) )
                    elif self._column_panda_types[i] == 'mixed-integer':
                        # integers with non-integers
                        new_row.setDouble(i, 
                                          self._dataframe.iloc[j, i])
                    elif self._column_panda_types[i] == 'mixed-integer-float':
                        # floats and integers
                        new_row.setDouble(i, 
                                          self._dataframe.iloc[j, i])
                    elif self._column_panda_types[i] == 'decimal':
                        new_row.setDouble(i, 
                                          self._dataframe.iloc[j, i])
                    elif self._column_panda_types[i] == 'complex':
                        # No complex set type
                        new_row.setString(i, 
                                          str(self._dataframe.iloc[j, i]) )
                    elif self._column_panda_types[i] == 'categorical':
                        new_row.setCharString(i, 
                                              str(self._dataframe.iloc[j, i]) )
                    elif self._column_panda_types[i] == 'boolean':
                        new_row.setBoolean(i, 
                                           self._dataframe.iloc[j, i])
                    elif self._column_panda_types[i] == 'datetime64':
#                        print(str(i) + ' ' + str(j))
                        new_row.setDateTime(i,
                                            self._dataframe.iloc[j, i].year,
                                            self._dataframe.iloc[j, i].month,
                                            self._dataframe.iloc[j, i].day,
                                            self._dataframe.iloc[j, i].hour,
                                            self._dataframe.iloc[j, i].minute,
                                            self._dataframe.iloc[j, i].second,
                                            self._dataframe.iloc[j, i].microsecond)
                    elif self._column_panda_types[i] == 'datetime':
                        new_row.setDateTime(i,
                                            self._dataframe.iloc[j, i].year,
                                            self._dataframe.iloc[j, i].month,
                                            self._dataframe.iloc[j, i].day,
                                            self._dataframe.iloc[j, i].hour,
                                            self._dataframe.iloc[j, i].minute,
                                            self._dataframe.iloc[j, i].second,
                                            self._dataframe.iloc[j, i].microsecond)
                    elif self._column_panda_types[i] == 'date':
                        new_row.setDate(i,
                                            self._dataframe.iloc[j, i].year,
                                            self._dataframe.iloc[j, i].month,
                                            self._dataframe.iloc[j, i].day)
                    elif self._column_panda_types[i] == 'timedelta64':
                        new_row.setDuration(i,
                                            self._dataframe.iloc[j, i].day,
                                            self._dataframe.iloc[j, i].hour,
                                            self._dataframe.iloc[j, i].minute,
                                            self._dataframe.iloc[j, i].second,
                                            self._dataframe.iloc[j, i].microsecond)
                    elif self._column_panda_types[i] == 'timedelta':
                        new_row.setDuration(i,
                                            self._dataframe.iloc[j, i].day,
                                            self._dataframe.iloc[j, i].hour,
                                            self._dataframe.iloc[j, i].minute,
                                            self._dataframe.iloc[j, i].second,
                                            self._dataframe.iloc[j, i].microsecond)
                    elif self._column_panda_types[i] == 'time':
                        new_row.setDuration(i,
                                            self._dataframe.iloc[j, i].day,
                                            self._dataframe.iloc[j, i].hour,
                                            self._dataframe.iloc[j, i].minute,
                                            self._dataframe.iloc[j, i].second,
                                            self._dataframe.iloc[j, i].microsecond)
                    elif self._column_panda_types[i] == 'period':
                        new_row.setDuration(i,
                                            self._dataframe.iloc[j, i].day,
                                            self._dataframe.iloc[j, i].hour,
                                            self._dataframe.iloc[j, i].minute,
                                            self._dataframe.iloc[j, i].second,
                                            self._dataframe.iloc[j, i].microsecond)
                    elif self._column_panda_types[i] == 'mixed': 
                        new_row.setString(i, 
                                          str(self._dataframe.iloc[j, i]) )
                    else:
                        new_row.setNull(i)
                else:
                    new_row.setNull(i)
                
                tableau_table.insert( new_row )