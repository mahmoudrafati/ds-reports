import os 
import pandas as pd




def sort():
    # Sort ds to via date
    pass

def split_ds():
    # Split ds into months
    pass

def save_to_csv():
    # Save to csv in dir by name and filename by month
    pass

def OLDmain():
    base_dir = 'data/datasets/ezb'
    output_base = 'data/datasets/ezb/'
    for file in os.listdir(base_dir):
        if file.endswith('.csv'):
            csv_file = pd.DataFrame(file, sep=';')
            sorted_file = sort(csv_file)
            split_file, filenames = split_ds(sorted_file)
            save_to_csv(split_file, os.path.join(output_base, filenames))      


def main(path, output_path):
    start_time = time.time()  # Start timing
    process_file(path, output_path)
    print(f"Process completed in {time.time() - start_time:.2f} seconds.")  # End timing

if __name__ == '__main__':
    #main()
    path = 'data/raw_pdf/ezb/all_bulletins.csv'
    # df = pd.read_csv(path, sep=';')
    # df = df.head()
    # print(len(df))
    # df['Date'] = pd.to_datetime(df['Date'], errors='raise')
    # print(df.head())
    # df['Month'] = df['Date'].dt.strftime('%B')
    # print(df.head())
    main(path, 'data/raw_pdf/ezb')