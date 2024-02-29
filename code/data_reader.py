import pandas as pd
import csv
from monte_carlo_pricer import Option, PayoffType

class DataManager:  
    def __init__(self, args):  

        self.input_output_manager = InputOutputManager(args)
        self.valid_arguments = self.input_output_manager.valid_arguments
 
        if(self.valid_arguments):
            self.market_data = self.input_output_manager.get_market_data()
            self.trade_data = self.input_output_manager.get_trade_data()

        self.df = self.prepare_pricer_input()
        

    def prepare_pricer_input(self):
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
        
        header = ['trade_id', 'pv', 'delta', 'vega'] 

        with open(r"..\output_data\output.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
 


    def get_market_data(self):
        df = self.read_market_data()

        return df


    def read_market_data(self):
        df = pd.read_csv(r"..\\input_data\\" + self.market_filename)


        return df    


    def get_trade_data(self):
        df = self.read_trade_data()
    
        return df
         

      
    def read_trade_data(self):
        df = pd.read_csv(r"..\\input_data\\" + self.trade_filename)

            
        df['call_put'] = df['call_put'].apply(lambda x: Option(x))
        df['type'] = df['type'].apply(lambda x: PayoffType(x))
        df['expiry'] = (df['expiry'] * 252).astype(int).clip(lower=1)
        df['payment_time'] = (df['payment_time'] * 252).astype(int).clip(lower=1)

        return df

    def validate_args(self, args):
        if len(args) != 4:
            return False
        
        else:
            return True

 

        