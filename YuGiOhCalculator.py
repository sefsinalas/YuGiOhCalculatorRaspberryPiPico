# *****************************************************************************
# * | File        :	  YuGiOhCalculator.py
# * | Author      :   Eduardo Federico Santillan (sefsinalas)
# * | Function    :   Being a YuGiOh calculator and the first experiment with a raspberry pi pico
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2023-07-01
# # | Info        :   None
# -----------------------------------------------------------------------------

from machine import Pin, SPI
import framebuf
import utime

class Keyboard():

    def __init__(self):
        # Estos son los pines de la raspberry pi que usamos
        self.col_list = [1,2,3,4]
        self.row_list = [5,6,7,15]
        self.key_map = []

        # Seteamos los pines de ROWs para que sean de salida y que devuelvan el valor 1
        for x in range(0,4):
            self.row_list[x] = Pin(self.row_list[x], Pin.OUT)
            self.row_list[x].value(1)
            
        # Seteamos los pintos de COLs para que sean los de lectura
        for x in range(0,4):
            self.col_list[x] = Pin(self.col_list[x], Pin.IN, Pin.PULL_UP)
            
        # Creamos el keymap
        self.key_map=[["D","#","0","*"],\
                ["C","9","8","7"],\
                ["B","6","5","4"],\
                ["A","3","2","1"]]
        
    def Keypad4x4Read(self, cols, rows):
        for r in rows:
            r.value(0)
            result = [cols[0].value(), cols[1].value(), cols[2].value(), cols[3].value()]
            if min(result)==0:
                #print(int(rows.index(r)))
                #print(int(result.index(0)))
                key = self.key_map[int(rows.index(r))][int(result.index(0))]
                r.value(1) # manages key keept pressed
                return(key)
            r.value(1)
    
    def readKey(self):
        while True:
            key = self.Keypad4x4Read(self.col_list, self.row_list)
            if key != None:
                print("You pressed: " + key)
                return key

# Display resolution
EPD_WIDTH       = 128
EPD_HEIGHT      = 296

RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13

WF_PARTIAL_2IN9 = [
    0x0,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x80,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x40,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0A,0x0,0x0,0x0,0x0,0x0,0x1,  
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x22,0x22,0x22,0x22,0x22,0x22,0x0,0x0,0x0,
    0x22,0x17,0x41,0xB0,0x32,0x36,
]
       

