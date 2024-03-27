from utils.load_config import LoadConfig
from utils.loe_processor import LOEProcessor
from utils.t4_processor import T4Processor
from utils.payslip_processor import PayslipProcessor
import os

app_config = LoadConfig()


def main():
    client_path = os.path.join(app_config.client_data_directory,"Alex and Patricia\Alex")
    payslip_path = r"N:\Dev\AI\Underwriting\data\clients\Alex and Patricia\Alex\Alexander_Deaibes_Pay_Stub(s)_9tM4WQ8J9J3yc13DgjRkEo.pdf"
    # loe_data = LOEProcessor(client_path).extract_info()
    # print(loe_data)
    # t4_data = T4Processor(client_path).extract_info()
    # print(t4_data)
    payslip_data = PayslipProcessor(payslip_path)
    # print(payslip_data.get_earnings('regular' ,agent='csv'))
    print(payslip_data.get_earnings('ytd' ,agent='csv'))

if __name__ == "__main__":
    main()