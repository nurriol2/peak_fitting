import logging
FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
from setup import build_file_tree
from data_toolbox.preprocessing import ready_all_ucl
from data_toolbox.preprocessing import ready_all_cst


def main():
    
    build_file_tree()
    
    ready_all_ucl()
    ready_all_cst()


    return 

if __name__=="__main__":
    main()