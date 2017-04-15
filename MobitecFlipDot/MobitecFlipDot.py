'''
    Mobitec Flip Dot
    Biblioteka funkcji sluzacych do sterowania wyswietlaczami klapkowymi (flip dot) firmy Mobitec.
    Wyswietlacze klapkowe sa wyposazone w jednokierunkowy interfejs RS485, pracujacy z predkoscia 4800 kbps.
    Do komunikacji z wyswietlaczami firmy Mobitec niezbedny jest adapter RS232 - RS485.
    Biblioteka obejmuje nastepujace funkcje:
    - czyszczenie marycy wyswietlacza
    - wyswietlanie tekstu (okreslony font i pozycja)
    - rysowanie pojedynczych pikseli
    - wyswietlanie monochromatycznych map bitowych (pliki *.bmp)

    Interfejs rozwiazania:
    obiekt = MobitecFlipDot('PORT COM', 'adres hex') - definicja obiektu wyswietlacza
    obiekt.clearScreen() - czyszczenie wyswietlacza
    obiekt.writeText([[font, X, Y, 'Tekst1'], [font, X, Y, 'Tekst2']]) - wyswietlanie napisow
    obiekt.showPixel([[X, Y], [X, Y], [X, Y]]) - wlaczanie pikseli o podanych wspolrzednych
    obiekt.showBMP('plik.bmp')- wyswietlanie monochromatycznej bitmapy (rozmiar dostosowany do wyswietlacza)
    obiekt.showMixed(X, Y, 'plik.bmp', [[font, X, Y, 'Tekst1'], [font, X, Y, 'Tekst2']]) - wyswietlanie tresci mieszanej
'''

__author__ = 'Tomasz'

import serial
from PIL import Image


