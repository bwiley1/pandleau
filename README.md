# pandleau

A quick and easy way to convert a Pandas DataFrame to a Tableau extract.

## Getting Started

### Prerequites

You'll need to install tableauSDK directly from Tableau's site: https://onlinehelp.tableau.com/current/api/sdk/en-us/SDK/tableau_sdk_installing.htm. 

### Installing

Once installing tableauSDK is done, download this repository, navigate to your downloads file and run the following in cmd:  
```bash
python -m setup.py install
```

## Example

I grabbed the following Brazil flights data off of kaggle for this example: https://www.kaggle.com/microtang/exploring-brazil-flights-data/data.

```python
import pandas as pd
from pandleau import *

# Import the data
example_df = pd.read_csv(r'example/BrFlights2.csv', encoding = 'iso-8859-1')

# Format dates in pandas
example_df['Partida.Prevista'] = pd.to_datetime(example_df['Partida.Prevista'], format = '%Y-%m-%d')
example_df['Partida.Real'] = pd.to_datetime(example_df['Partida.Real'], format = '%Y-%m-%d')
example_df['Chegada.Prevista'] = pd.to_datetime(example_df['Chegada.Prevista'], format = '%Y-%m-%d')
example_df['Chegada.Real'] = pd.to_datetime(example_df['Chegada.Real'], format = '%Y-%m-%d')

# Set up a spatial column
example_df.loc[:, 'SpatialDest'] = example_df['LatDest'].apply( lambda x: "POINT (" + str( round(x, 6) ) ) + \
	example_df['LongDest'].apply( lambda x: " "+str( round(x, 6) ) + ")" )

# Change to pandleau object
df_tableau = pandleau(example_df)

# Define spatial column
df_tableau.set_spatial('SpatialDest')

# Write .tde Extract!
df_tableau.to_tableau('example.tde')

```

## Authors

* **Benjamin Wiley** - [jamin4lyfe](https://github.com/bwiley1)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
