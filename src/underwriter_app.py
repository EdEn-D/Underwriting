from utils.load_config import LoadConfig
from utils.loe_processor import LOEProcessor
from utils.t4_processor import T4Processor
import os

app_config = LoadConfig()


def main():
    client_path = os.path.join(app_config.client_data_directory,"Oysharja Sayed and Saadman Ahmed\Oysharja")
    # loe_data = LOEProcessor(client_path).extract_info()
    # print(loe_data)
    t4_data = T4Processor(client_path).extract_info()
    print(t4_data)
    # payslip_data =

if __name__ == "__main__":
    main()