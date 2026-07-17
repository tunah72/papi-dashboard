import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analysis import dynamics

def test_changes_keeps_complete_pairs():
    d=pd.DataFrame({"province_vi":["A","A","B","B"],"region":["X"]*4,"year":[2020,2024,2020,2024],"score":[1.,3.,2.,1.]})
    out=dynamics.changes(d,"score",2020,2024)
    assert out.province_vi.tolist()==["A","B"] and out.change.tolist()==[2.,-1.]

def test_cluster_profiles_assigns_every_complete_province():
    d=pd.DataFrame({"province_vi":["A","B","C","D"],"region":["X"]*4,"year":[2024]*4,"D1":[1.,2.,8.,9.],"D2":[1.,2.,8.,9.]})
    out=dynamics.cluster_profiles(d,2024,["D1","D2"],2)
    assert len(out)==4 and out.cluster.nunique()==2
