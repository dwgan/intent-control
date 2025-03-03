import serial

def send_command(serial_port, data):
    # 初始化协议帧（每次调用都重置为初始值）
    cmd = b'\x7E\x01\x01\x01\x7F'
    cmd_array = bytearray(cmd)  # 转换为可修改的字节数组

    # 根据意图修改协议帧
    if data['intent'] == 'LAUNCH':  # 注意拼写是否正确（原代码中是 'LAUCH'？）
        cmd_array[3] = 0x01
    # 根据槽位修改协议帧
    if 'name' in data['slots'] and data['slots']['name'][0] == '灯':  # 确保槽位存在且值正确
        cmd_array[2] = 0x03

    # 发送修改后的字节数组
    serial_port.write(cmd_array)  # 必须发送 cmd_array 而非原 cmd
