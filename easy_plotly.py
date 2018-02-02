import plotly.offline as py
import plotly.graph_objs as go
from plotly import tools


class GraphBuilder(object):

    """
    class that contains all functions to build plots evolves as needed
    """

    def __init__(self):

        self.traces = []
        self.layout = go.Layout()


    def add_trace(self, trace):
        """
        method to add trace to the plot
        :param trace: plotly.go object
        :return:
        """
        self.traces.append(trace)


    def layout_add(self, *args, **kwargs):
        """
        adds layout options, see go.Layout
        :param kwargs:
        :return:
        """
        self.layout.update(*args,**kwargs)

    def annot_var_add(self, dictionary):
        """

        :param dictionary: 'text displayed':'variable'
        :return:
        """
        annots = go.Annotations()
        text = ''
        for key in dictionary:
            text += '<br>%s = %.3f<br>' % (key, dictionary[key])

        annots.append(go.Annotation(
                          showarrow = False,
                          text = text,
                          xref = 'paper',
                          yref = 'paper',
                          x = 1,
                          y = 0.1,

                          ))
        self.layout_add(annotations=annots)

    def add_table_df(self, df):
        #function to add Table to the graph
        pass





    def plot(self, **kwargs):
        figure = go.Figure(data = self.traces, layout = self.layout)
        return py.plot(figure, **kwargs)

class GraphPandasTable(go.Table):
    """
    class that defines plotly graph go.Table
    """
    def __init__(self, data_frame):
        options_dict = dict(
            type='table',
            columnwidth=10,
            domain = dict(x=[0.038,0.45], y=[0,0.95]),
            header=dict(
                # we could automatically determine the values/column headers from the initial loop
                values=[' '] +['<b>%s</b>'%x for x in list(data_frame.columns)],
                line=dict(color='#506784', width =2),
                fill=dict(color='#C2D4FF'),
                align=['left', 'center'],
                font=dict(color='white', size=12)),
            cells=dict(
                # We use our values list here, to fill the cells in the table
                line = dict(width =2),
                values=[data_frame.index] + [data_frame[col] for col in data_frame.columns],
                align=['left', 'center'],
                font=dict(color='#506784', size=11))
        )
        super(GraphPandasTable, self).__init__(**options_dict)




class BuilderFromHolder(GraphBuilder):
    """
    class to integrate GraphBuilder with DataFramesHolder class
    """
    def __init__(self, holder, default = True):
        """

        :param holder: DataFramesHolder object
        """
        super(BuilderFromHolder, self).__init__()
        self.holder = holder
        self.layout={}
        if default:
            self.trace_columns()
            self.trace_average()
            self.holder.add_aret_mdd_stats_df()
            self.add_stats_table()

    def trace_columns(self, column_name = 'Total PnL%'):
        """ method adds lines on the graph from each table"""
        for df_name in self.holder.dataframes.iterkeys():
            df = self.holder.dataframes[df_name]['default']
            self.add_trace(go.Scatter(x=df.index, y=df[column_name],
                                      name = df_name))

    def trace_average(self, column_name = 'Total PnL%', **kwargs):
        """method adds average line on the graph from the column
        :param column_name: name of the column to add average
        :param kwargs: keyword arguments go.Scatter can accept
        """
        if not column_name in self.holder.averages_dict:
            self.holder.add_average_column(column=column_name)
        df = self.holder.averages_dict[column_name]
        self.add_trace(go.Scatter(x=df.index,
                                  y=df,
                                  name='%s Average'%column_name,
                                  line=dict(
                                      color='red',
                                      width=3),
                                  **kwargs
                                  ))
    def add_stats_table(self):
        """
        method adds Table with the stats(ARET MDD ARET/MDD + averages) for each file to the  plot"""
        table_trace = GraphPandasTable(data_frame=self.holder.stats_table)
        self.add_trace(table_trace)











if __name__ == '__main__':
    import pandas as pd
    from modules.main_processing import *
    from modules.parsers import *
    DataFramesHolder()

    parser = ParserCsv(files_paths=['/home/wiff/programming/tests/csv_folder/2.csv',
                                    '/home/wiff/programming/tests/csv_folder/8.csv'])
    parser.first_level_parsing()
    parser.holder.add_aret_mdd_stats_df()
    builder = BuilderFromHolder(holder=parser.holder, default=True)
    builder.plot()