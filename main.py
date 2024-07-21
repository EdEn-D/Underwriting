import sys, os, json
from pathlib import Path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


from underwriting.utils import LoadConfig
from underwriting.utils import LOEProcessor
# from underwriting.utils import T4Processor
# from underwriting.utils import PayslipProcessor

app_config = LoadConfig()


def main():
    client_path = os.path.join(app_config.client_data_directory,"Alex and Patricia\Alex")
    payslip_path = r"N:\Dev\AI\Underwriting\data\clients\Alex and Patricia\Alex\Alexander_Deaibes_Pay_Stub(s)_9tM4WQ8J9J3yc13DgjRkEo.pdf"
    loe_path = r"N:\Dev\AI\Underwriting\data\clients\Alex and Patricia\Alex\LOE - Alexander_Deaibes_Letter(s)_of_Employment_Confirming_Start_Date,_Position_and_Income_1B8mAwSAYfoChPo.pdf"
    t4_path = r"N:\Dev\AI\Underwriting\data\clients\Alex and Patricia\Alex\Alexander LOE 02.08.2024.pdf"
    loe_data = LOEProcessor(loe_path).extract_data()
    print("\nLOE Data: \n",
          json.dumps(loe_data, indent = 2))
    # t4_data = T4Processor(client_path).extract_info()
    # print(t4_data)
    # payslip_data = PayslipProcessor(payslip_path)
    # print(payslip_data.get_earnings('regular' ,agent='csv'))
    # print(payslip_data.get_earnings('ytd' ,agent='csv'))

if __name__ == "__main__":
    main()