import yaml

def load_config(data):
    with open("hexactrl_script/configs/XLFL_production_test.yaml") as fin: # TODO Read From Data
        test_config = yaml.safe_load(fin)
        data = {}
        for rid, roc in test_config['rocs'].items():
            data[f'ROC{rid}'] = roc
        return data