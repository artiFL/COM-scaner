import sys, glob, time, serial, os, struct, subprocess, threading, struct

std_speeds = ['115200', '57600', '38400', '19200', '9600', '4800', '2400', '1200', '600', '300', '150', '100', '75', '50']
paritys = ['N', 'E', 'O']   #Бит четности
stopbitss = [1, 2]          #Количество стоп-бит
bite_size = 8               #Биты данных
t_out = 1                   #Таймаут в секундах, должен быть больше 1с
flag1=0                     #Флаг для остановки программы, устанавливается в 1, если найдена сигнатура  
reading_bytes = 1           #Количество байт для чтения после открытия порта

SIGNATURE_TO_CONNECTION         = b'\x5e'       #'^'
SIGNATURE_END_SERCH             = b'\x5f'       #'_'
SIGNATURE_CONFIRM_CONNECTION    = b'\x7e'       #'~'

SIGNATURE_PORT_CLOSE  			= b'\x7C'		#'|'

SIGMATURE_START_SEND_ARRAY		= b'\x1D'		#'{' PC -> UART
SIGNATURE_END_SEND_ARRAY		= b'\x7D' 		#'}'

SIGNATURE_START_RECIVE_ARRAY	= b'\x5B'		#'[' UART -> PC
SIGNATURE_END_RECIVE_ARRAY		= b'\x5D'		#']'


recive_buffer = []

ser = serial.Serial()

################# Поиск доступных портов windows, linux,
def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
##################################

print('Сигнатура для поиска:', end = '')
print(SIGNATURE_TO_CONNECTION)

ports=serial_ports()
if ports:
        print('Доступные порты:')
        print(ports)
        if len(ports)>1:
            #ser.port = 'COM8'                       #############################    раскоментировать
            ser.port = input('Введите адрес COM порта ')
        else:
            ser.port = ports[0]
            print ('Работаем с портом '+ser.port)
else:
    print('\nНет доступных COM портов, проверьте подключние.\n')
    sys.exit()

try: 
    for stop_bit in stopbitss:
        for parit in paritys:
            for com_speed in std_speeds:
                ser.close()
                ser.baudrate = com_speed
                ser.timeout = t_out
                ser.bytesize = bite_size
                ser.parity = parit
                ser.stopbits = stop_bit
                ser.open()
                #ser.write(cmd)                                       #!Раскомментировать при необходимости отправки команды в устройство для инициализации связи                    
                message_b = ser.read(reading_bytes)
                if flag1==1:
                    break
                if message_b:
                    print ('\nRAW data on '+ser.port+', '+com_speed+', '+str(ser.bytesize)+', '+ser.parity+', '+str(ser.stopbits)+':')
                    print ('---------------------')
                    print (message_b)
                    print ('---------------------')
                    try:
                        if SIGNATURE_TO_CONNECTION in message_b:
                            print ('\n\033[0;33mСигнатура ', end = '') #желтый цвет текста
                            print(SIGNATURE_TO_CONNECTION, end = '')
                            print(' найдена при следующих настройках: \n'+ser.port+', '+com_speed+', '+str(ser.bytesize)+', '+ser.parity+', '+str(ser.stopbits))
                            print('\x1b[0m')
                            ser.close()
                            port = ser.port
                            baudrate  = com_speed
                            bytesize = ser.bytesize
                            parity = ser.parity
                            stopbits = ser.stopbits
                            flag1=1
                            break
                        else:
                            ser.close()
                    except:
                        print ('error decode')
                        print ('---------------------')
                        ser.close()
                else:
                    print('timeout on '+ser.port+', '+com_speed+', '+str(ser.bytesize)+', '+ser.parity+', '+str(ser.stopbits))
                    print ('---------------------')
                    ser.close()
    if flag1 == 0:
        print('Поиск завершен, сигнатура не найдена')
except serial.SerialException:                                
    print ('Ошибка при открытии порта '+ser.port)
    sys.exit()

def connect_to_serial():

    while (ser.read() != SIGNATURE_CONFIRM_CONNECTION):
        ser.write(SIGNATURE_END_SERCH)

def read_array ():
    buf = 0
    while (ser.read() != SIGNATURE_END_RECIVE_ARRAY):
        buf = ser.read(30)
        recive_buffer.append(buf)


def main():   

    connect_to_serial()

    if ser.read() != 0:

        while(ser.read() != SIGNATURE_PORT_CLOSE):
            print(ser.read())

            if ser.read() == SIGNATURE_START_RECIVE_ARRAY:
                read_array()
                print(recive_buffer)

        ser.close()

    else:
        print("serial is empty") 


















































if __name__ == '__main__':
    main()
















