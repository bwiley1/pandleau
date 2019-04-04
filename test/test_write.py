from pandleau import pandleau
import pandas as pd
import numpy as np
import pathlib

def test_hyper_write_speed(tmp_path):
    mapper = pandleau.mapper
    frame = pd.DataFrame({'int': np.random.random(10000)})
    pandleau(frame).to_hyper(pathlib.Path(tmp_path))