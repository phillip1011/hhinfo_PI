from models.DeviceModel import DeviceModel
from models.ServerModel import ServerModel
from models.ScannerModel import ScannerModel



def initialize(): 
    initDevice()
    initServer()
    initScanner()

def initServer():
    global _server
    _server = ServerModel()
  

def initScanner():
    global _scanner
    _scanner = ScannerModel()

def initDevice():
    global _device
    _device = DeviceModel()
    