print("in underwriting init")
# import sys
# from pathlib import Path

# project_root = Path(__file__).resolve().parent
# if str(project_root) not in sys.path:
#     sys.path.insert(0, str(project_root))

# tools_path = project_root / "tools"
# if tools_path not in sys.path:
#     sys.path.insert(0, str(tools_path))

# utils_path = project_root / "utils"
# if utils_path not in sys.path:
#     sys.path.insert(0, str(utils_path))


from .tools import doc_tools, parsing_tools
from .utils import payslip_processor
from .utils import load_config
from .utils import loe_processor
from .utils import t4_processor