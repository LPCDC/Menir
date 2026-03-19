import pytest
import os
import pandas as pd
from src.v3.skills.excel_parser import BecoExcelParser

@pytest.fixture
def mock_excel_path(tmp_path):
    # Criar um Excel fake seguindo o mapeamento da Nicole
    path = tmp_path / "test_invoice.xlsx"
    data = [
        [None] * 5, [None] * 5, [None] * 5, [None] * 5, [None] * 5,
        [None, 'BECO', None, None, None],
        [None, 'Titulaire Nicole Berra', None, None, None],
        [None, 'Avenue des Morgines 12,', None, None, None],
        [None, '1213 Petit-Lancy', None, None, None],
        [None, None, None, 'My Café Bar Sàrl', None], # Row 9 (Index)
        [None, None, None, 'Avenue Wendt 7,', None],
        [None, None, None, '1203 Genève', None],
        [None] * 5, [None] * 5,
        [None, None, None, 'Genève, le 27 février 2026', None],
        [None] * 5, [None] * 5,
        [None, 'F A C T U R E', None, 'payable dès réception', None],
        [None] * 5,
        [None, 'date : 27.02.2026', None, ' ', None], # Row 19
        [None, 'numéro de facture: 6026/2026', None, ' ', None], # Row 20
        [None] * 5,
        [None, ' Description', 'Quantité', 'Prix unitaire / h.  ', 'Prix facturé '],
        [None] * 5,
        [None, 'Forfait : Prestations Février 2026', None, None, None],
        [None] * 5,
        [None, 'Comptabilité Février 2026', 1, 220, 220],
        [None, 'Salaires Février 2026', 4, 45, 180],
        [None] * 5,
        [None, '   solde en notre faveur :', None, None, 400] # Row 29
    ]
    df = pd.DataFrame(data)
    df.to_excel(path, index=False, header=False)
    return str(path)

def test_beco_excel_extraction(mock_excel_path):
    parser = BecoExcelParser()
    result = parser.parse(mock_excel_path)
    
    assert result["client_name"] == "My Café Bar Sàrl"
    assert "Avenue Wendt 7" in result["client_address"]
    assert result["invoice_number"] == "6026/2026"
    assert result["invoice_date"] == "27.02.2026"
    assert result["total_amount"] == 400.0
    assert len(result["services"]) == 2
    assert result["services"][0]["description"] == "Comptabilité Février 2026"
    assert result["services"][0]["quantity"] == 1
    assert float(result["services"][0]["unit_price"]) == 220.0
