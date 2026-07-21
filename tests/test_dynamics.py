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


def test_cluster_transitions_are_deterministic_and_share_endpoint_labels():
    rows = []
    for year, offset in [(2020, 0.0), (2024, 0.4)]:
        for index in range(8):
            rows.append({
                "province_vi": f"P{index}", "region": "X" if index < 4 else "Y", "year": year,
                "D1": float(index + offset), "D2": float((index % 4) + offset),
            })
    panel = pd.DataFrame(rows)
    first = dynamics.cluster_transitions(panel, 2020, 2024, ["D1", "D2"])
    second = dynamics.cluster_transitions(panel, 2020, 2024, ["D1", "D2"])
    assert 2 <= first["selected_k"] <= 6
    assert first["assignments"].equals(second["assignments"])
    assert len(first["assignments"]) == 8
    assert sum(item["n"] for item in first["transitions"]) == 8
    assert abs(sum(item["share"] for item in first["transitions"]) - 1) < 1e-12
    assert first["assignments"].pca_distance.ge(0).all()
    assert len(first["pca_variance"]) == 2


def test_cluster_transitions_respects_manual_k_and_drops_incomplete_pair():
    panel = pd.DataFrame({
        "province_vi": ["A", "A", "B", "B", "C", "C", "D", "D"],
        "region": ["X"] * 8, "year": [2020, 2024] * 4,
        "D1": [1., 1.2, 2., 2.2, 8., 8.2, 9., None],
        "D2": [1., 1.1, 2., 2.1, 8., 8.1, 9., 9.1],
    })
    out = dynamics.cluster_transitions(panel, 2020, 2024, ["D1", "D2"], requested_k=2)
    assert out["selected_k"] == 2 and out["selection_mode"] == "manual"
    assert out["assignments"].province_vi.tolist() == ["A", "B", "C"]
