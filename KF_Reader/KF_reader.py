# coding=windows-1250
__author__ = 'tszreniawa@gmail.com'

"""
Program literujący znaki wywoławcze krótkofalowców w systemie:
- łączności krajowych,
- łączności międzynarodowych.
"""

class KFReader:
    local = {'A': 'Adam', 'B': 'Barbara', 'C': 'Celina (Cezary)', 'D': 'Dorota', 'E': 'Ewa', 'F': 'Franciszek',
             'G': 'Grażyna', 'H': 'Halina', 'I': 'Irena', 'J': 'Jadwiga', 'K': 'Karol', 'L': 'Ludwik', 'M': 'Maria',
             'N': 'Natalia', 'O': 'Olga', 'P': 'Paweł', 'Q': 'Kłebek (Queen', 'R': 'Roman', 'S': 'Stefan',
             'T': 'Tadeusz', 'U': 'Urszula', 'V': 'Violetta', 'W': 'Wanda', 'X': 'Xawery (Ksantypa)',
             'Y': 'Yokohama (Ypsilon)', 'Z': 'Zygmunt', '1': 'Jeden (1)', '2': 'Dwa (2)', '3': 'Trzy (3)',
             '4': 'Cztery (4)', '5': 'Pięć (5)', '6': 'Sześć (6)', '7': 'Siedem (7)', '8': 'Osiem (8)',
             '9': 'Dziewięć (9)', '0': 'Zero (0)'}

    dx = {'A': 'Alfa', 'B': 'Bravo', 'C': 'Charlie', 'D': 'Delta', 'E': 'Echo', 'F': 'Foxtrot',
          'G': 'Golf', 'H': 'Hotel', 'I': 'India', 'J': 'Juliett', 'K': 'Kilo', 'L': 'Lima', 'M': 'Mike',
          'N': 'November', 'O': 'Oscar', 'P': 'Papa', 'Q': 'Quebec', 'R': 'Romeo', 'S': 'Sierra', 'T': 'Tango',
          'U': 'Uniform', 'V': 'Victor', 'W': 'Whiskey', 'X': 'X-Ray', 'Y': 'Yankee', 'Z': 'Zulu', '1': 'One (1)',
          '2': 'Two (2)', '3': 'Three (3)', '4': 'Four (4)', '5': 'Five (5)', '6': 'Six (6)', '7': 'Seven (7)',
          '8': 'Eight (8)', '9': 'Nine (9)', '0': 'Zero (0)'}

    def __init__(self, sign):
        self.sign = sign

    def decrypt(self, mode):
        if mode != 'local' and mode != 'dx':
            return 'Zły parametr!'
        else:
            output = ''
            for character in self.sign:
                output = output + getattr(self, mode)[character.upper()] + '\n'
            return output

obiekt = KFReader('SR9WX')
print obiekt.decrypt('local')
print obiekt.decrypt('dx')