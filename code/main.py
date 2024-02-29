import yaml
import os, sys
import numpy as np
from monte_carlo_pricer import MonteCarloPricer, Option, PayoffType
from data_reader import InputOutputManager, DataManager
from task_runner import TaskRunner


def main():
    file_path = os.path.dirname(__file__)
    os.chdir(file_path)
 
    with open(r"..\config\config.yaml") as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

    #data_manager = DataManager(sys.argv)
    data_manager = DataManager(["", "trade_data.csv", "market_data.csv", "cc.csv "])

    if data_manager.valid_arguments:
        input_df = data_manager.df
        task_runner = TaskRunner(input_df, cfg)
        output_rows = task_runner.do_task_1()
        data_manager.export_to_csv(output_rows)

        # Lägg till ett par rader med exempeldata här, det står tydligt att endast en funktion efterfrågas, behöver inte överarbeta!!!
        task_runner.get_implied_volatility()    

if __name__ == "__main__":
    main()