# Klasa sterujaca wyswietlaczem
class MobitecFlipDot():
    mobitecFont = ('0x61', '0x62', '0x63', '0x64', '0x65', '0x66', '0x67', '0x68', '0x69', '0x6A', '0x6B',
                   '0x6C', '0x6D', '0x6E', '0x6F', '0x71', '0x72', '0x73', '0x74', '0x76', '0x78', '0x79')

    # Konstruktor klasy (numer portu - str, adres wyswietlacza - Hex)
    def __init__(self, port, adres):
        self.displayAddress = adres
        self.serialPort = serial.Serial(port, 4800,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE,
                                        bytesize=serial.EIGHTBITS)

    # Metoda wysylajaca dane do wyswietlacza
    def sendData(self, data):
        for byte in data:
            self.serialPort.write(chr(int(byte, 16)))

    # Metoda do obliczania sumy kontrolnej ciagu danych
    def controlCheckValue(self, data):
        check = 0
        for br in data:
            check = (check + int(br, 16)) % 256
        return check

    # Metoda czyszczaca matryce wyswietlacza
    def clearScreen(self):

        cleanOrder = ['0xA2', '0xD2', '0x00', '0xD3', '0x00', '0xD4', '0x00', '0x20']

        cleanOrder.insert(0, self.displayAddress)
        crcSum = self.controlCheckValue(cleanOrder)
        if crcSum >= 254:
            cleanOrder.append('0xFE')
            cleanOrder.append(hex(crcSum + 2))
        else:
            cleanOrder.append(hex(crcSum))

        # Znaczniki poczatku i konca ramki
        cleanOrder.insert(0, '0xFF')
        cleanOrder.append('0xFF')

        # Wyslanie ramki rozkazu do wyswietlacza
        self.sendData(cleanOrder)

        return cleanOrder

    # Metoda wyswietlajaca podane teksty, z wybranym fontem, w podanych miejscach wyswietlacza
    def writeText(self, data):
        # Zmienna do budowy ramki wyswietlajacej napisy
        writeOrder = []

        # Budowanie podstawowej struktury ramki (adres wyswietlacza)
        # i wprowadzenie zestawu tekstow (czcionka, pozycja tekstu, tekst)
        writeOrder.append(self.displayAddress)
        writeOrder.append('0xA2')

        for set in data:
            writeOrder.append('0xD2')
            writeOrder.append(str(hex(set[1])))
            writeOrder.append('0xD3')
            writeOrder.append(str(hex(set[2])))
            writeOrder.append('0xD4')

            # Ustawienie jednej z czcionek (wybor ze zbioru dostepnych)
            if set[0] >= 0 and set[0] <= 21:
                self.font = self.mobitecFont[set[0]]
            else:
                self.font = self.mobitecFont[0]

            writeOrder.append(self.font)

            # Przetwarzanie podanego tekstu z zestawu na Hex
            for sign in set[3]:
                writeOrder.append(hex(ord(sign)))

        # Wyliczenie sumy kontrolnej ramki
        crcSum = self.controlCheckValue(writeOrder)
        if crcSum >= 254:
            writeOrder.append('0xFE')
            writeOrder.append(hex(crcSum + 2))
        else:
            writeOrder.append(hex(crcSum))

        # Znaczniki poczatku i konca ramki
        writeOrder.insert(0, '0xFF')
        writeOrder.append('0xFF')

        # Wyslanie ramki rozkazu do wyswietlacza
        self.sendData(writeOrder)

        return writeOrder

    # Metoda buduje ramke i wysyla rozkaz z podanymi obrazami pikselowymi
    def showPixel(self, map):
        # Zmienna do budowy ramki wyswietlajacej obrazy pikselowe
        pixelOrder = []

        # Budowanie podstawowej struktury ramki (adres wyswietlacza)
        # i wprowadzenie mapy symboli
        pixelOrder.append(self.displayAddress)
        pixelOrder.append('0xA2')

        # Rysowanie pikseli wedlug podanej mapy
        for piksel in map:
            pixelOrder.append('0xD2')
            pixelOrder.append(str(hex(piksel[0])))
            pixelOrder.append('0xD3')
            pixelOrder.append(str(hex(piksel[1] + 4)))
            pixelOrder.append('0xD4')
            pixelOrder.append('0x77')
            pixelOrder.append('0x21')

        # Wyliczenie sumy kontrolnej ramki
        crcSum = self.controlCheckValue(pixelOrder)
        if crcSum >= 254:
            pixelOrder.append('0xFE')
            pixelOrder.append(hex(crcSum + 2))
        else:
            pixelOrder.append(hex(crcSum))

        # Znaczniki poczatku i konca ramki
        pixelOrder.insert(0, '0xFF')
        pixelOrder.append('0xFF')

        # Wyslanie ramki rozkazu do wyswietlacza
        self.sendData(pixelOrder)

        return pixelOrder

    # Metoda przenosi obraz bimapy na ekran
    def showBMP(self, bitmap):
        # Mapa bitowa obrazu
        pictureMap = []
        bmp = Image.open(bitmap)
        picture = bmp.convert('RGB')

        for x in range(picture.size[0]):
            for y in range(picture.size[1]):
                if picture.getpixel((x, y)) == (0, 0, 0):
                    pictureMap.append([x, y])

        self.showPixel(pictureMap)

    # Metoda wyswietla tresc mieszana: BMP + tekst
    def showMixed(self, xR, yR, file, texts):
        # Zmienna do budowy ramki o mieszanej tresci (tekst + napisy)
        mixedOrder = []

        # Budowanie podstawowej struktury ramki (adres wyswietlacza)
        # i wprowadzenie zestawu tekstow (czcionka, pozycja tekstu, tekst)
        mixedOrder.append(self.displayAddress)
        mixedOrder.append('0xA2')

        bmp = Image.open(file)
        obrazek = bmp.convert('RGB')

        for set in texts:
            mixedOrder.append('0xD2')
            mixedOrder.append(str(hex(set[1])))
            mixedOrder.append('0xD3')
            mixedOrder.append(str(hex(set[2])))
            mixedOrder.append('0xD4')

            # Ustawienie jednej z czcionek (wybor ze zbioru dostepnych)
            if set[0] >= 0 and set[0] <= 21:
                self.tekstCzcionka = self.mobitecFont[set[0]]
            else:
                self.tekstCzcionka = self.mobitecFont[0]

            mixedOrder.append(self.tekstCzcionka)

            # Przetwarzanie podanego tekstu z zestawu na Hex
            for litera in set[3]:
                mixedOrder.append(hex(ord(litera)))

        for x in range(obrazek.size[0]):
            for y in range(obrazek.size[1]):
                if obrazek.getpixel((x, y)) == (0, 0, 0):
                    # Dodanie piksela do ramki
                    mixedOrder.append('0xD2')
                    mixedOrder.append(str(hex(x + xR)))
                    mixedOrder.append('0xD3')
                    mixedOrder.append(str(hex(y + yR + 4)))
                    mixedOrder.append('0xD4')
                    mixedOrder.append('0x77')
                    mixedOrder.append('0x21')

        # Wyliczenie sumy kontrolnej ramki
        sumaCRC = self.controlCheckValue(mixedOrder)
        if sumaCRC >= 254:
            mixedOrder.append('0xFE')
            mixedOrder.append(hex(sumaCRC + 2))
        else:
            mixedOrder.append(hex(sumaCRC))

        # Znaczniki poczatku i konca ramki
        mixedOrder.insert(0, '0xFF')
        mixedOrder.append('0xFF')

        # Wyslanie ramki rozkazu do wyswietlacza
        self.sendData(mixedOrder)

        return mixedOrder
