import pandas as pd
import csv
from monte_carlo_pricer import Option, PayoffType

class DataManager:  
    def __init__(self, args):  
        self.input_output_manager = InputOutputManager(args)
        self.valid_arguments = self.input_output_manager.valid_arguments
 
        if(self.valid_arguments):
            self.market_data = self.input_output_manager.read_market_data()
            self.trade_data = self.input_output_manager.read_trade_data()
            self.df = self.prepare_pricer_input()
        
    def prepare_pricer_input(self):
        """
        We join in the market data to the trade data so that each row contains the information necessary to price the trade
        """
        market_data = self.market_data.copy()
        trade_data = self.trade_data.copy()

        all_data = trade_data.merge(market_data, on='underlying', how='left')

        return all_data
    
    def export_to_csv(self, rows):
        self.input_output_manager.write_to_output(rows)



class InputOutputManager:  
    def __init__(self, args):  

        self.valid_arguments = self.validate_args(args)

        if(self.valid_arguments):
            self.trade_filename = args[1]
            self.market_filename = args[2]
            self.output_filename = args[3]

    def write_to_output(self, rows):
        """
        Expects a list of list where each inner list corresponds to a row in the output csv
        Writes to a hardcoded relative location
        """
        
        header = ['trade_id', 'pv', 'delta', 'vega'] 

        with open(r"..\output_data\\" + self.output_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
 
    def read_market_data(self):
        """
        We read the file using hardcoded relative paths, could be moved to config
        """
        df = pd.read_csv(r"..\\input_data\\" + self.market_filename)
        return df   

    def read_trade_data(self):
        """
        We read the file using hardcoded relative paths, could be moved to config
        """
        df = pd.read_csv(r"..\\input_data\\" + self.trade_filename)  
        df['call_put'] = df['call_put'].apply(lambda x: Option(x))
        df['type'] = df['type'].apply(lambda x: PayoffType(x))
        df['expiry'] = (df['expiry'] * 252).astype(int).clip(lower=1)
        df['payment_time'] = (df['payment_time'] * 252).astype(int).clip(lower=1)
        return df

    def validate_args(self, args):
        """
        Very simple validator, could be extended
        """
        if len(args) != 4:
            return False
        
        else:
            return True

 

        