class EPD_2in9_Landscape(framebuf.FrameBuffer):
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
        self.lut = WF_PARTIAL_2IN9
        
        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        
        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.height, self.width, framebuf.MONO_VLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)   

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        print("e-Paper busy")
        while(self.digital_read(self.busy_pin) == 1):      #  0: idle, 1: busy
            self.delay_ms(10) 
        print("e-Paper busy release")  

    def TurnOnDisplay(self):
        self.send_command(0x22) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0xF7)
        self.send_command(0x20) # MASTER_ACTIVATION
        self.ReadBusy()

    def TurnOnDisplay_Partial(self):
        self.send_command(0x22) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0x0F)
        self.send_command(0x20) # MASTER_ACTIVATION
        self.ReadBusy()

    def SendLut(self):
        self.send_command(0x32)
        for i in range(0, 153):
            self.send_data(self.lut[i])
        self.ReadBusy()

    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44) # SET_RAM_X_ADDRESS_START_END_POSITION
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start>>3) & 0xFF)
        self.send_data((x_end>>3) & 0xFF)
        self.send_command(0x45) # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    def SetCursor(self, x, y):
        self.send_command(0x4E) # SET_RAM_X_ADDRESS_COUNTER
        self.send_data(x & 0xFF)
        
        self.send_command(0x4F) # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        self.ReadBusy()
        
    def init(self):
        # EPD hardware init start     
        self.reset()

        self.ReadBusy()   
        self.send_command(0x12)  #SWRESET
        self.ReadBusy()   

        self.send_command(0x01) #Driver output control      
        self.send_data(0x27)
        self.send_data(0x01)
        self.send_data(0x00)
    
        self.send_command(0x11) #data entry mode       
        self.send_data(0x07)

        self.SetWindow(0, 0, self.width-1, self.height-1)

        self.send_command(0x21) #  Display update control
        self.send_data(0x00)
        self.send_data(0x80)
    
        self.SetCursor(0, 0)
        self.ReadBusy()
        # EPD hardware init end
        return 0

    def display(self, image):
        if (image == None):
            return            
        self.send_command(0x24) # WRITE_RAM
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])   
        self.TurnOnDisplay()

    def display_Base(self, image):
        if (image == None):
            return   
        self.send_command(0x24) # WRITE_RAM
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])    
                
        self.send_command(0x26) # WRITE_RAM
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])      
                
        self.TurnOnDisplay()
        
    def display_Partial(self, image):
        if (image == None):
            return
            
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(2)   
        
        self.SendLut()
        self.send_command(0x37) 
        self.send_data(0x00)  
        self.send_data(0x00)  
        self.send_data(0x00)  
        self.send_data(0x00) 
        self.send_data(0x00)  
        self.send_data(0x40)  
        self.send_data(0x00)  
        self.send_data(0x00)   
        self.send_data(0x00)  
        self.send_data(0x00)

        self.send_command(0x3C) #BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x22) 
        self.send_data(0xC0)   
        self.send_command(0x20) 
        self.ReadBusy()

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)
        
        self.send_command(0x24) # WRITE_RAM
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])    
        self.TurnOnDisplay_Partial()

    def display_Partial_Custom(self, image):
        if (image == None):
            return

        self.send_command(0x24) # WRITE_RAM
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(image[i + j * self.height])    
        self.TurnOnDisplay_Partial()
        
    def Clear(self, color):
        self.send_command(0x24) # WRITE_RAM
        for j in range(int(self.width / 8) - 1, -1, -1):
            for i in range(0, self.height):
                self.send_data(color)
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10) # DEEP_SLEEP_MODE
        self.send_data(0x01)
        
        self.delay_ms(2000)
        self.module_exit()

    def clear_line(self, y, color=0xff):
        # Each character is 8 pixels high
        y_start = y
        y_end = y_start + 7

        for x in range(0, self.height):
            for y in range(y_start, y_end + 1):
                self.pixel(x, y, color)
        
        self.display_Partial(self.buffer)

    def clear_partial_line(self, y, xStart, xFinish, color=0xff):
        # Each character is 8 pixels high
        y_start = y
        y_end = y_start + 7

        for x in range(xStart, xFinish):
            for y in range(y_start, y_end + 1):
                self.pixel(x, y, color)
        
        self.display_Partial(self.buffer)
    
    def clear_first_line_section(self, color=0xff):
        # Each character is 8 pixels high
        y_start = 120
        y_end = y_start + 7

        for x in range(0, 180):
            for y in range(y_start, y_end + 1):
                self.pixel(x, y, color)
        
        self.display_Partial(self.buffer)

    def clear_second_line_section(self, color=0xff):
        # Each character is 8 pixels high
        y_start = 120
        y_end = y_start + 7

        for x in range(181, 230):
            for y in range(y_start, y_end + 1):
                self.pixel(x, y, color)
        
        self.display_Partial(self.buffer)

    def clear_third_line_section(self, color=0xff):
        # Each character is 8 pixels high
        y_start = 120
        y_end = y_start + 7

        for x in range(231, 290):
            for y in range(y_start, y_end + 1):
                self.pixel(x, y, color)
        
        self.display_Partial(self.buffer)
        

