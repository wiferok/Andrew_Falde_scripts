import pandas as pd
import plotly
import os
import re
import easy_plotly
from plotly import graph_objs as go

input_path =os.path.join(os.path.dirname(os.path.realpath(__file__)), 'input_folder')
output_path =os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output_folder')
# Join absolute path to filename
files_list = [os.path.join(input_path, x) for x in os.listdir(input_path)]

#we have file
# def add

def add_year_columns(file_path):
    df = pd.read_csv(file_path, header = 0, delimiter='\t')
    df.name = os.path.basename(file_path)
    ###formating df, adding PNLS
    df['PnL%'] = df['Close'].pct_change()
    df['Total PnL%'] = df['PnL%'].cumsum()
    df['Date'] = pd.to_datetime(df['Date'])
    for row in df.iterrows():
        year = row[1].loc['Date'].year
        df.loc[row[0], str(year)] = row[1]['Total PnL%']

    return df
    ## creating year df

def create_compare_years_df(df):
    """
    function creates a df with yers columns comparing to the date of year
    :param df:
    :return:
    """
    for y in df.columns:
        if re.match(r'\d\d\d\d', y):
            year = y
            break
    else:
        raise IOError("No year columns with format('xxxx', x - numbers) in file %s "%df.name)
    year_df = df.loc[:,['Date',year]]
    for col_name in df.columns:
        if re.match(r'\d\d\d\d', col_name):
            year_df.loc[:,col_name] = df[col_name]
    year_df = year_df.resample(rule = '1D', on='Date').mean()
    year_df.loc[:, 'Date']=year_df.index.map(lambda x : x.dayofyear)
    year_df = year_df.groupby('Date').mean()
    year_df = year_df.interpolate(limit=5)
    return year_df

def make_builder(year_df):
    builder = easy_plotly.GraphBuilder()
    for col in year_df.columns:
        builder.add_trace(go.Scatter(x=year_df.index, y=year_df[col],
                                     name=col))
    return builder

def process_file(file_path):
    new_base_name = 'o_'+os.path.basename(file_path)
    out_path = os.path.join(output_path, new_base_name)
    df = add_year_columns(file_path)
    df.to_csv(out_path, index=False)
    year_df = create_compare_years_df(df)
    builder = make_builder(year_df)
    builder.plot(filename=out_path+'.html', auto_open=False, link_text='')


if __name__ == '__main__':
 for file_path in files_list:
     process_file(file_path)