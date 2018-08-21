import winsound
# # import time
# #
# # duration = 10  # millisecond
# # freq = 4000  # Hz
# #
# # def beeper():
# #     for i in range(4):
# #         winsound.Beep(freq, duration)
# #
# # for i in range(10):
# #     time.sleep(1)
# #     beeper()

def annoy():
     for i in range(1, 10):
         winsound.Beep(i * 100, 200)

def sos():
    for i in range(0, 3): winsound.Beep(2000, 100)
    for i in range(0, 3): winsound.Beep(2000, 400)
    for i in range(0, 3): winsound.Beep(2000, 100)

sos()
