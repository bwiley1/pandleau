# pandleau

A quick and easy way to convert a Pandas DataFrame to a Tableau .tde or .hyper extract.

## Getting Started

### Prerequisites

 - If you want to output as a .tde format, you'll need to install TableauSDK directly from Tableau's site [here]( https://onlinehelp.tableau.com/current/api/sdk/en-us/help.htm#SDK/tableau_sdk_installing.htm%3FTocPath%3D_____3).
  - If you want to output as a .hyper format, you'll need to install Extract API 2.0 directly from Tableau's site [here](https://onlinehelp.tableau.com/current/api/extract_api/en-us/help.htm#Extract/extract_api_installing.htm%3FTocPath%3D_____3).
  - Although Tableau's site claims Python 3 is not supported, this module has been tested to work fully functionally on Python 3.6.

### Installing

Once installing TableauSDK is done, download this repository, navigate to your downloads file and run the following in cmd or terminal:  
```bash
python -m setup.py install
```

You can also install pandleau using pip:
```bash
pip install pandleau
```
But note that this will throw a warning to install tableausdk using the above link in Prerequisites.

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
example_df.loc[:, 'SpatialDest'] = example_df['LongDest'].apply( lambda x: "POINT (" + str( round(x, 6) ) ) + \
	example_df['LatDest'].apply( lambda x: " "+str( round(x, 6) ) + ")" )

# Change to pandleau object
df_tableau = pandleau(example_df)

# Define spatial column
df_tableau.set_spatial('SpatialDest', indicator=True)

# Write .tde or .hyper Extract!
df_tableau.to_tableau('test.hyper', add_index=False)

```

## Tableau Server/Online Automation

Eric Chan ([erickhchan](https://github.com/erickhchan)) wrote a really cool blog post on using Python to blend and clean data before pushing it to Tableau Online (which is a SaaS version of Tableau Server). This is a great way to learn how to automate the data refresh process with Tableau Server Client and Pandleau. Check out his blog post here: https://www.erickhchan.com/data/2019/03/18/python-tableau-server.html

## Authors

* **Benjamin Wiley** - [jamin4lyfe](https://github.com/bwiley1)
* **Zhirui(Jerry) Wang**  - [zhiruiwang](https://github.com/zhiruiwang)
* **Aaron Wiegel** - [aawiegel](https://github.com/aawiegel)
* **Pointy Shiny Burning** - [PointyShinyBurning](https://github.com/pointyshinyburning)
* **Harrison** - [harrison-h](https://github.com/harrison-h)

## Related Project

[RTableau](https://github.com/zhiruiwang/RTableau) Convert R data.frame to Tableau Extract using pandleau

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
