import pytest
from unittest.mock import patch, MagicMock
from dash import Dash
from dopo.dash.app import populate_projects_on_load, update_databases, update_filtered_dataset_options, update_impact_assessment_list

# Mock project class
class MockProject:
    def __init__(self, name):
        self.name = name

@patch("dopo.dash.app.get_projects")
def test_populate_projects_on_load(mock_get_projects):
    mock_get_projects.return_value = [MockProject("Project A"), MockProject("Project B")]
    options, value = populate_projects_on_load(1)
    assert len(options) == 2
    assert options[0]["label"] == "Project A"
    assert value == "Project A"

@patch("dopo.dash.app.activate_project")
@patch("dopo.dash.app.get_databases")
def test_update_databases(mock_get_databases, mock_activate_project):
    mock_get_databases.return_value = ["DB1", "DB2"]
    result = update_databases("MockProject")
    assert result == [{"label": "DB1", "value": "DB1"}, {"label": "DB2", "value": "DB2"}]

@patch("dopo.dash.app.get_classifications_from_database")
def test_update_filtered_dataset_options(mock_get_classifications):
    mock_get_classifications.side_effect = lambda db, key: ["item1", "item2", "market item"]
    sectors, cpc, isic, datasets = update_filtered_dataset_options(
        ["cpc", "isic", ], ["MockDB"], "market"
    )
    assert sectors == []
    assert datasets == []
    assert all("market" in opt["label"] for opt in cpc)
    assert all("market" in opt["label"] for opt in isic)

@patch("dopo.dash.app.activate_project")
@patch("dopo.dash.app.get_methods")
def test_update_impact_assessment_list(mock_get_methods, mock_activate_project):
    mock_get_methods.return_value = [("Method A",), ("Other",)]
    result = update_impact_assessment_list("method", "MockProject", triggered_id="impact-search")
    assert any("Method A" in opt["label"] for opt in result)
