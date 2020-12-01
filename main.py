import argparse
import pandas
import matplotlib.pyplot as plt

NOTIFICATION_DATE_COLUMN = 'Data da Notificação'
TEST_RESULT_COLUMN = 'Resultado do Teste'

class MovingAverageData:
  def __init__(self, size):
    self.size = size
    self.data = pandas.Series()
    self.values = []

  def __current_mean(self):
    return float(sum(self.values)) / max(len(self.values), 1)

  def add(self, index, value):
    self.values.append(value)
    if len(self.values) > self.size:
      self.values.pop(0)
      
    self.data[index] = self.__current_mean()

  def get_data(self):
    return self.data

  def get_label(self):
    return "Média Móvel - {} dias".format(self.size)

def calc_moving_average(mr_data):
  # read csv file
  df = pandas.read_csv('covid_dataset.csv')

  # filter only positive values
  df =  df[df[TEST_RESULT_COLUMN].eq('Positivo')]

  # transform date columns in pandas datetime
  df[NOTIFICATION_DATE_COLUMN] = pandas.to_datetime(df[NOTIFICATION_DATE_COLUMN], format="%d/%m/%Y")

  # group notifications by date and sort
  notifications = df[NOTIFICATION_DATE_COLUMN].value_counts().sort_index(0)

  # iterate over all notifications and calc moving average
  for index, value in notifications.items():
    for data in mr_data:
      data.add(index, value)

  # show graph
  plt.figure(figsize=[15, 10])
  plt.grid(True)
  plt.plot(notifications, label='Casos Confirmados')
  for data in mr_data:
    plt.plot(data.get_data(), label=data.get_label())
  plt.legend(loc=2)
  plt.show()

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input', '-i', default='samples/Please_Open_The_Door_Loud.wav', help='Input audio file name')
  calc_moving_average([MovingAverageData(7), MovingAverageData(14)])

if __name__ == "__main__":
  main()
