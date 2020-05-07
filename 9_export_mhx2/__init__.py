#
#    MakeHuman .mhx2 exporter
#    Copyright (C) Thomas Larsson 2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from export import Exporter
try:
    from exportutils.config import Config as ExportConfig
except ImportError:
    from export import ExportConfig


class Mhx2Config(ExportConfig):
    def __init__(self):
        ExportConfig.__init__(self)
        self.useBinary     = False


class ExporterMhx2(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "MakeHuman Exchange (mhx2)"
        self.filter = "MakeHuman Exchange (*.mhx2)"
        self.fileExtension = "mhx2"
        self.orderPriority = 80.0
        self.useBinary = False

    def build(self, options, taskview):
        import gui
        Exporter.build(self, options, taskview)
        self.useBinary   = options.addWidget(gui.CheckBox("Binary file", False))
        self.useExpressions   = options.addWidget(gui.CheckBox("Expressions", False))
        self.usePoses   = options.addWidget(gui.CheckBox("Poses", False))
        #self.feetOnGround   = options.addWidget(gui.CheckBox("Feet on ground", True))

    def export(self, human, filename):
        from . import mh2mhx2
        #self.taskview.exitPoseMode()
        cfg = self.getConfig()
        cfg.setHuman(human)
        mh2mhx2.exportMhx2(filename("mhx2"), cfg)
        #self.taskview.enterPoseMode()

    def getConfig(self):
        cfg = Mhx2Config()
        cfg.useTPose          = False
        cfg.useBinary         = self.useBinary.selected
        cfg.useExpressions    = self.useExpressions.selected
        cfg.usePoses          = self.usePoses.selected
        cfg.feetOnGround      = self.feetOnGround.selected
        cfg.scale,cfg.unit    = self.taskview.getScale()

        return cfg

def load(app):
    app.addExporter(ExporterMhx2())

def unload(app):
    pass

