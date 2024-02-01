# %%
import os
import pandas as pd
import plotly.express as px
from dataclasses import dataclass

# %%
@dataclass
class Machine_data:

    folder_path: str 
    start_date: str
    end_date: str


    def get_csv_files(self):
        folder_path = self.folder_path
        files = os.listdir(folder_path)
        csv_files = [file for file in files if file.endswith('.csv')]

        start_date = self.start_date.replace('-', '')
        end_date = self.end_date.replace('-', '')

        csv_files = [file for file in csv_files if int(file.replace('.csv', '')) >= int(start_date) and int(file.replace('.csv', '')) <= int(end_date)]

        return csv_files

    
    def make_dataframe(self, csv_file):
        df = pd.read_csv(f'{ self.folder_path}/{csv_file}')
        df.dropna(how='all', axis=1, inplace=True)
        # Create timestamp column with 10 secoonds interval
        df['timestamp'] = pd.date_range('2024-01-01', periods=len(df), freq="10s")
        
        df['start']= pd.to_datetime(df['timestamp'])
        df['end']= pd.to_datetime(df['timestamp']) + pd.Timedelta(seconds=10)
        df['resource'] = f'{csv_file[0:4]}-{csv_file[4:6]}-{csv_file[6:8]}'

        return df
    

    def create_machine_state(self, df):

        # Check alarm
        if df['ATMD_ALARM'] == 1:
            return 'ALARM'

        # Auto Kjøring
        elif (df['ATMD_MEM'] == 1 or df['ATMD_TAPE'] == 1) and \
            df['SGNL_DEN2'] == 0 and \
            all(df[col] == 0 for col in ['SGNL_SMZ', 'SGNL_INP', 'SGNL_AFC']) and \
            (df['SGNL_CUT'] == 1 or df['SGNL_CXF'] == 1) and \
            all(df[col] == 1 for col in ['SGNL_STL', 'SGNL_OP']):

            return 'AUTO KJØRING'
        
        # Feed Hold
        elif (df['ATMD_MEM'] == 1 or df['ATMD_TAPE'] == 1) and \
            (df['SGNL_DEN2'] == 1  or df['SGNL_DEN2'] == 0) and \
            (df['SGNL_CXF'] == 1 or df['SGNL_CXF'] == 0) and \
            all(df[col] == 1 for col in ['SGNL_SMZ', 'SGNL_INP', 'SGNL_AFC']) and \
            (df['SGNL_OP'] == 1 or df['SGNL_OP'] == 0):

            return 'FEED HOLD'

        # Oppsett
        elif any(df[col] == 1 for col in ['ATMD_MDI', 'ATMD_NA.3', 'MNMD_RET', 'MNMD_PTP', 'MNMD_STEP', 'MNMD_HAND', 'MNMD_JOG']) and \
            any(df[col] == 1 for col in ['SGNL_SMZ', 'SGNL_INP', 'SGNL_AFC']):
            return 'OPPSETT'
        
        else:
            return 'empty'
    

    def get_dataframe(self):
        dates = self.get_csv_files()
        new_df = pd.DataFrame()

        for date in dates:
            df = self.make_dataframe(date)
            df['Machine_State'] = df.apply(self.create_machine_state, axis=1)
            new_df = pd.concat([new_df, df])
        
        return new_df
        

    def plot(self):
        df = self.get_dataframe()

        colors = {'OPPSETT': '#cce619',
                'AUTO KJØRING': '#3617e8',
                'FEED HOLD': '#2ed140',
                'ALARM': '#f80d07',
                'empty': 'rgba(0, 0, 0, 0)'}

        fig = px.timeline(df, x_start="start", x_end="end", y="resource", color='Machine_State', color_discrete_map=colors)
        fig.update_traces(marker_line_color='rgba(0,0,0,0)', marker_line_width=1, opacity=1)
        fig.update_layout(template='plotly_dark', width=1000, height=500)

        # Add vertical line skipping each 3 hours
        for hour in range(24):
            if hour % 3 != 0:
                fig.add_vline(x=f'2024-01-01 {hour}:00:00', line_width=0.5, line_dash="dot", line_color="grey", opacity=0.5)

        fig.show()


# %%
if __name__ == '__main__':
    
    # To use this code, create a folder and put all the csv files in it. Then, pass the folder path, start date and end date to the Machine_data class.
    # Format for start and end date: 'YYYY-MM-DD'
    
    machine_data = Machine_data(folder_path='timelines4', start_date='2024-01-03', end_date='2024-01-09')
    machine_data.plot()
# %%

