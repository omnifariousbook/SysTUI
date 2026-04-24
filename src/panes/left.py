from textual.app import ComposeResult
from textual.widgets import Static, DataTable

class ProcessTable(Static):

    BORDER_TITLE = "Process"

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("PID", "Name", "USER", "CPU%", "TIME", "MEM%", "MEM (MB)", "Status")
        table.add_rows([("Value1", "Value2", "Value3", "Value4", "Value5", "Value6","Value7", "Value8") for _ in range(30)])
        table.cursor_type = "row"