class Game():
    

    def __init__(self):
        # Jugadores
        self.players_list=["CHANCHO", "JAVI", "PERRO"]
        self.player1 = ""
        self.player2 = ""
        self.epd = EPD_2in9_Landscape()
        self.keypad = Keyboard()
        self.epd.fill(1)
        self.epd.Clear(0xff)
        self.selectedPlayer = 1
        self.lifePointsPlayer1 = 8000
        self.lifePointsPlayer2 = 8000
        self.lifePointPlayer1Array = [8000]
        self.lifePointPlayer2Array = [8000]
        self.actualOperation = "ADD"
        self.actualNumberString = ""
        self.enableReset = False
        self.enableTurnOff = False

    def start(self):
        print("Iniciando...")
        self.epd.text("INICIANDO", 0, 0, 0xff)
        self.epd.display_Partial(self.epd.buffer)
        self.epd.delay_ms(100)
        self.epd.text("INICIANDO.", 0, 0, 0)
        self.epd.display_Partial(self.epd.buffer)
        self.epd.delay_ms(100)
        self.epd.text("INICIANDO..", 0, 0, 0)
        self.epd.display_Partial(self.epd.buffer)
        self.epd.delay_ms(100)
        self.epd.text("INICIANDO...", 0, 0, 0)
        self.epd.display_Partial(self.epd.buffer)
        self.epd.delay_ms(100)
        self.epd.fill(0xff)
        self.epd.display_Partial(self.epd.buffer)

    def selectPlayers(self):
        self.epd.Clear(0xff)
        self.epd.fill(0xff)
        self.epd.text("ELIJA EL JUGADOR DE LA IZQUIERDA", 0, 0, 0)
        self.epd.text("1 para " + self.players_list[0], 0, 10, 0)
        self.epd.text("2 para " + self.players_list[1], 0, 20, 0)
        self.epd.text("3 para " + self.players_list[2], 0, 30, 0)
        self.epd.display_Partial(self.epd.buffer)

        player1Selected = False
        while player1Selected == False:
            key = self.keypad.readKey()
            utime.sleep(0.3)
            if key in ["1", "2", "3"]:
                self.player1 = self.players_list[int(key) - 1]
                player1Selected = True

        self.epd.fill(1)
        self.epd.text("ELIJA EL JUGADOR DE LA DERECHA", 0, 0, 0)
        self.epd.text("1 para " + self.players_list[0], 0, 10, 0)
        self.epd.text("2 para " + self.players_list[1], 0, 20, 0)
        self.epd.text("3 para " + self.players_list[2], 0, 30, 0)
        self.epd.display_Partial(self.epd.buffer)

        player2Selected = False
        while player2Selected == False:
            key = self.keypad.readKey()
            utime.sleep(0.3)
            if key in ["1", "2", "3"]:
                self.player2 = self.players_list[int(key) - 1]
                player2Selected = True

        print("Jugador 1: " + self.player1)
        print("Jugador 2: " + self.player2)

    def drawBoard(self):
        self.epd.fill(0xff)
        self.epd.vline(148, 5, 108, 0x00)
        self.epd.hline(4, 18, 290, 0x00)
        self.epd.hline(4, 112, 290, 0x00)
        self.epd.text(self.player1, 50, 5, 0x00)
        self.epd.text(self.player2, 204, 5, 0x00)

        self.epd.display(self.epd.buffer)
        self.epd.delay_ms(2000)
    
    def waitNextAction(self):
        key = self.keypad.readKey()

        # Selecciona el jugador actual y lo muestra en pantalla
        if(key == "*"):
            if(self.selectedPlayer == 1): 
                self.setPlayer(2)
            else:
                self.setPlayer(1)
        
        # Agrega puntos al jugador actual si oprime la tecla A
        if(key == "A"):
            self.epd.clear_second_line_section()
            self.actualOperation = "ADD"
            self.epd.text("+", 180, 120, 0x00)
            self.epd.display_Partial(self.epd.buffer)

        # Resta puntos al jugador actual si oprime la tecla B
        if(key == "B"):
            self.epd.clear_second_line_section()
            self.actualOperation = "SUB"
            self.epd.text("-", 180, 120, 0x00)
            self.epd.display_Partial(self.epd.buffer)


        if key in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
            # permitir ingresar varios numeros seguidos
            self.actualNumberString = self.actualNumberString + key
            self.epd.text(key, 231 + (len(self.actualNumberString) * 7), 120, 0x00)
            self.epd.display_Partial(self.epd.buffer)
        
        # Al apretar tecla D, convierte actualNumberString en un numero y lo suma o resta al jugador actual
        if(key == "D"):
            if(self.actualOperation == "ADD"):
                self.actualNumber = int(self.actualNumberString)
                self.actualNumberString = ""
                if(self.selectedPlayer == 1):
                    self.lifePointsPlayer1 = self.lifePointsPlayer1 + self.actualNumber
                    self.lifePointPlayer1Array.append(self.lifePointsPlayer1)
                else:
                    self.lifePointsPlayer2 = self.lifePointsPlayer2 + self.actualNumber
                    self.lifePointPlayer2Array.append(self.lifePointsPlayer2)
            else:
                self.actualNumber = int(self.actualNumberString)
                self.actualNumberString = ""
                if(self.selectedPlayer == 1):
                    self.lifePointsPlayer1 = self.lifePointsPlayer1 - self.actualNumber
                    self.lifePointPlayer1Array.append(self.lifePointsPlayer1)
                else:
                    self.lifePointsPlayer2 = self.lifePointsPlayer2 - self.actualNumber
                    self.lifePointPlayer2Array.append(self.lifePointsPlayer2)

            self.epd.clear_third_line_section()
            self.updateBoard()

            # Reviso si alguno perdio y muestro un mensaje en pantalla
            if(self.lifePointsPlayer1 <= 0):
                self.epd.clear_first_line_section()
                self.epd.clear_second_line_section()
                self.epd.clear_third_line_section()
                self.epd.text("GANO " + self.player2 + " ★★$$$$$★★", 0, 120, 0x00)
                self.epd.display_Partial(self.epd.buffer)
                self.enableReset = True
                self.enableTurnOff = True
            elif(self.lifePointsPlayer2 <= 0):
                self.epd.clear_first_line_section()
                self.epd.clear_second_line_section()
                self.epd.clear_third_line_section()
                self.epd.text("GANO " + self.player1 + " ★★$$$$$★★", 0, 120, 0x00)
                self.epd.display_Partial(self.epd.buffer)
                self.enableReset = True
                self.enableTurnOff = True

        if(key == "C"):
            if(self.enableReset == True):
                self.enableReset = False
                self.resetGame()

        if(key == "#"):
            if(self.enableTurnOff == True):
                self.enableTurnOff = False
                self.epd.fill(1)
                self.epd.Clear(0xff)
                self.epd.fill(0)
                self.epd.Clear(0xff)
                self.epd.sleep()

        if(key != "#" or (key == "#" and self.enableTurnOff == False)):
            self.waitNextAction()

    def resetGame(self):
        self.selectedPlayer = 1
        self.lifePointsPlayer1 = 8000
        self.lifePointsPlayer2 = 8000
        self.lifePointPlayer1Array = [8000]
        self.lifePointPlayer2Array = [8000]
        self.actualOperation = "ADD"
        self.actualNumberString = ""
        self.epd.Clear(0xff)
        self.selectPlayers()
        self.drawBoard()
        self.setPlayer(1)
        self.waitNextAction()

    def updateBoard(self):
        # para el jugador 1, 
        if(self.selectedPlayer == 1):
            # por cada elemento en lifePointPlayer1Array, lo muestra en pantalla uno abajo de otro, comenzando desde la posicion 25
            for i in range(len(self.lifePointPlayer1Array)):
                # por cada elemento en lifePointPlayer1Array, lo muestra en pantalla uno abajo de otro, comenzando desde la posicion 25
                if(i <= 8):
                    self.epd.text(str(self.lifePointPlayer1Array[i]), 0, 24 + (i * 10), 0x00)
                elif(i > 8 and i <= 17):
                    self.epd.text(str(self.lifePointPlayer1Array[i]), 35, 24 + ( (i - 9) * 10), 0x00)
                elif(i > 17 and i <= 26):
                    self.epd.text(str(self.lifePointPlayer1Array[i]), 70, 24 + ((i - 18) * 10), 0x00)
                else:
                    self.epd.text(str(self.lifePointPlayer1Array[i]), 105, 24 + ((i - 27) * 10), 0x00)

                self.epd.display_Partial(self.epd.buffer)

        # hago lo mismo para el jugador 2
        else:
            for i in range(len(self.lifePointPlayer2Array)):
                if(i <= 8):
                    self.epd.text(str(self.lifePointPlayer2Array[i]), 155, 24 + (i * 10), 0x00)
                elif(i > 8 and i <= 17):
                    self.epd.text(str(self.lifePointPlayer2Array[i]), 190, 24 + ( (i - 9) * 10), 0x00)
                elif(i > 17 and i <= 26):
                    self.epd.text(str(self.lifePointPlayer2Array[i]), 225, 24 + ((i - 18) * 10), 0x00)
                else:
                    self.epd.text(str(self.lifePointPlayer2Array[i]), 260, 24 + ((i - 27) * 10), 0x00)

                self.epd.display_Partial(self.epd.buffer)
        
    
    def setPlayer(self, player):
        self.selectedPlayer = player
        self.epd.clear_first_line_section()
        if(player == 1):
            self.epd.text("JUGADOR: " + self.player1, 0, 120, 0x00)
            self.epd.display_Partial(self.epd.buffer)
        else:
            self.epd.text("JUGADOR: " + self.player2, 0, 120, 0x00)
            self.epd.display_Partial(self.epd.buffer)


if __name__=='__main__':

    game = Game()
    game.start()
    game.selectPlayers()
    game.drawBoard()
    game.setPlayer(2)
    game.updateBoard()
    game.setPlayer(1)
    game.updateBoard()
    game.waitNextAction()
