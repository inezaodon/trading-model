"""CLI smoke tests."""

import json

from mc_option_pricing.cli import main


def test_price_json(capsys):
    code = main(["price", "--sample", "AAPL", "--n-paths", "2000", "--seed", "5"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert "price" in payload
    assert "stderr" in payload
    assert "bs_price" in payload
    assert payload["paths_used"] == 2000
    assert "params" in payload
    assert payload["params"]["sample"] == "AAPL"


def test_converge_json(capsys):
    code = main(
        [
            "converge",
            "--spot",
            "100",
            "--strike",
            "100",
            "--rate",
            "0.05",
            "--vol",
            "0.2",
            "--maturity",
            "1",
            "--path-counts",
            "500,1000",
            "--seed",
            "2",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["n_paths"] == [500, 1000]
    assert len(payload["mc_price"]) == 2


def test_samples_json(capsys):
    code = main(["samples"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert "QQQ" in payload["samples"]
    assert "NVDA" in payload["samples"]


def test_sample_override_strike(capsys):
    code = main(["price", "--sample", "QQQ", "--strike", "500", "--n-paths", "1500", "--seed", "1"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["params"]["strike"] == 500.0
    assert payload["params"]["spot"] == 480.0  # from sample
