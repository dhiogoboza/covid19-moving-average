import argparse
import pandas
import matplotlib.pyplot as plt
import seaborn as sns

NOTIFICATION_DATE_COLUMN = 'Data da Notificação'
TEST_RESULT_COLUMN = 'Resultado do Teste'
POSITIVE_VALUE = 'Positivo'

NOTIFICATION_DATE_COLUMN_ONLINE = 'datas'
POSITIVE_CASES_ONLINE = 'casos_positivos'

COLORS = ['red', 'blue', 'purple', 'orange', 'yellow', 'cyan']
X_MAX_LOC = 8

CHART_TITLE = 'Casos confirmados de covid-19 RN - Brasil'
Y_AXIS_LABEL = 'Casos diários'
X_AXIS_LABEL = ''
MOVING_AVERAGE_LABEL = 'Média Móvel - {} dias'

class MovingAverageData:
  def __init__(self, size):
    self.size = size
    self.data = pandas.Series(dtype='float64')
    self.values = []

  def __current_mean(self):
    return float(sum(self.values)) / max(len(self.values), 1)

  def add(self, index, value):
    self.values.append(value)
    if len(self.values) > self.size:
      self.values.pop(0)

    self.data[index] = int(self.__current_mean())

  def get_data(self):
    return self.data

  def get_label(self):
    return MOVING_AVERAGE_LABEL.format(self.size)

def calc_moving_average(local_data, ma_data):
  if local_data:
    # read csv file
    df = pandas.read_csv('data/covid_dataset.csv')

    # filter only positive values
    df = df[df[TEST_RESULT_COLUMN].eq(POSITIVE_VALUE)]

    # transform date columns in pandas datetime
    df[NOTIFICATION_DATE_COLUMN] = pandas.to_datetime(df[NOTIFICATION_DATE_COLUMN], format='%d/%m/%Y')

    # group notifications by date and sort
    notifications = df[NOTIFICATION_DATE_COLUMN].value_counts().sort_index(0)
  else:
    # read csv online data
    df = pandas.read_csv('https://covid.lais.ufrn.br/dados_abertos/evolucao_casos.csv', sep=';')

    # transform date columns in pandas datetime
    df[NOTIFICATION_DATE_COLUMN_ONLINE] = pandas.to_datetime(df[NOTIFICATION_DATE_COLUMN_ONLINE], format='%Y-%m-%d')

    # create notifications serie
    notifications = pandas.Series(df[POSITIVE_CASES_ONLINE].values, index =(df[NOTIFICATION_DATE_COLUMN_ONLINE].values))

  # max notifications to setup graphs max value
  max_not = 0

  # iterate over all notifications and calc moving average
  for index, value in notifications.items():
    for data in ma_data:
      data.add(index, value)
    if value > max_not:
      max_not = value

  # add a 10% padding   
  max_not *= 1.1

  # return date column to string
  dates = ['{}/{}/{}'.format(x.day, x.month, x.year) for x in notifications.keys()] 

  # data to create a new pandas dataframe
  df_data = {'dates': dates, 'notifications': notifications.values}

  # add moving averages data in dataframe
  for i, data in enumerate(ma_data):
    df_data['movingavg' + str(i)] = data.get_data().values

  # create pandas dataframe
  df = pandas.DataFrame(df_data)

  # create chart
  fig, ax1 = plt.subplots(figsize=(15,10))
  ax1.set_title(CHART_TITLE, fontsize=16)
  color = 'tab:green'

  # daily notifications in bar plot  
  ax1 = sns.barplot(x='dates', y='notifications', data=df, color=color)
  ax1.set_xlabel(X_AXIS_LABEL)
  ax1.xaxis.set_major_locator(plt.MaxNLocator(X_MAX_LOC))
  ax1.set_ylabel(Y_AXIS_LABEL, fontsize=12)
  ax1.tick_params(axis='y')
  ax1.set(ylim=(0, max_not))
  ax1.twinx()

  for i, data in enumerate(ma_data):
    color = 'tab:' + COLORS[i % len(COLORS)]

    # moving average line plot
    ax2 = sns.lineplot(x='dates', y='movingavg' + str(i), data = df, sort=False, color=color, label=data.get_label())
    ax2.xaxis.set_major_locator(plt.MaxNLocator(X_MAX_LOC))
    ax2.set(ylim=(0, max_not))
    ax2.yaxis.set_visible(False)

  # show plot
  plt.legend(loc=len(ma_data))
  plt.show()

def str2bool(v):
  if isinstance(v, bool): return v
  return v.lower() in ('yes', 'true', 't', 'y', '1')

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--moving_average', '-ma', nargs='+', help='Moving averages in days')
  parser.add_argument('--local_data', '-l', type=str2bool, default=False, help='Use local data instead of fetch data online')
  parser.add_argument('-f', help='Unused') # workaround to run this code in codelab
  args = vars(parser.parse_args())

  if args['moving_average'] is None:
    args['moving_average'] = ['7', '14']

  moving_avgs = [MovingAverageData(int(x)) for x in args['moving_average']]
  calc_moving_average(args['local_data'], moving_avgs)

if __name__ == '__main__':
  main()

