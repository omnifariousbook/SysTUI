# Texutal Library
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical, VerticalScroll
from textual.widgets import Footer, Static, TabbedContent, TabPane, Rule
from textual.binding import Binding
from textual import log

# psutil Library
import psutil

# Collections Library
from collections import deque

# time module
import time

# SysTUI custom module
from panes.left import ProcessTable
from panes.top import getUnit, systemName, cores, processorName, bar, perCoreDisplay, renderGraph, renderTank, speedPerSecond
from panes.right import upTime, logUpdate, getSysInfo


#-------------------------------APP-----------------------------------
class SysTUI(App):
    CSS_PATH = "systui.tcss"


    # Footer keybinds
    BINDINGS = [Binding(key="^q", action="quit", description="Quit")]

    # Disable Textual default command palette
    ENABLE_COMMAND_PALETTE = True

    # Everything that contain in side the app
    def compose(self) -> ComposeResult:
        # Footer at the buttom of the app
        yield Footer(show_command_palette=True)

        # container to store and split into part
        with Container(id="app-grid"):
            with TabbedContent(id="top"):

                with TabPane("CPU", id="cpu-pane"):
                    with ScrollableContainer(id="left-cpu"):
                        # add empty stuff before the actual data load to make it look more instentinous
                        yield Static(f"", id="overall-cpu")

                        # add empty stuff before the actual data load to make it look more instentinous
                        yield Static("Loading...", id="all-cpu")

                    yield Static(id="cpu-graph")

                with TabPane("MEMORY", id="mem-pane"):
                    yield Static("", id="mem-tank")
                    yield Static("", id="mem-graph")
                    yield Static("", id="swap-graph")
                    yield Static("", id="swap-tank")

                with TabPane("DISK", id="disk-pane"):
                    with VerticalScroll(id="diskinfo-scroll"):
                        yield Static("", id="disk-info")
                    with Vertical(id="disk-container"):
                        yield Static("", id="read-disk-graph")
                        yield Static("", id="write-disk-graph")

                with TabPane("NETWORK", id="net-pane"):
                    with VerticalScroll(id="netinfo-scroll"):
                        yield Static("Loading...", id="net-info")
                    with Vertical(id="net-container"):
                        yield Static("", id="send-net-graph")
                        yield Static("", id="recv-net-graph")

            with Container(id="bottom-left"):
                yield ProcessTable()

            with Container(id="bottom-right"):
                with VerticalScroll(id="sys-container"):
                    yield Static(getSysInfo(), id="sys-info")
                with VerticalScroll(id="log-container"):
                    yield Static("", id="log-info")



    def on_mount(self) -> None:
        # Theme
        self.theme = "gruvbox"

        self.get_css_variables()
        # ----------------------------------Top-------------------------------------

        # ----------------CPU---------------
        top = self.query_one("#top", TabbedContent)
        top.border_title = f"[white]{systemName}[/]"

        self.leftCPU = self.query_one("#left-cpu", ScrollableContainer)
        self.leftCPU.border_title = f"[white]{processorName()}[/]"
        self.leftCPU.border_subtitle = f"[white]Cores:[/] [$primary]{cores}[/]"

        self.cpuBar = self.query_one("#overall-cpu", Static)
        self.perCoreBar = self.query_one("#all-cpu", Static)

        self.cpuGraph = self.query_one("#cpu-graph", Static)
        self.cpuGraph.border_title = "[white]CPU Status[/white]"

        log(self.cpuGraph.size.width)
        log(self.cpuGraph.size.height)


        # ----------------MEMORY---------------
        self.memTank = self.query_one("#mem-tank", Static)
        self.swapTank = self.query_one("#swap-tank", Static)
        self.memGraph = self.query_one("#mem-graph", Static)
        self.swapGraph = self.query_one("#swap-graph", Static)


        # -----------------DISK----------------
        self.diskInfoScroll = self.query_one("#diskinfo-scroll", VerticalScroll)
        self.diskInfo = self.query_one("#disk-info", Static)
        self.diskContainer = self.query_one("#disk-container", Vertical)
        self.readGraph = self.query_one("#read-disk-graph", Static)
        self.writeGraph = self.query_one("#write-disk-graph", Static)

        # Store highest value here so the next one can compare to
        self.highestRead = 0
        self.highestWrite = 0

        # -----------------NETWORK----------------
        self.netInfoScroll = self.query_one("#netinfo-scroll", VerticalScroll)
        self.netInfo = self.query_one("#net-info", Static)
        self.netContainer = self.query_one("#net-container", Vertical)
        self.sendGraph = self.query_one("#send-net-graph", Static)
        self.recvGraph = self.query_one("#recv-net-graph", Static)

        # Store highest value here so the next one can compare to
        self.highestSend = 0
        self.highestRecv = 0

        # -----------------DELTA DISK & NETWORK----------------
        # To get the read and write speed we will do delta calculation
        self.disk1 = psutil.disk_io_counters()
        self.net1 = psutil.net_io_counters()
        self.time1 = time.time()

        # ------------------------------Bottom left----------------------------------
        bottomLeft = self.query_one("#bottom-left", Container)
        bottomLeft.border_title = "[white]Processes[/white]"

        # ------------------------------Bottom right---------------------------------
        bottomRight = self.query_one("#bottom-right", Container)
        bottomRight.border_title = "[white]Info[/white]"

        self.sysInfo = self.query_one("#sys-info", Static)

        logContainer = self.query_one("#log-container", VerticalScroll)
        logContainer.border_title = "[white]Logs[/white]"

        self.logInfo = self.query_one("#log-info", Static)


        # Updata CPU data
        # store all history and data for graph here because it can live until program die
        self.cpuHistory = deque([0.0] * 128, maxlen=128)
        self.memHistory = deque([0.0] * 52, maxlen=52)
        self.swapHistory = deque([0.0] * 52, maxlen=52)
        self.readHistory = deque([0.0] * 136, maxlen=136)
        self.writeHistory = deque([0.0] * 136, maxlen=136)
        self.sendHistory = deque([0.0] * 136, maxlen=136)
        self.recvHistory = deque([0.0] * 136, maxlen=136)

        self.set_interval(1, self.longUpdate)


    # Add on functions--------------------------------------------------------------
    # Update CPU data. This function will be called every 1 second so any value update is possible
    def longUpdate(self) -> None:

        # ----------------------------------Top-------------------------------------
        # ----------------CPU---------------
        perCore = psutil.cpu_percent(interval=None, percpu=True)
        cpuOverall = round(sum(perCore) / len(perCore), 1)
        cpuColor = "$success" if cpuOverall < 60 else ("$warning" if 60 < cpuOverall < 80 else "$error")

        # add data to the list so it can show in the graph
        self.cpuHistory.append(cpuOverall)

        # Overall bar
        self.cpuBar.border_title = f"[white]Usage:[/] [{cpuColor}]{cpuOverall}[/] [white]%[/]"
        self.cpuBar.update(bar(cpuOverall, totalBlock=self.leftCPU.size.width - 4))

        # Per core bar
        self.perCoreBar.update(perCoreDisplay(perCore, self.perCoreBar.size.width))


        # Get the actual rendered size of the widget
        graph = self.cpuGraph
        h = graph.size.height
        w = graph.size.width
        cpuHistoryAsList = list(self.cpuHistory)[len(self.cpuHistory) - (w-2):-1]
        graph.update(renderGraph(cpuHistoryAsList, h, 100.0))

        # ----------------MEMORY---------------
        mem = psutil.virtual_memory()
        memPercent = mem.percent
        memTotal = mem.total / (1024 ** 3)
        # Because of the way memory work mem.available is the number we want to see. Unlike free which only show the memory that not being used at all, available show both free and used that can be return when need right away.
        memUsed = mem.used / (1024 ** 3)
        memColor = "$success" if memPercent < 60 else ("$warning" if 60 < memPercent < 80 else "$error")
        self.memHistory.append(memPercent)

        swap = psutil.swap_memory()
        swapPercent = swap.percent
        swapTotal = swap.total / (1024 ** 3)
        # Swap does not work like memory so free and available is the same
        swapUsed = swap.used / (1024 ** 3)
        swapColor = "$success" if swapPercent < 60 else ("$warning" if 60 < swapPercent < 80 else "$error")
        self.swapHistory.append(swapPercent)

        # Title and Subtitle
        mtank = self.memTank
        mtank.border_title = f"Usage: [{memColor}]{memUsed:.1f}G/{memTotal:.1f}G ({memPercent:5<.1f}%)[/]"
        mtank.border_subtitle = f"Total [$primary]⣿[/], Used [{memColor}]⣿[/]"

        stank = self.swapTank
        stank.border_title = f"Usage: [{swapColor}]{swapUsed:.1f}G/{swapTotal:.1f}G ({swapPercent:5<.1f}%)[/]"
        stank.border_subtitle = f"Total [$primary]⣿[/], Used [{memColor}]⣿[/]"


        # Tank
        mth = mtank.size.height
        mtw = mtank.size.width

        sth = stank.size.height
        stw = stank.size.width

        if mtw > 0:
            mtank.update(renderTank(memPercent, mth, mtw))
        if stw > 0:
            stank.update(renderTank(swapPercent, sth, stw))


        # Graph
        mh = self.memGraph.size.height
        mw = self.memGraph.size.width
        memHistoryAsList = list(self.memHistory)[len(self.memHistory) - (mw-2): - 1]
        self.memGraph.update(renderGraph(memHistoryAsList, mh, 100.0))
        
        sh = self.swapGraph.size.height
        sww = self.swapGraph.size.width
        swapHistoryAsList = list(self.swapHistory)[len(self.swapHistory) - (sww-2): - 1]
        self.swapGraph.update(renderGraph(swapHistoryAsList, sh, 100.0))


        # ----------------DELTA DISK & NETWORK---------------
        # The second value that we need for delta calculation
        time2 = time.time()
        disk2 = psutil.disk_io_counters()
        net2 = psutil.net_io_counters()


        # TODO: on Windows "diskperf -y" command may need to be executed first otherwise this function won’t find any disk.

        # ----------------DISK---------------

        # LEFT
        # TODO: Update disk information here
        self.diskInfo.update() 

        # RIGHT

        readps = speedPerSecond(self.disk1.read_bytes, disk2.read_bytes, self.time1, time2)
        writeps = speedPerSecond(self.disk1.write_bytes, disk2.write_bytes, self.time1, time2)

        # update list
        self.readHistory.append(readps)
        self.writeHistory.append(writeps)

        # update highest value if the current one is higher
        if readps > self.highestRead:
            self.highestRead = readps

        if writeps > self.highestWrite:
            self.highestWrite = writeps

        # border title and subtitle
        self.diskContainer.border_title = f"[$primary]▲ Read: {getUnit(readps)}B/s, Highest: {getUnit(self.highestRead)}B/s[/]"
        self.diskContainer.border_subtitle = f"[$accent]▼ Write: {getUnit(writeps)}B/s, Highest: {getUnit(self.highestWrite)}B/s[/]"

        # Graph
        diskContainerWidth = self.diskContainer.size.width
        rh = self.readGraph.size.height
        wh = self.readGraph.size.height

        readHistoryAsList = list(self.readHistory)[len(self.readHistory) - (diskContainerWidth-3):-1]
        writeHistoryAsList = list(self.writeHistory)[len(self.writeHistory) - (diskContainerWidth-3):-1]

        self.readGraph.update(renderGraph(readHistoryAsList, rh, self.highestRead, colorInput="$primary"))
        self.writeGraph.update(renderGraph(writeHistoryAsList, wh, self.highestWrite, colorInput="$accent", upsidedown=True))


        # ----------------NETWORK---------------
        # LEFT
        # TODO: Update network information here
        self.netInfo.update()
 
        # RIGHT
        sendps = speedPerSecond(self.net1.bytes_sent, net2.bytes_recv, self.time1, time2)
        recvps = speedPerSecond(self.net1.bytes_recv, net2.bytes_recv, self.time1, time2)

        # update list
        self.sendHistory.append(sendps)
        self.recvHistory.append(recvps)
        
        # update highest value if the current one is higher
        if sendps > self.highestSend:
            self.highestSend = sendps

        if recvps > self.highestRecv:
            self.highestRecv = recvps

        # border title and subtitle
        self.netContainer.border_title = f"[$primary]▲ Send: {getUnit(sendps)}B/s, Highest: {getUnit(self.highestSend)}B/s[/]"
        self.netContainer.border_subtitle = f"[$accent]▼ Receive: {getUnit(recvps)}B/s, Highest: {getUnit(self.highestRecv)}B/s[/]"

        # Graph
        netContainerWidth = self.netContainer.size.width
        sh = self.sendGraph.size.height
        rh = self.recvGraph.size.height

        sendHistoryAsList = list(self.sendHistory)[len(self.sendHistory) - (netContainerWidth-3):-1]
        recvHistoryAsList = list(self.recvHistory)[len(self.recvHistory) - (netContainerWidth-3):-1]

        self.sendGraph.update(renderGraph(sendHistoryAsList, sh, self.highestSend, colorInput="$primary"))
        self.recvGraph.update(renderGraph(recvHistoryAsList, rh, self.highestRecv, colorInput="$accent", upsidedown=True))



        # ----------------------UPDATE VALUE FOR DISK & NETWORK----------------------
        # update the previous value so the next new value can compare to it
        self.disk1 = disk2
        self.net1 = net2
        self.time1 = time2

        # ------------------------------Bottom right---------------------------------

        # update log
        self.logInfo.update(logUpdate(cpuOverall, memPercent, swapPercent))

        # Bottom right
        # update this here because it contain time which need to update every second
        self.sysInfo.update(getSysInfo())







#-----------------------------RUN APP---------------------------------
if __name__ == "__main__":
    app = SysTUI()
    app.run()

