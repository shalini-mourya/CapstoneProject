# Agent, Planner, Memory classes -import and register the tool
from tools.pdf_tool import PDFTool
from tools.storage_tool import StorageTool

memory = InMemoryStore()
pdf_tool = PDFTool()
storage_tool = StorageTool()

agent = Agent(memory=memory, tools=[pdf_tool, storage_tool])